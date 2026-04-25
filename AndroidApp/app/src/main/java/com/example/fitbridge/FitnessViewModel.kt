package com.example.fitbridge

import android.content.Context
import android.util.Log
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableFloatStateOf
import androidx.compose.runtime.mutableIntStateOf
import androidx.compose.runtime.mutableStateListOf
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.setValue
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.example.fitbridge.ai.LocalAIAnalyzer
import com.example.fitbridge.model.DataPoint
import com.example.fitbridge.model.FitnessData
import com.google.gson.Gson
import kotlinx.coroutines.delay
import kotlinx.coroutines.launch
import java.text.SimpleDateFormat
import java.util.Date
import java.util.Locale

import java.util.UUID

data class ChatMessage(val text: String, val isUser: Boolean, val timestamp: Long = System.currentTimeMillis())

data class ChatSession(
    val id: String = UUID.randomUUID().toString(),
    val title: String,
    val messages: List<ChatMessage>
)

class FitnessViewModel(private val repository: FitnessRepository, context: Context) : ViewModel() {
    private val gson = Gson()
    private var lastFetchedData: FitnessData? = null

    val chatMessages = mutableStateListOf<ChatMessage>()
    val savedSessions = mutableStateListOf<ChatSession>()
    var currentSessionId by mutableStateOf<String?>(null)

    var mood by mutableStateOf("Analysing...")
    var stressLevel by mutableStateOf("Calculating...")
    var recommendations by mutableStateOf<List<String>>(emptyList())
    var prescription by mutableStateOf("")

    // Multi-Agent Logs
    var profilerAgentLog by mutableStateOf("Waiting for sensor stream...")
    var actionAgentLog by mutableStateOf("Standing by...")
    var arbiterAgentLog by mutableStateOf("Observing context...")

    var isChatting by mutableStateOf(false)
        private set
    var heartRate by mutableFloatStateOf(0f)
        private set
    var steps by mutableIntStateOf(0)
        private set
    var spo2 by mutableFloatStateOf(0f)
        private set
    var sleepHours by mutableFloatStateOf(0f)
        private set
    var workouts by mutableStateOf<List<String>>(emptyList())
        private set
    var lastUpdated by mutableStateOf("Never")
        private set
    var isSyncing by mutableStateOf(false)
        private set
    var syncStatus by mutableStateOf("")
        private set

    var aiInsight by mutableStateOf("Ready to analyze your data...")
        private set

    var heartRateHistory by mutableStateOf<List<DataPoint>>(emptyList())
        private set
    var stepHistory by mutableStateOf<List<DataPoint>>(emptyList())
        private set

    private val analyzer = LocalAIAnalyzer.getInstance(context)
    private val dateFormat = SimpleDateFormat("HH:mm:ss", Locale.getDefault())

    init {
        loadFromLocal()
    }

    override fun onCleared() {
        super.onCleared()
        // We don't necessarily want to close the singleton here if other ViewModels use it,
        // but since we only have one, it helps prevent resource leaks on process death/recreation
        // analyzer.close()
    }

    private fun loadFromLocal() {
        repository.getLatestLocalData()?.let { data ->
            updateUI(data)
        }
    }

    fun startPolling() {
        viewModelScope.launch {
            while (true) {
                syncData(isAuto = true)
                // Polling every 3 hours (3 * 60 * 60 * 1000 ms)
                delay(3 * 60 * 60 * 1000)
            }
        }
    }

    fun triggerManualSync() {
        viewModelScope.launch {
            syncData(isAuto = false)
        }
    }

    private suspend fun syncData(isAuto: Boolean) {
        if (isSyncing) return
        isSyncing = true
        syncStatus = "Syncing..."

        val data = repository.fetchAndSendData()
        if (data != null) {
            lastFetchedData = data
            updateUI(data)
            syncStatus = "Sync Successful"

            // Run Local AI Analysis
            Log.d("LocalAI", "Data fetched, checking model readiness...")
            aiInsight = "AI is thinking..."
            val json = gson.toJson(data)
            aiInsight = analyzer.generateInsight(json)
            updateMoodAndRecs(json)
            Log.d("LocalAI", "Insight generated: $aiInsight")
        } else {
            syncStatus = "Sync Failed"
        }

        isSyncing = false
        if (!isAuto) {
            delay(3000)
            if (!isSyncing) syncStatus = ""
        }
    }

    fun sendMessage(text: String) {
        if (text.isBlank()) return
        chatMessages.add(ChatMessage(text, true))
        isChatting = true

        viewModelScope.launch {
            Log.d("ChatAI", "Sending message: $text")
            val history = chatMessages.takeLast(10).joinToString("\n") {
                if (it.isUser) "User: ${it.text}" else "Assistant: ${it.text}"
            }
            val json = lastFetchedData?.let { gson.toJson(it) } ?: "{}"
            
            try {
                val response = analyzer.chat(history, text, json)
                Log.d("ChatAI", "Received response: $response")

                // Clean up common AI artifacts
                val cleanedResponse = response.substringBefore("<end_of_turn>")
                    .substringBefore("User:")
                    .trim()

                chatMessages.add(ChatMessage(cleanedResponse, false))
            } catch (e: Exception) {
                Log.e("ChatAI", "Error in chat", e)
                chatMessages.add(ChatMessage("Sorry, I encountered an error: ${e.message}", false))
            } finally {
                isChatting = false
            }
        }
    }

    fun startNewChat() {
        if (chatMessages.isNotEmpty()) {
            val title = chatMessages.firstOrNull { it.isUser }?.text?.take(20) ?: "New Chat"
            savedSessions.add(0, ChatSession(messages = chatMessages.toList(), title = "$title..."))
        }
        chatMessages.clear()
        currentSessionId = UUID.randomUUID().toString()
    }

    fun loadSession(session: ChatSession) {
        if (chatMessages.isNotEmpty()) {
            val title = chatMessages.firstOrNull { it.isUser }?.text?.take(20) ?: "Past Chat"
            savedSessions.add(0, ChatSession(messages = chatMessages.toList(), title = "$title..."))
        }
        chatMessages.clear()
        chatMessages.addAll(session.messages)
        savedSessions.remove(session)
        currentSessionId = session.id
    }

    fun clearHistory() {
        chatMessages.clear()
        savedSessions.clear()
        currentSessionId = null
    }

    private suspend fun updateMoodAndRecs(json: String) {
        val analysis = analyzer.analyzeMultiAgent(json)
        profilerAgentLog = analysis.profilerLog
        actionAgentLog = analysis.actionAgentLog
        arbiterAgentLog = analysis.arbiterLog
        prescription = analysis.result

        // Derive mood/stress from profiler
        mood = if (analysis.profilerLog.contains("exercise", true)) "Active 🏃" else "Calm 😌"
        stressLevel = if (analysis.profilerLog.contains("stress", true)) "Elevated" else "Low"

        recommendations = listOf(
            "Observation: ${analysis.profilerLog}",
            "Suggestion: ${analysis.arbiterLog}"
        )
    }

    private fun updateUI(data: FitnessData) {
        heartRate = data.heartRate
        steps = data.steps
        spo2 = data.spo2
        sleepHours = data.sleepHours
        workouts = data.workouts
        heartRateHistory = data.heartRateHistory
        stepHistory = data.stepHistory
        lastUpdated = dateFormat.format(Date(data.timestamp * 1000))
    }
}
