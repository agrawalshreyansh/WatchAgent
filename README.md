# ⌚ Wearable Context Engine (WatchAgent OS)

This project is a visual dashboard representation of a **Multi-Agent Wearable Context Engine**. It demonstrates how AI agents can process raw, high-frequency telemetry and biometric data from smartwatches to make autonomous, context-aware decisions regarding user safety, health, and notifications.

## 🚀 Edge-Native Architecture

This workflow is designed to be highly efficient. It can currently be implemented on any mobile device paired with a smartwatch. With further model quantization and specialized training, this exact multi-agent architecture is lightweight enough to run **natively on the smartwatch itself**.

We specifically built this utilizing the **Gemma-3 1B (`gemma3:1b`)** model. This model was chosen because:
1. It is explicitly designed for edge devices and mobile hardware.
2. It has an incredibly small memory footprint while maintaining the high reasoning accuracy required for our context agents.

## 🔗 The Data Pipeline & Simulation Challenge

In our real-world implementation, we built a mobile companion app that connects directly to the user's health ecosystem. The pipeline looks like this:

`Noise Smartwatch` ➔ `NoiseFit App` ➔ `Google Fit` ➔ `Android Health Connect` ➔ `Companion App`

### 📱 Real-World App Deployment

> **[Download the Companion Android App Here](https://drive.google.com/drive/folders/1ghFQ0oqob1gIt7aX4MNvQUBamgXggFWe?usp=sharing)** 

If you wish to test the live Android application rather than the simulation dashboard, please ensure your device is correctly configured to push biometric data to the Android health ecosystem:

1. Connect your smartwatch (e.g., Noise Smartwatch) to its native app (e.g., **NoiseFit App**).
2. Open the native app and configure it to sync your health data downstream to **Google Fit**.
3. Ensure **Google Fit** is granted permissions to sync into **Android Health Connect**.
4. Install and open our Companion App, which will securely pull the aggregated data from Health Connect and feed it into the WatchAgent OS.

### 🧪 Why build a simulation dashboard?
While the real-world pipeline works perfectly, the long synchronization chain introduces latency that makes live demonstrations of rapid, life-threatening scenarios (like a sudden cardiac spike while driving) difficult to showcase in real-time. 

To solve this, we built this Streamlit dashboard to cleanly **simulate** those exact scenarios. It allows us to seamlessly inject edge-case biometric data into the continuous stream and watch the Multi-Agent engine react instantly.

## 🧠 How the Agents Work

The system relies on three distinct AI agents evaluating the stream simultaneously:

1. **The Profiler (Observer)**: Constantly monitors the stream to deduce the user's state (e.g., "Commuting", "Sleeping", "Exercising"). It calculates a continuous Vulnerability Score and Stress Index.
2. **The Action Agent (Urgency)**: Looks for spikes and anomalies. It reacts instinctively to raw data (e.g., "Heart rate is 155 BPM! Issue an alert!").
3. **The Arbiter (Wisdom)**: The final decision-maker. It combines the Action Agent's urgency with the Profiler's context. (e.g., "Heart rate is 155 BPM, *but* the user is running in a familiar park. Suppress the alert, they are just exercising.")

## 🛠️ Running the Dashboard Locally

Make sure you have [Ollama](https://ollama.com/) installed and running locally.

1. Pull the Gemma 3 model:
   ```bash
   ollama pull gemma3:1b
   ```
2. Install dependencies:
   ```bash
   pip install streamlit requests
   ```
3. Run the dashboard:
   ```bash
   streamlit run app.py
   ```
