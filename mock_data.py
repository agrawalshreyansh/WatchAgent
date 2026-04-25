from datetime import datetime

def ts():
    return datetime.now().strftime("%H:%M:%S")

SCENARIOS = {
    "normal_commute": {
        "label": "🚇 Normal Commute",
        "color": "#00e676",
        "tag": "LOW RISK",
        "description": "Familiar route, stable vitals, user in transit",
        "expected": "LOG",
        "ticks": [
            {"heart_rate": 72, "hrv": 48, "spo2": 98, "accelerometer": {"activity": "transit", "steps_per_min": 0, "magnitude": 0.4}, "gps": {"context": "familiar_zone", "label": "Koramangala Metro"}, "active_app": "Spotify", "battery_pct": 65, "screen_on": False},
            {"heart_rate": 74, "hrv": 46, "spo2": 98, "accelerometer": {"activity": "transit", "steps_per_min": 0, "magnitude": 0.5}, "gps": {"context": "familiar_zone", "label": "Koramangala Metro"}, "active_app": "Spotify", "battery_pct": 64, "screen_on": False},
            {"heart_rate": 76, "hrv": 45, "spo2": 97, "accelerometer": {"activity": "walking", "steps_per_min": 88, "magnitude": 1.1}, "gps": {"context": "familiar_zone", "label": "Indiranagar"}, "active_app": "Maps", "battery_pct": 63, "screen_on": True},
            {"heart_rate": 75, "hrv": 47, "spo2": 98, "accelerometer": {"activity": "walking", "steps_per_min": 85, "magnitude": 1.0}, "gps": {"context": "familiar_zone", "label": "Indiranagar"}, "active_app": "Spotify", "battery_pct": 62, "screen_on": False},
            {"heart_rate": 73, "hrv": 49, "spo2": 98, "accelerometer": {"activity": "transit", "steps_per_min": 0, "magnitude": 0.3}, "gps": {"context": "familiar_zone", "label": "Office Area"}, "active_app": "Slack", "battery_pct": 61, "screen_on": True},
            {"heart_rate": 71, "hrv": 50, "spo2": 98, "accelerometer": {"activity": "sedentary", "steps_per_min": 0, "magnitude": 0.1}, "gps": {"context": "familiar_zone", "label": "Office"}, "active_app": "Slack", "battery_pct": 60, "screen_on": False},
        ]
    },

    "morning_wake": {
        "label": "☀️ Morning Wake Up",
        "color": "#69f0ae",
        "tag": "RESTING",
        "description": "8 AM — calm morning, just woke up, low HR — system stays silent",
        "expected": "LOG (SILENT)",
        "ticks": [
            {"heart_rate": 58, "hrv": 68, "spo2": 98, "accelerometer": {"activity": "stationary", "steps_per_min": 0, "magnitude": 0.02}, "gps": {"context": "familiar_zone", "label": "Home"}, "active_app": "Clock", "battery_pct": 82, "screen_on": False},
            {"heart_rate": 62, "hrv": 65, "spo2": 98, "accelerometer": {"activity": "stationary", "steps_per_min": 0, "magnitude": 0.05}, "gps": {"context": "familiar_zone", "label": "Home"}, "active_app": "Clock", "battery_pct": 81, "screen_on": True},
            {"heart_rate": 65, "hrv": 62, "spo2": 99, "accelerometer": {"activity": "sedentary", "steps_per_min": 0, "magnitude": 0.1}, "gps": {"context": "familiar_zone", "label": "Home"}, "active_app": "Weather", "battery_pct": 80, "screen_on": True},
            {"heart_rate": 67, "hrv": 60, "spo2": 98, "accelerometer": {"activity": "walking", "steps_per_min": 40, "magnitude": 0.6}, "gps": {"context": "familiar_zone", "label": "Home"}, "active_app": "Notes", "battery_pct": 79, "screen_on": True},
        ]
    },

    "morning_jog": {
        "label": "🏃 Morning Jog",
        "color": "#00b0ff",
        "tag": "SUPPRESS",
        "description": "9:30 AM — HR spikes to 130+ during intentional jog — system correctly stays quiet",
        "expected": "SUPPRESS (exercise context)",
        "ticks": [
            {"heart_rate": 95, "hrv": 42, "spo2": 97, "accelerometer": {"activity": "running", "steps_per_min": 145, "magnitude": 3.2}, "gps": {"context": "familiar_zone", "label": "Neighborhood Park"}, "active_app": "Strava", "battery_pct": 75, "screen_on": True},
            {"heart_rate": 118, "hrv": 38, "spo2": 97, "accelerometer": {"activity": "running", "steps_per_min": 162, "magnitude": 3.8}, "gps": {"context": "familiar_zone", "label": "Neighborhood Park"}, "active_app": "Strava", "battery_pct": 74, "screen_on": True},
            {"heart_rate": 132, "hrv": 34, "spo2": 96, "accelerometer": {"activity": "running", "steps_per_min": 170, "magnitude": 4.1}, "gps": {"context": "familiar_zone", "label": "Cubbon Park"}, "active_app": "Strava", "battery_pct": 73, "screen_on": True},
            {"heart_rate": 145, "hrv": 31, "spo2": 96, "accelerometer": {"activity": "running", "steps_per_min": 175, "magnitude": 4.4}, "gps": {"context": "familiar_zone", "label": "Cubbon Park"}, "active_app": "Strava", "battery_pct": 72, "screen_on": True},
            {"heart_rate": 155, "hrv": 29, "spo2": 95, "accelerometer": {"activity": "running", "steps_per_min": 178, "magnitude": 4.6}, "gps": {"context": "familiar_zone", "label": "Cubbon Park"}, "active_app": "Strava", "battery_pct": 71, "screen_on": True},
            {"heart_rate": 148, "hrv": 33, "spo2": 96, "accelerometer": {"activity": "running", "steps_per_min": 172, "magnitude": 4.2}, "gps": {"context": "familiar_zone", "label": "Cubbon Park"}, "active_app": "Strava", "battery_pct": 70, "screen_on": True},
        ]
    },

    "meditation_battery": {
        "label": "🧘 Meditation + Low Battery",
        "color": "#7c4dff",
        "tag": "ARBITER OVERRIDE",
        "description": "10 AM — meditating at office, battery at 15% — Arbiter defers the battery alert",
        "expected": "DEFER (Arbiter overrides alert)",
        "ticks": [
            {"heart_rate": 72, "hrv": 58, "spo2": 98, "accelerometer": {"activity": "sedentary", "steps_per_min": 0, "magnitude": 0.05}, "gps": {"context": "unfamiliar_zone", "label": "Office Meeting Room"}, "active_app": "Headspace", "battery_pct": 20, "screen_on": True},
            {"heart_rate": 70, "hrv": 60, "spo2": 98, "accelerometer": {"activity": "stationary", "steps_per_min": 0, "magnitude": 0.03}, "gps": {"context": "unfamiliar_zone", "label": "Office Meeting Room"}, "active_app": "Headspace", "battery_pct": 17, "screen_on": False},
            {"heart_rate": 68, "hrv": 62, "spo2": 99, "accelerometer": {"activity": "stationary", "steps_per_min": 0, "magnitude": 0.02}, "gps": {"context": "unfamiliar_zone", "label": "Office Meeting Room"}, "active_app": "Headspace", "battery_pct": 15, "screen_on": False},
            {"heart_rate": 67, "hrv": 64, "spo2": 99, "accelerometer": {"activity": "stationary", "steps_per_min": 0, "magnitude": 0.02}, "gps": {"context": "unfamiliar_zone", "label": "Office Meeting Room"}, "active_app": "Headspace", "battery_pct": 13, "screen_on": False},
            {"heart_rate": 66, "hrv": 65, "spo2": 99, "accelerometer": {"activity": "stationary", "steps_per_min": 0, "magnitude": 0.01}, "gps": {"context": "unfamiliar_zone", "label": "Office Meeting Room"}, "active_app": "Headspace", "battery_pct": 11, "screen_on": False},
        ]
    },

    "lunch_drive_emergency": {
        "label": "🚨 Lunch Drive Emergency",
        "color": "#ff1744",
        "tag": "EMERGENCY",
        "description": "12 PM — driving to lunch, HR spikes to 155, completely still, unfamiliar neighborhood",
        "expected": "EMERGENCY_PROTOCOL",
        "ticks": [
            {"heart_rate": 82, "hrv": 44, "spo2": 98, "accelerometer": {"activity": "transit", "steps_per_min": 0, "magnitude": 0.4}, "gps": {"context": "unfamiliar_zone", "label": "Whitefield Rd"}, "active_app": "Maps", "battery_pct": 48, "screen_on": True},
            {"heart_rate": 95, "hrv": 36, "spo2": 97, "accelerometer": {"activity": "sedentary", "steps_per_min": 0, "magnitude": 0.2}, "gps": {"context": "unfamiliar_zone", "label": "Whitefield Rd"}, "active_app": "Maps", "battery_pct": 47, "screen_on": True},
            {"heart_rate": 118, "hrv": 28, "spo2": 96, "accelerometer": {"activity": "sedentary", "steps_per_min": 0, "magnitude": 0.15}, "gps": {"context": "unfamiliar_zone", "label": "Outer Ring Road"}, "active_app": "Maps", "battery_pct": 46, "screen_on": True},
            {"heart_rate": 142, "hrv": 20, "spo2": 95, "accelerometer": {"activity": "stationary", "steps_per_min": 0, "magnitude": 0.1}, "gps": {"context": "unfamiliar_zone", "label": "Outer Ring Road"}, "active_app": "Maps", "battery_pct": 46, "screen_on": True},
            {"heart_rate": 155, "hrv": 16, "spo2": 94, "accelerometer": {"activity": "stationary", "steps_per_min": 0, "magnitude": 0.08}, "gps": {"context": "unfamiliar_zone", "label": "Varthur Junction"}, "active_app": "Maps", "battery_pct": 45, "screen_on": True},
            {"heart_rate": 158, "hrv": 14, "spo2": 93, "accelerometer": {"activity": "stationary", "steps_per_min": 0, "magnitude": 0.09}, "gps": {"context": "unfamiliar_zone", "label": "Varthur Junction"}, "active_app": "Maps", "battery_pct": 45, "screen_on": True},
        ]
    },

    "movie_sleep": {
        "label": "🎬 Movie Nap (Battery Critical)",
        "color": "#9c27b0",
        "tag": "ARBITER OVERRIDE",
        "description": "2 PM — fell asleep watching movie, battery drops to 5% — Arbiter lets them sleep",
        "expected": "DEFER (Arbiter overrides battery alert)",
        "ticks": [
            {"heart_rate": 68, "hrv": 62, "spo2": 98, "accelerometer": {"activity": "stationary", "steps_per_min": 0, "magnitude": 0.05}, "gps": {"context": "familiar_zone", "label": "Home"}, "active_app": "Netflix", "battery_pct": 18, "screen_on": True},
            {"heart_rate": 62, "hrv": 68, "spo2": 98, "accelerometer": {"activity": "stationary", "steps_per_min": 0, "magnitude": 0.03}, "gps": {"context": "familiar_zone", "label": "Home"}, "active_app": "Netflix", "battery_pct": 12, "screen_on": False},
            {"heart_rate": 57, "hrv": 74, "spo2": 99, "accelerometer": {"activity": "stationary", "steps_per_min": 0, "magnitude": 0.02}, "gps": {"context": "familiar_zone", "label": "Home"}, "active_app": "Sleep Tracker", "battery_pct": 8, "screen_on": False},
            {"heart_rate": 55, "hrv": 76, "spo2": 99, "accelerometer": {"activity": "stationary", "steps_per_min": 0, "magnitude": 0.01}, "gps": {"context": "familiar_zone", "label": "Home"}, "active_app": "Sleep Tracker", "battery_pct": 5, "screen_on": False},
            {"heart_rate": 54, "hrv": 78, "spo2": 99, "accelerometer": {"activity": "stationary", "steps_per_min": 0, "magnitude": 0.01}, "gps": {"context": "familiar_zone", "label": "Home"}, "active_app": "Sleep Tracker", "battery_pct": 4, "screen_on": False},
        ]
    },

    "emergency_hr_spike": {
        "label": "💀 HR Spike (Sedentary)",
        "color": "#ff1744",
        "tag": "EMERGENCY",
        "description": "HR spikes while user is completely still at desk — potential cardiac event",
        "expected": "ALERT",
        "ticks": [
            {"heart_rate": 76, "hrv": 44, "spo2": 98, "accelerometer": {"activity": "sedentary", "steps_per_min": 0, "magnitude": 0.08}, "gps": {"context": "familiar_zone", "label": "Office Desk"}, "active_app": "VS Code", "battery_pct": 54, "screen_on": True},
            {"heart_rate": 88, "hrv": 38, "spo2": 97, "accelerometer": {"activity": "sedentary", "steps_per_min": 0, "magnitude": 0.09}, "gps": {"context": "familiar_zone", "label": "Office Desk"}, "active_app": "VS Code", "battery_pct": 54, "screen_on": True},
            {"heart_rate": 108, "hrv": 30, "spo2": 96, "accelerometer": {"activity": "sedentary", "steps_per_min": 0, "magnitude": 0.1}, "gps": {"context": "familiar_zone", "label": "Office Desk"}, "active_app": "VS Code", "battery_pct": 53, "screen_on": True},
            {"heart_rate": 135, "hrv": 22, "spo2": 95, "accelerometer": {"activity": "sedentary", "steps_per_min": 0, "magnitude": 0.1}, "gps": {"context": "familiar_zone", "label": "Office Desk"}, "active_app": "VS Code", "battery_pct": 53, "screen_on": True},
            {"heart_rate": 158, "hrv": 16, "spo2": 94, "accelerometer": {"activity": "sedentary", "steps_per_min": 0, "magnitude": 0.12}, "gps": {"context": "familiar_zone", "label": "Office Desk"}, "active_app": "VS Code", "battery_pct": 52, "screen_on": True},
            {"heart_rate": 162, "hrv": 14, "spo2": 93, "accelerometer": {"activity": "sedentary", "steps_per_min": 0, "magnitude": 0.11}, "gps": {"context": "familiar_zone", "label": "Office Desk"}, "active_app": "VS Code", "battery_pct": 52, "screen_on": True},
        ]
    },

    "smart_suppress_navigation": {
        "label": "🔋 Low Battery + Navigation",
        "color": "#ffab00",
        "tag": "SUPPRESS",
        "description": "5% battery but user navigating unfamiliar city — agent stays quiet",
        "expected": "SUPPRESS",
        "ticks": [
            {"heart_rate": 80, "hrv": 42, "spo2": 98, "accelerometer": {"activity": "walking", "steps_per_min": 95, "magnitude": 1.2}, "gps": {"context": "unfamiliar_zone", "label": "Hyderabad Old City"}, "active_app": "Google Maps", "battery_pct": 12, "screen_on": True},
            {"heart_rate": 82, "hrv": 40, "spo2": 98, "accelerometer": {"activity": "walking", "steps_per_min": 98, "magnitude": 1.3}, "gps": {"context": "unfamiliar_zone", "label": "Hyderabad Old City"}, "active_app": "Google Maps", "battery_pct": 9, "screen_on": True},
            {"heart_rate": 83, "hrv": 41, "spo2": 97, "accelerometer": {"activity": "walking", "steps_per_min": 100, "magnitude": 1.2}, "gps": {"context": "unfamiliar_zone", "label": "Hyderabad Old City"}, "active_app": "Google Maps", "battery_pct": 7, "screen_on": True},
            {"heart_rate": 81, "hrv": 40, "spo2": 98, "accelerometer": {"activity": "walking", "steps_per_min": 92, "magnitude": 1.1}, "gps": {"context": "unfamiliar_zone", "label": "Charminar Area"}, "active_app": "Google Maps", "battery_pct": 5, "screen_on": True},
            {"heart_rate": 82, "hrv": 39, "spo2": 98, "accelerometer": {"activity": "walking", "steps_per_min": 94, "magnitude": 1.2}, "gps": {"context": "unfamiliar_zone", "label": "Charminar Area"}, "active_app": "Google Maps", "battery_pct": 4, "screen_on": True},
        ]
    },

    "deep_sleep": {
        "label": "😴 Deep Sleep",
        "color": "#3d5afe",
        "tag": "SLEEPING",
        "description": "User in deep sleep — agent silences all non-critical alerts",
        "expected": "LOG",
        "ticks": [
            {"heart_rate": 56, "hrv": 72, "spo2": 98, "accelerometer": {"activity": "stationary", "steps_per_min": 0, "magnitude": 0.02}, "gps": {"context": "familiar_zone", "label": "Home"}, "active_app": "Sleep Tracker", "battery_pct": 88, "screen_on": False},
            {"heart_rate": 54, "hrv": 75, "spo2": 99, "accelerometer": {"activity": "stationary", "steps_per_min": 0, "magnitude": 0.02}, "gps": {"context": "familiar_zone", "label": "Home"}, "active_app": "Sleep Tracker", "battery_pct": 89, "screen_on": False},
            {"heart_rate": 52, "hrv": 78, "spo2": 99, "accelerometer": {"activity": "stationary", "steps_per_min": 0, "magnitude": 0.01}, "gps": {"context": "familiar_zone", "label": "Home"}, "active_app": "Sleep Tracker", "battery_pct": 90, "screen_on": False},
            {"heart_rate": 53, "hrv": 76, "spo2": 98, "accelerometer": {"activity": "stationary", "steps_per_min": 0, "magnitude": 0.02}, "gps": {"context": "familiar_zone", "label": "Home"}, "active_app": "Sleep Tracker", "battery_pct": 91, "screen_on": False},
        ]
    },

    "stress_commute": {
        "label": "😰 Stressed + Unfamiliar City",
        "color": "#ff6d00",
        "tag": "HIGH STRESS",
        "description": "Elevated HR, low HRV, navigating unknown area — agent monitors carefully",
        "expected": "LOG + STRESS WATCH",
        "ticks": [
            {"heart_rate": 94, "hrv": 32, "spo2": 97, "accelerometer": {"activity": "walking", "steps_per_min": 110, "magnitude": 1.4}, "gps": {"context": "unfamiliar_zone", "label": "Mumbai CST Area"}, "active_app": "Google Maps", "battery_pct": 38, "screen_on": True},
            {"heart_rate": 98, "hrv": 29, "spo2": 97, "accelerometer": {"activity": "walking", "steps_per_min": 115, "magnitude": 1.5}, "gps": {"context": "unfamiliar_zone", "label": "Mumbai CST Area"}, "active_app": "Google Maps", "battery_pct": 37, "screen_on": True},
            {"heart_rate": 102, "hrv": 27, "spo2": 96, "accelerometer": {"activity": "walking", "steps_per_min": 118, "magnitude": 1.6}, "gps": {"context": "unfamiliar_zone", "label": "Dadar Station"}, "active_app": "Google Maps", "battery_pct": 36, "screen_on": True},
            {"heart_rate": 105, "hrv": 25, "spo2": 96, "accelerometer": {"activity": "walking", "steps_per_min": 120, "magnitude": 1.6}, "gps": {"context": "unfamiliar_zone", "label": "Dadar Station"}, "active_app": "Google Maps", "battery_pct": 35, "screen_on": True},
        ]
    },

    "workout_suppress": {
        "label": "🏋️ Workout (Smart Suppress)",
        "color": "#00e5ff",
        "tag": "SUPPRESS",
        "description": "HR at 172 but user is running — no emergency, context is exercise",
        "expected": "SUPPRESS",
        "ticks": [
            {"heart_rate": 142, "hrv": 38, "spo2": 97, "accelerometer": {"activity": "running", "steps_per_min": 168, "magnitude": 3.8}, "gps": {"context": "familiar_zone", "label": "Cubbon Park"}, "active_app": "Strava", "battery_pct": 41, "screen_on": True},
            {"heart_rate": 155, "hrv": 35, "spo2": 96, "accelerometer": {"activity": "running", "steps_per_min": 172, "magnitude": 4.1}, "gps": {"context": "familiar_zone", "label": "Cubbon Park"}, "active_app": "Strava", "battery_pct": 40, "screen_on": True},
            {"heart_rate": 162, "hrv": 32, "spo2": 96, "accelerometer": {"activity": "running", "steps_per_min": 175, "magnitude": 4.3}, "gps": {"context": "familiar_zone", "label": "Cubbon Park"}, "active_app": "Strava", "battery_pct": 39, "screen_on": True},
            {"heart_rate": 172, "hrv": 28, "spo2": 95, "accelerometer": {"activity": "running", "steps_per_min": 180, "magnitude": 4.6}, "gps": {"context": "familiar_zone", "label": "Cubbon Park"}, "active_app": "Strava", "battery_pct": 38, "screen_on": True},
        ]
    },
}


def get_tick(scenario_key, tick_index):
    scenario = SCENARIOS[scenario_key]
    ticks = scenario["ticks"]
    tick = ticks[tick_index % len(ticks)].copy()
    tick["timestamp"] = datetime.now().strftime("%H:%M:%S")
    tick["scenario"] = scenario_key
    return tick
