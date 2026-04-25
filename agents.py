import requests
import json
import logging
from typing import Optional

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "gemma3:1b"
logger = logging.getLogger(__name__)


def call_ollama(prompt: str, max_tokens: int = 300) -> str:
    try:
        res = requests.post(OLLAMA_URL, json={
            "model": MODEL,
            "prompt": prompt,
            "stream": False,
            "format": "json",
            "options": {"temperature": 0.1, "num_predict": max_tokens}
        }, timeout=5)
        res.raise_for_status()
        payload = res.json()
        if not isinstance(payload, dict):
            logger.warning("Ollama response is not JSON object")
            return ""
        return payload.get("response", "")
    except (requests.RequestException, ValueError) as exc:
        logger.warning("Ollama request failed: %s", exc)
        return ""


def parse_json(raw: str) -> Optional[dict]:
    try:
        cleaned = raw.strip().replace("```json", "").replace("```", "").strip()
        return json.loads(cleaned)
    except (AttributeError, json.JSONDecodeError):
        return None


# ── Rule-based fallbacks ──────────────────────────────────────────────────────

def profiler_fallback(tick: dict) -> dict:
    hr = tick.get("heart_rate", 75)
    activity = tick.get("accelerometer", {}).get("activity", "unknown")
    steps = tick.get("accelerometer", {}).get("steps_per_min", 0)
    gps = tick.get("gps", {}).get("context", "familiar_zone")
    app = tick.get("active_app", "")
    battery = tick.get("battery_pct", 50)
    hrv = tick.get("hrv", 45)
    spo2 = tick.get("spo2", 98)

    # Determine state
    if activity == "stationary" and hr < 62:
        state = "sleeping"
    elif activity == "running":
        state = "exercising"
    elif activity in ["transit", "walking"] and gps == "unfamiliar_zone":
        state = "navigating"
    elif hr > 95 and hrv < 35:
        state = "stressed"
    elif hr < 65 and activity in ["stationary", "sedentary"] and not tick.get("screen_on", True):
        state = "resting"
    elif activity in ["transit", "walking"]:
        state = "commuting"
    elif app in ["Headspace", "Calm", "Meditation", "Insight Timer"]:
        state = "meditating"
    else:
        state = "working"

    stress = max(1, min(10, round((100 - hrv) / 10 + (hr - 60) / 20)))
    activity_level = {"stationary": 1, "sedentary": 1, "transit": 3, "walking": 5, "running": 9}.get(activity, 3)
    vulnerability = _compute_vulnerability(state, battery, gps, hr, hrv)

    flags = []
    if hr > 130 and activity in ["sedentary", "stationary"]:
        flags.append("HR_SPIKE")
    if hr > 130:
        flags.append("ELEVATED_HR")
    if hrv < 25:
        flags.append("LOW_HRV")
    if battery < 10:
        flags.append("CRITICAL_BATTERY")
    if gps == "unfamiliar_zone":
        flags.append("UNFAMILIAR_LOCATION")
    if activity in ["stationary", "sedentary"] and hr > 130:
        flags.append("STILL_BODY")
    if spo2 < 95:
        flags.append("LOW_SPO2")

    summaries = {
        "sleeping": f"User in deep sleep, HR {hr} BPM, vitals stable and calm",
        "exercising": f"User running at {hr} BPM, high physical activity detected",
        "navigating": f"User navigating unfamiliar area with {battery}% battery remaining",
        "stressed": f"Elevated stress detected — HR {hr} BPM, HRV {hrv}ms, vulnerability high",
        "resting": f"User at rest, calm vitals — HR {hr} BPM, HRV {hrv}ms",
        "commuting": f"User commuting on familiar route, moderate vitals — HR {hr}",
        "meditating": f"User in deep focus / meditation session, HR {hr} BPM, calm state",
        "working": f"User at desk working, HR {hr} BPM, normal office activity",
    }

    return {
        "state": state,
        "stress_level": stress,
        "activity_level": activity_level,
        "vulnerability_score": vulnerability,
        "flags": flags,
        "summary": summaries.get(state, f"User is {state}, HR {hr}"),
        "gps_familiarity": "familiar" if gps == "familiar_zone" else "unfamiliar",
        "source": "rule_engine"
    }


def action_fallback(profiler_state: dict, tick: dict) -> dict:
    hr = tick.get("heart_rate", 75)
    battery = tick.get("battery_pct", 50)
    hrv = tick.get("hrv", 45)
    state = profiler_state.get("state", "working")
    activity = tick.get("accelerometer", {}).get("activity", "sedentary")
    gps = profiler_state.get("gps_familiarity", "familiar")
    flags = profiler_state.get("flags", [])
    vulnerability = profiler_state.get("vulnerability_score", 3)

    # Emergency: high HR while completely still — not exercising
    if hr > 130 and activity in ["sedentary", "stationary"] and state != "sleeping" and state != "exercising":
        return {
            "action": "alert",
            "severity": 5,
            "urgency": 10,
            "reason": f"HR {hr} BPM with zero movement — possible cardiac event",
            "protocol": "emergency",
            "proposed_actions": ["notify_emergency_contacts", "share_gps", "call_sos"],
            "override_candidate": False
        }

    # Smart suppress: low battery + navigating unfamiliar area
    if battery < 10 and gps == "unfamiliar" and state in ["navigating", "commuting"]:
        return {
            "action": "suppress",
            "severity": 2,
            "urgency": 4,
            "reason": f"Battery at {battery}% but user navigating unfamiliar zone — map access critical",
            "protocol": "navigation",
            "proposed_actions": ["defer_battery_alert"],
            "override_candidate": True
        }

    # Workout suppress: high HR is contextually normal
    if state == "exercising" and hr > 130:
        return {
            "action": "suppress",
            "severity": 1,
            "urgency": 1,
            "reason": f"HR {hr} BPM normal for active running session — expected physiology",
            "protocol": "wellness",
            "proposed_actions": ["log_workout_data"],
            "override_candidate": False
        }

    # Sleep: silence everything non-critical
    if state == "sleeping":
        return {
            "action": "log",
            "severity": 1,
            "urgency": 1,
            "reason": "User in deep sleep — suppressing all non-critical notifications",
            "protocol": "sleep",
            "proposed_actions": ["silent_log"],
            "override_candidate": False
        }

    # Meditation / deep focus: defer non-emergency alerts
    if state == "meditating":
        if battery < 20:
            return {
                "action": "suppress",
                "severity": 3,
                "urgency": 5,
                "reason": f"Battery {battery}% low but user is meditating — defer to after session",
                "protocol": "defer",
                "proposed_actions": ["defer_battery_alert_20min"],
                "override_candidate": True
            }

    # Stress watch
    if profiler_state.get("stress_level", 1) > 7:
        return {
            "action": "log",
            "severity": 3,
            "urgency": 5,
            "reason": f"Stress markers elevated — HRV {hrv}ms, HR {hr} BPM, monitoring",
            "protocol": "stress",
            "proposed_actions": ["log_stress_event", "suggest_breathing"],
            "override_candidate": False
        }

    # Critical battery while awake
    if battery < 5 and state not in ["sleeping"]:
        return {
            "action": "alert",
            "severity": 4,
            "urgency": 8,
            "reason": f"Battery critically low at {battery}% — immediate charge required",
            "protocol": "battery",
            "proposed_actions": ["notify_battery_critical"],
            "override_candidate": True
        }

    return {
        "action": "log",
        "severity": 1,
        "urgency": 1,
        "reason": "Vitals nominal, all systems normal — no action required",
        "protocol": "normal",
        "proposed_actions": ["routine_log"],
        "override_candidate": False
    }


def arbiter_fallback(profiler_state: dict, action_state: dict, tick: dict) -> dict:
    """Arbiter wisdom: second-guesses the action agent with real-world context."""
    state = profiler_state.get("state", "working")
    action = action_state.get("action", "log")
    protocol = action_state.get("protocol", "normal")
    urgency = action_state.get("urgency", 1)
    battery = tick.get("battery_pct", 50)
    hr = tick.get("heart_rate", 75)
    flags = profiler_state.get("flags", [])
    gps = profiler_state.get("gps_familiarity", "familiar")
    override_candidate = action_state.get("override_candidate", False)

    # NEVER override a real emergency (multiple critical signals)
    if protocol == "emergency" and "HR_SPIKE" in flags and "STILL_BODY" in flags:
        return {
            "final_decision": action,
            "final_protocol": protocol,
            "overridden": False,
            "override_reason": None,
            "arbiter_reasoning": (
                f"AGREED with Action Agent. Multiple critical signals align: HR {hr} BPM + "
                f"zero movement + {gps} location = real potential emergency. "
                "Safety is non-negotiable. No override."
            ),
            "wisdom_applied": "safety_first",
            "defer_minutes": None,
            "source": "rule_engine"
        }

    # Sacred moment: sleeping — defer battery/non-critical alerts
    if state == "sleeping" and action == "alert" and protocol != "emergency":
        return {
            "final_decision": "defer",
            "final_protocol": "sleep_defer",
            "overridden": True,
            "override_reason": "User is sleeping. Non-emergency alerts deferred until wake-up.",
            "arbiter_reasoning": (
                "OVERRIDING Action Agent. Sleep is precious and restorative. "
                f"Battery at {battery}% will not cause immediate harm. "
                "Humans always charge when awake. Interrupting sleep causes real harm."
            ),
            "wisdom_applied": "respect_sleep",
            "defer_minutes": 30,
            "source": "rule_engine"
        }

    # Sacred moment: meditating — defer non-critical
    if state == "meditating" and action in ["alert", "suppress"] and protocol not in ["emergency"]:
        return {
            "final_decision": "defer",
            "final_protocol": "meditation_defer",
            "overridden": True,
            "override_reason": "User is in meditation/deep focus. Alert deferred for 20 minutes.",
            "arbiter_reasoning": (
                "OVERRIDING Action Agent. Meditation is a sacred mental health moment. "
                f"Battery at {battery}% is low but not life-threatening. "
                "User is at a fixed location — not driving or navigating. "
                "Interrupting now would cause real psychological harm."
            ),
            "wisdom_applied": "respect_focus",
            "defer_minutes": 20,
            "source": "rule_engine"
        }

    # Workout context: high HR during running is normal, don't alert
    if state == "exercising" and action == "alert" and "HR_SPIKE" in flags:
        return {
            "final_decision": "suppress",
            "final_protocol": "wellness",
            "overridden": True,
            "override_reason": "Elevated HR is physiologically expected during exercise.",
            "arbiter_reasoning": (
                "OVERRIDING Action Agent. User is actively running — elevated HR is intentional. "
                "Alerting would break their focus and cause unnecessary panic."
            ),
            "wisdom_applied": "exercise_context",
            "defer_minutes": None,
            "source": "rule_engine"
        }

    # Navigation context: critical battery but user needs the map
    if gps == "unfamiliar" and battery < 10 and action == "alert" and protocol == "battery":
        return {
            "final_decision": "defer",
            "final_protocol": "navigation_priority",
            "overridden": True,
            "override_reason": "User navigating unfamiliar area — map access prioritized over battery alert.",
            "arbiter_reasoning": (
                "OVERRIDING Action Agent. User is in an unfamiliar zone with active navigation. "
                "A battery alert now could cause them to look away from maps and get lost. "
                "Defer until they reach a familiar area or stop moving."
            ),
            "wisdom_applied": "navigation_safety",
            "defer_minutes": 15,
            "source": "rule_engine"
        }

    # Default: agree with Action Agent
    return {
        "final_decision": action,
        "final_protocol": protocol,
        "overridden": False,
        "override_reason": None,
        "arbiter_reasoning": (
            f"AGREED with Action Agent. Context analysis supports the {action.upper()} decision. "
            "No wisdom-based override required."
        ),
        "wisdom_applied": "agreement",
        "defer_minutes": None,
        "source": "rule_engine"
    }


def _compute_vulnerability(state: str, battery: int, gps: str, hr: int, hrv: int) -> int:
    score = 3
    if state in ["navigating", "commuting"] and gps == "unfamiliar_zone":
        score += 2
    if battery < 15:
        score += 2
    if hr > 130:
        score += 2
    if hrv < 30:
        score += 1
    if state == "sleeping":
        score = 1
    return min(10, score)


# ── Main agent functions ──────────────────────────────────────────────────────

def run_profiler(telemetry_history: list) -> dict:
    """
    Profiler Agent — The Observer.
    Watches sensor data and builds a rich, rolling picture of who the user is
    and what they're doing right now. Uses last 3 ticks for temporal context.
    """
    if not telemetry_history:
        return {}

    recent = telemetry_history[-3:]
    tick = telemetry_history[-1]
    hr = tick.get("heart_rate", 75)
    hrv = tick.get("hrv", 45)
    activity = tick.get("accelerometer", {}).get("activity", "unknown")
    battery = tick.get("battery_pct", 50)
    gps_context = tick.get("gps", {}).get("context", "familiar_zone")
    app = tick.get("active_app", "unknown")
    spo2 = tick.get("spo2", 98)

    prompt = f"""You are a smartwatch profiler agent — "The Observer". Your job is to analyze biometric and sensor telemetry and build a rich contextual picture of the user's current state.

You have access to the last {len(recent)} sensor readings. Use trends, not just the latest value.

Recent sensor history:
{json.dumps(recent, indent=2)}

Key signals to interpret:
- Heart Rate: {hr} BPM (elevated >100, critical >130 if sedentary)
- HRV: {hrv}ms (low HRV <30 = stress, high HRV >60 = calm/sleep)
- SpO2: {spo2}% (below 95 is concerning)
- Activity: {activity} (stationary/sedentary/walking/running/transit)
- GPS context: {gps_context}
- Active App: {app}
- Battery: {battery}%

Known user state categories:
- sleeping: HR<62, stationary, no screen, HRV high
- resting: calm HR, minimal movement, at home
- exercising: running or walking fast, elevated HR is EXPECTED
- meditating: calm/meditation app open, low HR, minimal movement
- working: at office/familiar location, moderate HR
- commuting: transit or walking on familiar route
- navigating: walking/transit in unfamiliar zone
- stressed: elevated HR + low HRV without exercise context

Identify any red flags (HR_SPIKE, LOW_HRV, CRITICAL_BATTERY, UNFAMILIAR_LOCATION, STILL_BODY, LOW_SPO2).
Compute a vulnerability score 1-10 (how much the user needs protection right now).

Return ONLY this exact JSON, nothing else:
{{
  "state": "<sleeping|resting|exercising|meditating|working|commuting|navigating|stressed>",
  "stress_level": <1-10>,
  "activity_level": <1-10>,
  "vulnerability_score": <1-10>,
  "flags": ["<flag1>", "<flag2>"],
  "summary": "<describe user state in 15 words max>",
  "gps_familiarity": "<familiar|unfamiliar>",
  "reasoning": "<1 sentence explaining why you chose this state>"
}}"""

    # raw = call_ollama(prompt, max_tokens=350)
    # result = parse_json(raw)

    # if result and "state" in result:
    #     result["source"] = "gemma3:1b"
    #     # Ensure flags is always a list
    #     if "flags" not in result:
    #         result["flags"] = []
    #     return result

    # Bypass LLM API for smooth streaming
    return profiler_fallback(tick)


def run_action_agent(profiler_state: dict, telemetry_history: list) -> dict:
    """
    Action Agent — The Urgency Expert.
    Gets the profiler's context and decides what to DO about it.
    First instinct, urgency-based. Usually right but sometimes too rigid.
    """
    if not profiler_state or not telemetry_history:
        return {
            "action": "log", "severity": 1, "urgency": 1,
            "reason": "Insufficient data to make decision",
            "protocol": "normal", "proposed_actions": [], "override_candidate": False
        }

    tick = telemetry_history[-1]
    hr = tick.get("heart_rate", 75)
    hrv = tick.get("hrv", 45)
    battery = tick.get("battery_pct", 50)
    spo2 = tick.get("spo2", 98)
    activity = tick.get("accelerometer", {}).get("activity", "unknown")
    steps = tick.get("accelerometer", {}).get("steps_per_min", 0)
    gps_label = tick.get("gps", {}).get("label", "unknown")
    app = tick.get("active_app", "unknown")
    state = profiler_state.get("state", "working")
    flags = profiler_state.get("flags", [])
    vulnerability = profiler_state.get("vulnerability_score", 3)
    stress = profiler_state.get("stress_level", 1)

    prompt = f"""You are a smartwatch action agent — "The Urgency Expert". The Profiler has given you the user's context. Your job is to decide what action to take RIGHT NOW.

Profiler's assessment:
{json.dumps(profiler_state, indent=2)}

Current vital readings:
- Heart Rate: {hr} BPM
- HRV: {hrv}ms
- SpO2: {spo2}%
- Battery: {battery}%
- Activity: {activity} ({steps} steps/min)
- Location: {gps_label}
- Active App: {app}
- Vulnerability Score: {vulnerability}/10
- Active Flags: {flags}

Decision framework (apply with context — DO NOT blindly follow rules):
1. HR > 130 AND activity is sedentary/stationary AND NOT exercising → ALERT severity 5, emergency protocol, urgency 10
2. Battery < 10% AND navigating unfamiliar area → SUPPRESS (user needs the map MORE than the alert), note as override_candidate
3. Running/exercising with elevated HR > 130 → SUPPRESS (physiologically normal), urgency 1
4. User sleeping (state=sleeping) → LOG only, never interrupt with non-emergency
5. Stress level > 7 (high HR + low HRV without exercise) → LOG with stress protocol, urgency 5
6. Battery < 5% AND user is awake and active → ALERT severity 4, urgency 8, note as override_candidate
7. User meditating with low battery → SUPPRESS with defer suggestion, override_candidate: true
8. SpO2 < 95% while sedentary → ALERT severity 4

Available actions: alert, suppress, log, defer
Available protocols: emergency, navigation, wellness, stress, sleep, normal, battery, defer
proposed_actions choices: notify_emergency_contacts, share_gps, call_sos, defer_battery_alert, defer_battery_alert_20min, log_workout_data, silent_log, log_stress_event, suggest_breathing, notify_battery_critical, routine_log

Return ONLY this exact JSON, nothing else:
{{
  "action": "<alert|suppress|log|defer>",
  "severity": <1-5>,
  "urgency": <1-10>,
  "reason": "<explain your decision in 15 words max>",
  "protocol": "<emergency|navigation|wellness|stress|sleep|normal|battery|defer>",
  "proposed_actions": ["<action1>", "<action2>"],
  "override_candidate": <true|false>
}}"""

    # raw = call_ollama(prompt, max_tokens=350)
    # result = parse_json(raw)

    # if result and "action" in result:
    #     result["source"] = "gemma3:1b"
    #     if "proposed_actions" not in result:
    #         result["proposed_actions"] = []
    #     if "override_candidate" not in result:
    #         result["override_candidate"] = False
    #     return result

    # Bypass LLM API for smooth streaming
    fb = action_fallback(profiler_state, tick)
    fb["source"] = "rule_engine"
    return fb


def run_arbiter(profiler_state: dict, action_state: dict, telemetry_history: list) -> dict:
    """
    Arbiter — The Wisdom Keeper.
    Second-guesses the Action Agent. Adds real-world wisdom and human-centered judgment.
    Makes the FINAL call. Can override OR agree with the Action Agent.
    """
    if not profiler_state or not action_state or not telemetry_history:
        return {
            "final_decision": "log",
            "final_protocol": "normal",
            "overridden": False,
            "override_reason": None,
            "arbiter_reasoning": "Insufficient data — deferring to passive logging.",
            "wisdom_applied": "insufficient_data",
            "defer_minutes": None,
            "source": "rule_engine"
        }

    tick = telemetry_history[-1]
    hr = tick.get("heart_rate", 75)
    hrv = tick.get("hrv", 45)
    battery = tick.get("battery_pct", 50)
    state = profiler_state.get("state", "working")
    flags = profiler_state.get("flags", [])
    vulnerability = profiler_state.get("vulnerability_score", 3)
    gps = profiler_state.get("gps_familiarity", "familiar")
    action = action_state.get("action", "log")
    protocol = action_state.get("protocol", "normal")
    urgency = action_state.get("urgency", 1)
    override_candidate = action_state.get("override_candidate", False)
    action_reason = action_state.get("reason", "")

    prompt = f"""You are the Arbiter — "The Wisdom Keeper". You are the final decision-maker for a smartwatch AI system. The Profiler has described the user's situation, and the Action Agent has proposed what to do. Your job is to evaluate that proposal through the lens of human wisdom and make the FINAL call.

You can AGREE with the Action Agent or OVERRIDE them. Overrides require strong justification.

PROFILER'S ASSESSMENT:
{json.dumps(profiler_state, indent=2)}

ACTION AGENT'S PROPOSAL:
{json.dumps(action_state, indent=2)}

CURRENT CONTEXT:
- Heart Rate: {hr} BPM
- Battery: {battery}%
- State: {state}
- GPS familiarity: {gps}
- Active flags: {flags}
- Vulnerability score: {vulnerability}/10

THE GOLDEN RULES OF WISDOM (apply thoughtfully):
1. NEVER override a true emergency (HR spike + still body + unfamiliar location = REAL danger)
2. ALWAYS protect sacred moments (sleep, meditation, prayer) from non-emergency interruptions
3. Smart timing matters — a battery alert while sleeping = worthless; same alert while awake = valuable
4. Context is everything — same HR spike during running is normal; while sitting is an emergency
5. User convenience < User safety. But comfort matters for non-emergencies.
6. When in doubt: DEFER rather than ALERT. Let the moment pass.
7. Only OVERRIDE the Action Agent when you have clear wisdom-based justification

Wisdom categories:
- safety_first: emergency situation, must alert
- respect_sleep: user sleeping, defer non-emergency
- respect_focus: user meditating/in deep work, defer
- exercise_context: high HR is normal during workout
- navigation_safety: user needs map, not notifications
- agreement: action agent is correct, no override needed

Defer options: 15 minutes, 20 minutes, 30 minutes, or until state changes

Return ONLY this exact JSON, nothing else:
{{
  "final_decision": "<alert|suppress|log|defer>",
  "final_protocol": "<emergency|navigation|wellness|stress|sleep|normal|battery|defer|sleep_defer|meditation_defer|navigation_priority>",
  "overridden": <true|false>,
  "override_reason": "<null or one sentence why you overrode>",
  "arbiter_reasoning": "<2-3 sentences of your wisdom-based reasoning>",
  "wisdom_applied": "<safety_first|respect_sleep|respect_focus|exercise_context|navigation_safety|agreement>",
  "defer_minutes": <null or number>
}}"""

    # raw = call_ollama(prompt, max_tokens=400)
    # result = parse_json(raw)

    # if result and "final_decision" in result:
    #     result["source"] = "gemma3:1b"
    #     return result

    # Bypass LLM API for smooth streaming
    return arbiter_fallback(profiler_state, action_state, tick)
