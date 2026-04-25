import streamlit as st
import time
from mock_data import SCENARIOS, get_tick
from agents import run_profiler, run_action_agent, run_arbiter

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Wearable Context Engine",
    page_icon="⌚",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=Inter:wght@300;400;500;600&display=swap');

html, body, .stApp {
    background: radial-gradient(circle at top, #111116 0%, #050505 100%) !important;
    font-family: 'Inter', sans-serif;
    color: #e0e0e0;
}

/* Hide streamlit chrome */
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding: 2rem 2.5rem !important; max-width: 100% !important; }

/* Custom Streamlit Buttons */
div.stButton > button {
    background: rgba(255, 255, 255, 0.03);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 8px;
    color: #a0a0a0;
    font-family: 'Space Mono', monospace;
    font-size: 0.75rem;
    transition: all 0.3s ease;
}
div.stButton > button:hover {
    background: rgba(255, 255, 255, 0.1);
    border-color: rgba(255, 255, 255, 0.2);
    color: #ffffff;
    transform: translateY(-1px);
}

/* Header */
.dash-header {
    display: flex; align-items: center; justify-content: space-between;
    padding-bottom: 1rem; margin-bottom: 1.5rem;
}
.dash-title { 
    font-family: 'Space Mono', monospace; 
    font-size: 1.3rem; 
    font-weight: 700;
    background: linear-gradient(90deg, #ffffff, #888888);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    letter-spacing: 0.05em; 
}
.dash-subtitle { font-size: 0.75rem; color: #666; letter-spacing: 0.15em; text-transform: uppercase; margin-top: 4px; }
.live-dot { display: inline-block; width: 6px; height: 6px; border-radius: 50%; background: #00e676; margin-right: 8px; animation: pulse 2s infinite; box-shadow: 0 0 8px #00e676; }
@keyframes pulse { 0%,100%{opacity:1;} 50%{opacity:0.4;} }
.live-badge { font-family: 'Space Mono', monospace; font-size: 0.65rem; color: #00e676; letter-spacing: 0.2em; }

/* Panel cards - Glassmorphism */
.panel-card {
    background: rgba(15, 15, 18, 0.4);
    backdrop-filter: blur(16px);
    -webkit-backdrop-filter: blur(16px);
    border: 1px solid rgba(255, 255, 255, 0.04);
    border-radius: 16px;
    padding: 1.25rem;
    height: 580px;
    overflow-y: auto;
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
}
.panel-title {
    font-family: 'Space Mono', monospace;
    font-size: 0.65rem;
    color: #666;
    letter-spacing: 0.2em;
    text-transform: uppercase;
    margin-bottom: 1.2rem;
    border-bottom: 1px solid rgba(255,255,255,0.03);
    padding-bottom: 0.75rem;
}

/* Telemetry row */
.tele-row {
    font-family: 'Space Mono', monospace;
    font-size: 0.65rem;
    color: #777;
    padding: 8px 0;
    border-bottom: 1px solid rgba(255,255,255,0.02);
    line-height: 1.8;
}
.tele-ts { color: #444; margin-right: 12px; }
.tele-key { color: #555; }
.tele-val { color: #aaaaaa; }
.tele-hr-high { color: #ff5252; font-weight: 700; text-shadow: 0 0 5px rgba(255,82,82,0.4); }
.tele-hr-ok { color: #69f0ae; }
.tele-hr-mid { color: #ffd740; }

/* Profiler state */
.state-chip {
    display: inline-block;
    padding: 4px 12px;
    border-radius: 24px;
    font-family: 'Space Mono', monospace;
    font-size: 0.65rem;
    font-weight: 700;
    letter-spacing: 0.15em;
    text-transform: uppercase;
    margin-bottom: 12px;
}
.profiler-summary {
    font-size: 0.9rem;
    font-weight: 300;
    color: #ddd;
    line-height: 1.6;
    margin-bottom: 1.5rem;
    padding-left: 12px;
    border-left: 2px solid rgba(255,255,255,0.1);
}
.metric-row { display: flex; justify-content: space-between; margin-bottom: 6px; }
.metric-label { font-size: 0.65rem; color: #555; font-family: 'Space Mono', monospace; letter-spacing: 0.1em; }
.metric-bar-bg { height: 2px; background: rgba(255,255,255,0.04); border-radius: 2px; margin-top: 4px; overflow: hidden; }
.metric-bar-fill { height: 100%; border-radius: 2px; transition: width 0.8s cubic-bezier(0.22, 1, 0.36, 1); }

/* Action log */
.action-entry {
    padding: 12px 14px;
    border-radius: 10px;
    margin-bottom: 10px;
    border-left: 2px solid;
    background: rgba(0,0,0,0.2);
    transition: transform 0.2s;
}
.action-entry:hover { transform: translateX(2px); }
.action-alert { border-color: #ff5252; background: linear-gradient(90deg, rgba(255,82,82,0.05), transparent); }
.action-suppress { border-color: #ffd740; background: linear-gradient(90deg, rgba(255,215,64,0.03), transparent); }
.action-log { border-color: #69f0ae; background: linear-gradient(90deg, rgba(105,240,174,0.02), transparent); }
.action-defer { border-color: #b388ff; background: linear-gradient(90deg, rgba(179,136,255,0.04), transparent); }

.action-tag {
    font-family: 'Space Mono', monospace;
    font-size: 0.6rem;
    font-weight: 700;
    letter-spacing: 0.2em;
    text-transform: uppercase;
}
.tag-alert { color: #ff5252; }
.tag-suppress { color: #ffd740; }
.tag-log { color: #69f0ae; }
.tag-defer { color: #b388ff; }

.action-reason { font-size: 0.8rem; font-weight: 300; color: #bbb; margin-top: 6px; line-height: 1.5; }

/* Vital strip - Minimalist */
.vital-strip {
    display: flex; gap: 20px;
    background: rgba(15, 15, 18, 0.4);
    backdrop-filter: blur(12px);
    -webkit-backdrop-filter: blur(12px);
    border: 1px solid rgba(255, 255, 255, 0.04);
    border-radius: 100px;
    padding: 12px 32px;
    margin-bottom: 2rem;
    align-items: center;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.2);
}
.vital-item { text-align: center; }
.vital-val { font-family: 'Space Mono', monospace; font-size: 1.2rem; font-weight: 700; color: #fff; }
.vital-unit { font-size: 0.55rem; color: #555; text-transform: uppercase; letter-spacing: 0.2em; margin-top: 2px; }
.vital-divider { width: 1px; height: 24px; background: rgba(255,255,255,0.05); }

/* Scrollbar hidden for minimalist look */
::-webkit-scrollbar { display: none; }
</style>
""", unsafe_allow_html=True)


# ── Session state init ────────────────────────────────────────────────────────
if "running" not in st.session_state:
    st.session_state.running = True
if "scenario" not in st.session_state:
    st.session_state.scenario = "morning_wake"
if "tick_index" not in st.session_state:
    st.session_state.tick_index = 0
if "history" not in st.session_state:
    st.session_state.history = []
if "profiler_state" not in st.session_state:
    st.session_state.profiler_state = {}
if "action_log" not in st.session_state:
    st.session_state.action_log = []
if "arbiter_log" not in st.session_state:
    st.session_state.arbiter_log = []
if "emergency_notified" not in st.session_state:
    st.session_state.emergency_notified = False


def normalize_tick(raw_tick: dict, scenario_key: str) -> dict:
    """Ensure telemetry has required keys and safe defaults."""
    if not isinstance(raw_tick, dict):
        raw_tick = {}

    accel = raw_tick.get("accelerometer") or {}
    if not isinstance(accel, dict):
        accel = {}

    gps = raw_tick.get("gps") or {}
    if not isinstance(gps, dict):
        gps = {}

    scenario_meta = SCENARIOS.get(scenario_key, {})

    return {
        "timestamp": raw_tick.get("timestamp", "--:--:--"),
        "heart_rate": int(raw_tick.get("heart_rate", 75) or 75),
        "hrv": int(raw_tick.get("hrv", 45) or 45),
        "spo2": int(raw_tick.get("spo2", 98) or 98),
        "accelerometer": {
            "activity": accel.get("activity", "unknown"),
            "steps_per_min": int(accel.get("steps_per_min", 0) or 0),
            "magnitude": float(accel.get("magnitude", 0.0) or 0.0),
        },
        "gps": {
            "context": gps.get("context", "familiar_zone"),
            "label": gps.get("label", "Unknown"),
        },
        "active_app": raw_tick.get("active_app", "unknown"),
        "battery_pct": max(0, min(100, int(raw_tick.get("battery_pct", 50) or 50))),
        "screen_on": bool(raw_tick.get("screen_on", False)),
        "scenario": raw_tick.get("scenario", scenario_key),
        "scenario_label": scenario_meta.get("label", scenario_key),
        "scenario_color": scenario_meta.get("color", "#999"),
    }


# ── Header ────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="dash-header">
  <div class="dash-title">WATCHAGENT OS</div>
  <div>
    <span class="live-dot"></span>
    <span class="live-badge">LIVE STREAM</span>
  </div>
</div>
""", unsafe_allow_html=True)


# ── Scenario selector ─────────────────────────────────────────────────────────
st.markdown("<div style='font-family:Space Mono,monospace;font-size:0.62rem;color:#333;letter-spacing:0.18em;text-transform:uppercase;margin-bottom:8px;'>INJECT SCENARIO (SEAMLESS INJECTION)</div>", unsafe_allow_html=True)

import math
scenario_keys = list(SCENARIOS.keys())
cols_per_row = 5
rows = math.ceil(len(scenario_keys) / cols_per_row)

for r in range(rows):
    cols = st.columns(cols_per_row)
    for c in range(cols_per_row):
        idx = r * cols_per_row + c
        if idx < len(scenario_keys):
            key = scenario_keys[idx]
            scenario = SCENARIOS[key]
            with cols[c]:
                if st.button(scenario["label"], key=f"btn_{key}", use_container_width=True):
                    st.session_state.scenario = key
                    st.session_state.tick_index = 0
                    # Note: We NO LONGER clear the history/logs so the stream is continuous!


# ── Advance tick ──────────────────────────────────────────────────────────────
tick = get_tick(st.session_state.scenario, st.session_state.tick_index)
tick = normalize_tick(tick, st.session_state.scenario)
st.session_state.history.append(tick)
if len(st.session_state.history) > 25:
    st.session_state.history = st.session_state.history[-25:]

# Run 3 Agents
profiler_state = run_profiler(st.session_state.history)
action_state = run_action_agent(profiler_state, st.session_state.history)
arbiter_state = run_arbiter(profiler_state, action_state, st.session_state.history)

st.session_state.profiler_state = profiler_state

# Log to action log
action_entry = {
    "timestamp": tick.get("timestamp", "--:--:--"),
    "tick": st.session_state.tick_index,
    **action_state,
    "hr": tick.get("heart_rate", 75),
    "battery": tick.get("battery_pct", 50),
}
st.session_state.action_log.insert(0, action_entry)
if len(st.session_state.action_log) > 30:
    st.session_state.action_log = st.session_state.action_log[:30]

# Log to arbiter log
arbiter_entry = {
    "timestamp": tick.get("timestamp", "--:--:--"),
    "tick": st.session_state.tick_index,
    **arbiter_state,
}
st.session_state.arbiter_log.insert(0, arbiter_entry)
if len(st.session_state.arbiter_log) > 30:
    st.session_state.arbiter_log = st.session_state.arbiter_log[:30]

st.session_state.tick_index += 1


# ── Emergency Overlay ─────────────────────────────────────────────────────────
is_emergency = arbiter_state.get("final_protocol") == "emergency"
if is_emergency and not st.session_state.emergency_notified:
    st.toast("🚨 **EMERGENCY PROTOCOL ACTIVATED!**\nPotential medical event detected. Calling contacts & sharing GPS coordinates.", icon="🚨")
    st.session_state.emergency_notified = True
elif not is_emergency:
    st.session_state.emergency_notified = False


# ── Vital strip ───────────────────────────────────────────────────────────────
hr = tick.get("heart_rate", 75)
battery = tick.get("battery_pct", 50)
activity = tick.get("accelerometer", {}).get("activity", "unknown")

hr_color = "#ff1744" if hr > 130 else "#ffab00" if hr > 100 else "#00e676"
bat_color = "#ff1744" if battery < 10 else "#ffab00" if battery < 25 else "#00e676"

st.markdown(f"""
<div class="vital-strip">
  <div class="vital-item">
    <div class="vital-val" style="color:{hr_color};">{hr}</div>
    <div class="vital-unit">BPM</div>
  </div>
  <div class="vital-divider"></div>
  <div class="vital-item">
    <div class="vital-val" style="color:{bat_color};">{battery}%</div>
    <div class="vital-unit">BATTERY</div>
  </div>
  <div class="vital-divider"></div>
  <div class="vital-item">
    <div class="vital-val" style="font-size:0.85rem;text-transform:capitalize;">{activity}</div>
    <div class="vital-unit">ACTIVITY</div>
  </div>
  <div style="margin-left:auto;">
    <div style="font-family:Space Mono,monospace;font-size:0.62rem;color:#555;">SCENARIO</div>
        <div style="font-size:0.8rem;font-weight:600;color:{tick.get('scenario_color', '#999')};">{tick.get('scenario_label', st.session_state.scenario)}</div>
  </div>
</div>
""", unsafe_allow_html=True)


# ── Four panel layout ────────────────────────────────────────────────────────
col1, col2, col3, col4 = st.columns([1.1, 1, 1.1, 1.3])

# ── Panel 1: Live Telemetry ───────────────────────────────────────────────────
with col1:
    telemetry_html = '<div class="panel-card"><div class="panel-title">📡 Sensor Stream</div>'
    for t in reversed(st.session_state.history[-8:]):
        h = t.get("heart_rate", 75)
        t_activity = t.get("accelerometer", {}).get("activity", "unknown")
        t_battery = t.get("battery_pct", 50)
        t_timestamp = t.get("timestamp", "--:--:--")
        hr_cls = "tele-hr-high" if h > 130 else "tele-hr-mid" if h > 100 else "tele-hr-ok"
        telemetry_html += f"""
        <div class="tele-row" style="display:flex; justify-content:space-between; align-items:center;">
          <span class="tele-ts">{t_timestamp}</span>
          <span><span class="tele-key">HR:</span> <span class="{hr_cls}">{h}</span></span>
          <span><span class="tele-key">ACT:</span> <span class="tele-val">{t_activity}</span></span>
          <span><span class="tele-key">BAT:</span> <span class="tele-val">{t_battery}%</span></span>
        </div>"""
    telemetry_html += '</div>'
    st.markdown(telemetry_html, unsafe_allow_html=True)


# ── Panel 2: Profiler Agent ───────────────────────────────────────────────────
with col2:
    ps = profiler_state
    state_colors = {
        "sleeping": "#7c4dff", "exercising": "#00b0ff", "navigating": "#ffab00",
        "stressed": "#ff6d00", "commuting": "#00e676", "working": "#40c4ff",
        "resting": "#69f0ae", "meditating": "#9c27b0", "unknown": "#555"
    }
    state_val = ps.get("state", "unknown")
    s_color = state_colors.get(state_val, "#555")
    stress = ps.get("stress_level", 0)
    vuln = ps.get("vulnerability_score", 0)
    
    profiler_html = f"""
    <div class="panel-card">
      <div class="panel-title">🧠 1. PROFILER (OBSERVER)</div>
      <div class="state-chip" style="background:rgba(255,255,255,0.05);color:{s_color};border:1px solid {s_color}33;">
        {state_val.upper()}
      </div>
      <div class="profiler-summary">{ps.get('summary', 'Initializing...')}</div>
    </div>"""
    st.markdown(profiler_html, unsafe_allow_html=True)


# ── Panel 3: Action Agent ─────────────────────────────────────────────────────
with col3:
    action_html = '<div class="panel-card"><div class="panel-title">⚡ 2. ACTION (URGENCY)</div>'

    for entry in st.session_state.action_log[:5]:
        action = entry.get("action", "log")
        reason = entry.get("reason", "—")
        
        action_class = f"action-{action}"
        tag_class = f"tag-{action}"
        action_label = {"alert": "🚨 ALERT", "suppress": "🔇 SUPPRESS", "log": "📋 LOG", "defer": "⏳ DEFER"}.get(action, action.upper())

        action_html += f"""
        <div class="action-entry {action_class}">
          <div style="display:flex;justify-content:space-between;">
            <span class="action-tag {tag_class}">{action_label}</span>
          </div>
          <div class="action-reason">{reason}</div>
        </div>"""

    action_html += '</div>'
    st.markdown(action_html, unsafe_allow_html=True)

# ── Panel 4: Arbiter Agent ────────────────────────────────────────────────────
with col4:
    arbiter_html = '<div class="panel-card"><div class="panel-title">⚖️ 3. ARBITER (WISDOM)</div>'

    for entry in st.session_state.arbiter_log[:4]:
        final_decision = entry.get("final_decision", "log")
        overridden = entry.get("overridden", False)
        reasoning = entry.get("arbiter_reasoning", "—")
        
        status_color = "#ffab00" if overridden else "#00e676"
        status_text = "OVERRIDE" if overridden else "AGREED"
        
        arbiter_html += f"""
        <div class="action-entry" style="border-left-color:{status_color}; background:rgba(255,255,255,0.03);">
          <div style="display:flex;justify-content:space-between;margin-bottom:4px;">
            <span class="action-tag" style="color:{status_color};">{status_text} ➔ {final_decision.upper()}</span>
          </div>
          <div class="action-reason" style="color:#d0d0d0;font-size:0.75rem;">{reasoning}</div>
        </div>"""

    arbiter_html += '</div>'
    st.markdown(arbiter_html, unsafe_allow_html=True)


# ── Auto-advance ──────────────────────────────────────────────────────────────
col_ctrl1, col_ctrl2 = st.columns([1, 10])
with col_ctrl1:
    if st.button("⏸ Pause" if st.session_state.running else "▶ Resume"):
        st.session_state.running = not st.session_state.running
        st.rerun()

st.markdown(f"<div style='font-family:Space Mono,monospace;font-size:0.65rem;color:#333;padding-top:10px;'>TICK #{st.session_state.tick_index - 1}</div>", unsafe_allow_html=True)

if st.session_state.running:
    time.sleep(1)
    st.rerun()
