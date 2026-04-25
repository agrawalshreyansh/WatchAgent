import streamlit as st
import time
import json
from datetime import datetime
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
@import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=DM+Sans:wght@300;400;500;600&display=swap');

html, body, .stApp {
    background-color: #07070f !important;
    font-family: 'DM Sans', sans-serif;
}

/* Hide streamlit chrome */
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding: 1rem 1.5rem !important; max-width: 100% !important; }

/* Header */
.dash-header {
    display: flex; align-items: center; justify-content: space-between;
    border-bottom: 1px solid rgba(255,255,255,0.07);
    padding-bottom: 0.75rem; margin-bottom: 1rem;
}
.dash-title { font-family: 'Space Mono', monospace; font-size: 1.1rem; color: #e0e0e0; letter-spacing: 0.08em; }
.dash-subtitle { font-size: 0.72rem; color: #555; letter-spacing: 0.12em; text-transform: uppercase; margin-top: 2px; }
.live-dot { display: inline-block; width: 8px; height: 8px; border-radius: 50%; background: #00e676; margin-right: 6px; animation: pulse 1.5s infinite; }
@keyframes pulse { 0%,100%{opacity:1;} 50%{opacity:0.3;} }
.live-badge { font-family: 'Space Mono', monospace; font-size: 0.68rem; color: #00e676; letter-spacing: 0.15em; }

/* Panel cards */
.panel-card {
    background: #0d0d1a;
    border: 1px solid rgba(255,255,255,0.07);
    border-radius: 10px;
    padding: 1rem;
    height: 550px;
    overflow-y: auto;
}
.panel-title {
    font-family: 'Space Mono', monospace;
    font-size: 0.68rem;
    color: #444;
    letter-spacing: 0.18em;
    text-transform: uppercase;
    margin-bottom: 0.75rem;
    border-bottom: 1px solid rgba(255,255,255,0.05);
    padding-bottom: 0.5rem;
}

/* Telemetry row */
.tele-row {
    font-family: 'Space Mono', monospace;
    font-size: 0.68rem;
    color: #8a8a8a;
    padding: 5px 0;
    border-bottom: 1px solid rgba(255,255,255,0.03);
    line-height: 1.6;
}
.tele-ts { color: #333; margin-right: 8px; }
.tele-key { color: #555; }
.tele-val { color: #c0c0c0; }
.tele-hr-high { color: #ff4444; font-weight: bold; }
.tele-hr-ok { color: #00e676; }
.tele-hr-mid { color: #ffab00; }

/* Profiler state */
.state-chip {
    display: inline-block;
    padding: 3px 10px;
    border-radius: 20px;
    font-family: 'Space Mono', monospace;
    font-size: 0.68rem;
    font-weight: 700;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    margin-bottom: 10px;
}
.profiler-summary {
    font-size: 0.85rem;
    color: #ccc;
    line-height: 1.5;
    margin-bottom: 1rem;
    padding: 10px;
    background: rgba(255,255,255,0.03);
    border-radius: 6px;
    border-left: 3px solid #2979ff;
}
.metric-row { display: flex; justify-content: space-between; margin-bottom: 8px; }
.metric-label { font-size: 0.72rem; color: #555; font-family: 'Space Mono', monospace; }
.metric-bar-bg { height: 4px; background: rgba(255,255,255,0.06); border-radius: 2px; margin-top: 3px; }
.metric-bar-fill { height: 4px; border-radius: 2px; transition: width 0.5s; }

/* Action log */
.action-entry {
    padding: 10px 12px;
    border-radius: 8px;
    margin-bottom: 8px;
    border-left: 3px solid;
    background: rgba(255,255,255,0.02);
}
.action-alert { background: rgba(255,23,68,0.08); border-color: #ff1744; }
.action-suppress { background: rgba(255,171,0,0.08); border-color: #ffab00; }
.action-log { background: rgba(0,230,118,0.05); border-color: rgba(0,230,118,0.3); }
.action-defer { background: rgba(124,77,255,0.08); border-color: #7c4dff; }

.action-tag {
    font-family: 'Space Mono', monospace;
    font-size: 0.62rem;
    font-weight: 700;
    letter-spacing: 0.15em;
    text-transform: uppercase;
}
.tag-alert { color: #ff1744; }
.tag-suppress { color: #ffab00; }
.tag-log { color: #00e676; }
.tag-defer { color: #7c4dff; }

.action-reason { font-size: 0.75rem; color: #aaa; margin-top: 4px; line-height: 1.4; }
.action-meta { font-family: 'Space Mono', monospace; font-size: 0.6rem; color: #333; margin-top: 5px; }

/* Vital strip */
.vital-strip {
    display: flex; gap: 12px;
    background: #0d0d1a;
    border: 1px solid rgba(255,255,255,0.07);
    border-radius: 8px;
    padding: 10px 16px;
    margin-bottom: 1rem;
    align-items: center;
}
.vital-item { text-align: center; }
.vital-val { font-family: 'Space Mono', monospace; font-size: 1.1rem; color: #e0e0e0; }
.vital-unit { font-size: 0.6rem; color: #444; text-transform: uppercase; letter-spacing: 0.1em; }
.vital-divider { width: 1px; height: 28px; background: rgba(255,255,255,0.06); }

/* Emergency Overlay */
.emergency-banner {
    background: linear-gradient(90deg, #d50000, #ff1744);
    color: white;
    padding: 20px;
    border-radius: 12px;
    margin-bottom: 1rem;
    display: flex;
    align-items: center;
    box-shadow: 0 4px 15px rgba(213,0,0,0.4);
    animation: pulse-border 1.5s infinite;
    border: 2px solid #ff5252;
}
@keyframes pulse-border { 0%,100%{box-shadow: 0 0 0 0 rgba(255,23,68,0.7);} 50%{box-shadow: 0 0 0 10px rgba(255,23,68,0);} }
.emergency-icon { font-size: 2.5rem; margin-right: 20px; }
.emergency-title { font-family: 'Space Mono', monospace; font-size: 1.2rem; font-weight: 700; letter-spacing: 0.1em; }
.emergency-text { font-size: 0.9rem; opacity: 0.9; margin-top: 5px; }

/* Scrollbar */
::-webkit-scrollbar { width: 3px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: #222; border-radius: 2px; }
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


# ── Header ────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="dash-header">
  <div>
    <div class="dash-title">⌚ WEARABLE CONTEXT ENGINE (3 AGENTS)</div>
    <div class="dash-subtitle">Profiler (Observer) · Action (Urgency) · Arbiter (Wisdom)</div>
  </div>
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
    "timestamp": tick["timestamp"],
    "tick": st.session_state.tick_index,
    **action_state,
    "hr": tick["heart_rate"],
    "battery": tick["battery_pct"],
}
st.session_state.action_log.insert(0, action_entry)
if len(st.session_state.action_log) > 30:
    st.session_state.action_log = st.session_state.action_log[:30]

# Log to arbiter log
arbiter_entry = {
    "timestamp": tick["timestamp"],
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
hr = tick["heart_rate"]
hrv = tick["hrv"]
spo2 = tick["spo2"]
battery = tick["battery_pct"]
activity = tick["accelerometer"]["activity"]

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
    <div class="vital-val">{hrv}</div>
    <div class="vital-unit">HRV ms</div>
  </div>
  <div class="vital-divider"></div>
  <div class="vital-item">
    <div class="vital-val">{spo2}%</div>
    <div class="vital-unit">SpO2</div>
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
  <div class="vital-divider"></div>
  <div class="vital-item">
    <div class="vital-val" style="font-size:0.85rem;">{tick['active_app']}</div>
    <div class="vital-unit">ACTIVE APP</div>
  </div>
  <div class="vital-divider"></div>
  <div class="vital-item">
    <div class="vital-val" style="font-size:0.78rem;">{tick['gps']['label']}</div>
    <div class="vital-unit">LOCATION</div>
  </div>
  <div style="margin-left:auto;">
    <div style="font-family:Space Mono,monospace;font-size:0.62rem;color:#333;">SCENARIO</div>
    <div style="font-size:0.8rem;color:{SCENARIOS[st.session_state.scenario]['color']};">{SCENARIOS[st.session_state.scenario]['label']}</div>
  </div>
</div>
""", unsafe_allow_html=True)


# ── Four panel layout ────────────────────────────────────────────────────────
col1, col2, col3, col4 = st.columns([1.1, 1, 1.1, 1.3])

# ── Panel 1: Live Telemetry ───────────────────────────────────────────────────
with col1:
    telemetry_html = '<div class="panel-card"><div class="panel-title">📡 Sensor Stream</div>'
    for t in reversed(st.session_state.history[-15:]):
        h = t["heart_rate"]
        hr_cls = "tele-hr-high" if h > 130 else "tele-hr-mid" if h > 100 else "tele-hr-ok"
        accel = t["accelerometer"]
        gps = t["gps"]
        telemetry_html += f"""
        <div class="tele-row">
          <span class="tele-ts">{t['timestamp']}</span><br>
          <span class="tele-key">HR: </span><span class="{hr_cls}">{h}</span>
          <span class="tele-key">HRV: </span><span class="tele-val">{t['hrv']}</span>
          <span class="tele-key">BAT: </span><span class="tele-val">{t['battery_pct']}%</span><br>
          <span class="tele-key">ACT: </span><span class="tele-val">{accel['activity']}</span>
          <span class="tele-key">LOC: </span><span class="tele-val">{gps['label']}</span><br>
          <span class="tele-key">APP: </span><span class="tele-val">{t['active_app']}</span>
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
    
    stress_color = "#ff1744" if stress > 7 else "#ffab00" if stress > 4 else "#00e676"
    vuln_color = "#ff1744" if vuln > 7 else "#ffab00" if vuln > 4 else "#00e676"
    
    flags_html = "".join([f"<span style='background:rgba(255,23,68,0.15);color:#ff1744;padding:2px 6px;border-radius:4px;font-size:0.6rem;margin-right:4px;'>{f}</span>" for f in ps.get('flags', [])])

    profiler_html = f"""
    <div class="panel-card">
      <div class="panel-title">🧠 1. PROFILER (OBSERVER)</div>
      <div class="state-chip" style="background:rgba(255,255,255,0.05);color:{s_color};border:1px solid {s_color}33;">
        {state_val.upper()}
      </div>
      <div class="profiler-summary">{ps.get('summary', 'Initializing...')}</div>

      <div style="margin-bottom:12px;">
        <div class="metric-row">
          <span class="metric-label">VULNERABILITY</span>
          <span style="font-family:Space Mono,monospace;font-size:0.72rem;color:{vuln_color};">{vuln}/10</span>
        </div>
        <div class="metric-bar-bg"><div class="metric-bar-fill" style="width:{min(100, vuln*10)}%;background:{vuln_color};"></div></div>
      </div>

      <div style="margin-bottom:12px;">
        <div class="metric-row">
          <span class="metric-label">STRESS INDEX</span>
          <span style="font-family:Space Mono,monospace;font-size:0.72rem;color:{stress_color};">{stress}/10</span>
        </div>
        <div class="metric-bar-bg"><div class="metric-bar-fill" style="width:{min(100, stress*10)}%;background:{stress_color};"></div></div>
      </div>
      
      <div style="margin-top:10px;margin-bottom:10px;">
        <div class="metric-label" style="margin-bottom:4px;">ACTIVE FLAGS</div>
        <div>{flags_html if flags_html else "<span style='color:#555;font-size:0.7rem;'>None</span>"}</div>
      </div>

      <div style="font-family:Space Mono,monospace;font-size:0.6rem;color:#444;margin-top:20px;">
        SOURCE: {"🤖 GEMMA3:1B" if ps.get("source") == "gemma3:1b" else "📐 RULE ENGINE"}
      </div>
    </div>"""
    st.markdown(profiler_html, unsafe_allow_html=True)


# ── Panel 3: Action Agent ─────────────────────────────────────────────────────
with col3:
    action_html = '<div class="panel-card"><div class="panel-title">⚡ 2. ACTION (URGENCY)</div>'

    for entry in st.session_state.action_log[:8]:
        action = entry.get("action", "log")
        severity = entry.get("severity", 1)
        reason = entry.get("reason", "—")
        
        action_class = f"action-{action}"
        tag_class = f"tag-{action}"
        action_label = {"alert": "🚨 ALERT", "suppress": "🔇 SUPPRESS", "log": "📋 LOG", "defer": "⏳ DEFER"}.get(action, action.upper())
        dots = "●" * severity + "○" * (5 - severity)

        action_html += f"""
        <div class="action-entry {action_class}">
          <div style="display:flex;justify-content:space-between;">
            <div>
              <span class="action-tag {tag_class}">{action_label}</span>
              <span style="font-family:Space Mono,monospace;font-size:0.6rem;color:#555;margin-left:6px;">{dots}</span>
            </div>
            <span style="font-size:0.6rem;color:#444;">#{entry.get('tick')}</span>
          </div>
          <div class="action-reason">{reason}</div>
        </div>"""

    action_html += '</div>'
    st.markdown(action_html, unsafe_allow_html=True)

# ── Panel 4: Arbiter Agent ────────────────────────────────────────────────────
with col4:
    arbiter_html = '<div class="panel-card"><div class="panel-title">⚖️ 3. ARBITER (WISDOM)</div>'

    for entry in st.session_state.arbiter_log[:6]:
        final_decision = entry.get("final_decision", "log")
        overridden = entry.get("overridden", False)
        reasoning = entry.get("arbiter_reasoning", "—")
        wisdom = entry.get("wisdom_applied", "—")
        
        status_color = "#ffab00" if overridden else "#00e676"
        status_text = "OVERRIDE" if overridden else "AGREED"
        
        arbiter_html += f"""
        <div class="action-entry" style="border-left-color:{status_color}; background:rgba(255,255,255,0.03);">
          <div style="display:flex;justify-content:space-between;margin-bottom:4px;">
            <span class="action-tag" style="color:{status_color};">{status_text} ➔ {final_decision.upper()}</span>
            <span style="font-family:Space Mono,monospace;font-size:0.6rem;color:#555;">[{wisdom}]</span>
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
