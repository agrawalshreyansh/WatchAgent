package com.example.fitbridge.ai

import android.content.Context
import android.util.Log
import com.google.mediapipe.tasks.genai.llminference.LlmInference
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.sync.Mutex
import kotlinx.coroutines.sync.withLock
import kotlinx.coroutines.withContext
import java.io.File

data class MultiAgentAnalysis(
    val profilerLog: String,
    val actionAgentLog: String,
    val arbiterLog: String,
    val result: String
)

class LocalAIAnalyzer private constructor(private val context: Context) {

    private var llmInference: LlmInference? = null
    private val aiMutex = Mutex()
    
    companion object {
        @Volatile
        private var instance: LocalAIAnalyzer? = null

        fun getInstance(context: Context): LocalAIAnalyzer {
            return instance ?: synchronized(this) {
                instance ?: LocalAIAnalyzer(context.applicationContext).also { instance = it }
            }
        }
    }
    
    // The user specified the model is at: /data/data/com.example.fitbridge/files/qwen.task
    private val modelPathTask = "/data/data/com.example.fitbridge/files/qwen.task"

    init {
        // Removed setupModel() from init to prevent UI freeze on main thread.
        // It will be called lazily on a background thread when needed.
    }

    private fun getExistingModelPath(): String? {
        val file = File(modelPathTask)
        val exists = file.exists()
        
        // Also check standard filesDir just in case
        val fallbackFile = File(context.filesDir, "qwen.task")
        
        Log.d("LocalAI", "Checking for model file at: $modelPathTask (exists=$exists)")
        
        return when {
            exists -> modelPathTask
            fallbackFile.exists() -> {
                Log.d("LocalAI", "Found model in fallback path: ${fallbackFile.absolutePath}")
                fallbackFile.absolutePath
            }
            else -> null
        }
    }

    private fun setupModel() {
        val path = getExistingModelPath() ?: return

        try {
            val options = LlmInference.LlmInferenceOptions.builder()
                .setModelPath(path)
                .setMaxTokens(1280) // Set to 1280 as recommended by logs
                .setMaxTopK(40)
                .setPreferredBackend(LlmInference.Backend.CPU) // Use CPU for better stability
                .build()

            llmInference = LlmInference.createFromOptions(context, options)
            Log.d("LocalAI", "Gemma model (qwen.task) loaded successfully on CPU")
        } catch (e: Exception) {
            Log.e("LocalAI", "Failed to initialize LLM: ${e.message}")
        }
    }

    fun close() {
        try {
            llmInference?.close()
            llmInference = null
            Log.d("LocalAI", "LlmInference closed")
        } catch (e: Exception) {
            Log.e("LocalAI", "Error closing LlmInference", e)
        }
    }

    fun isModelReady(): Boolean = getExistingModelPath() != null && llmInference != null

    suspend fun generateInsight(fitnessJson: String): String = withContext(Dispatchers.IO) {
        aiMutex.withLock {
            Log.d("LocalAI", "Generating insight with fitness data: $fitnessJson")
            if (llmInference == null) {
                Log.d("LocalAI", "llmInference is null, attempting to setup model")
                setupModel()
                if (llmInference == null) {
                    return@withLock "AI Model file (qwen.task) missing."
                }
            }

            val prompt = """
                <start_of_turn>user
                Context: You are a system of three AI agents (Profiler, Action Agent, Arbiter) protecting the user.
                Profiler: Analyzes sensor data.
                Action Agent: Proposes urgency and actions.
                Arbiter: Makes final wisdom-based decisions.
                
                Current Data: $fitnessJson
                
                Instruction: Provide a short "Day in the Life" story-style insight (max 2 sentences) about the user's current status from the perspective of the Arbiter.
                Provide only the insight text.<end_of_turn>
                <start_of_turn>model
            """.trimIndent()

            try {
                val response = llmInference?.generateResponse(prompt) ?: "Error: Inference returned null."
                response.substringBefore("<end_of_turn>").trim()
            } catch (e: Exception) {
                Log.e("LocalAI", "Generation error", e)
                "AI error: ${e.message}"
            }
        }
    }

    suspend fun analyzeMultiAgent(fitnessJson: String): MultiAgentAnalysis = withContext(Dispatchers.IO) {
        aiMutex.withLock {
            if (llmInference == null) {
                setupModel()
                if (llmInference == null) return@withLock MultiAgentAnalysis("Model missing", "Model missing", "Model missing", "No result")
            }

            val prompt = """
                <start_of_turn>user
                You are a system of three AI agents:
                1. PROFILER (Observer): Deduces user state (resting, exercising, driving, etc.) from sensors.
                2. ACTION AGENT (Urgency): Reacts to raw data spikes and proposes actions.
                3. ARBITER (Wisdom): Final decision maker. Overrides Action Agent if it's unwise to interrupt (e.g. meditation, sleep) for non-emergencies.
                
                Fitness Data: $fitnessJson
                
                Instruction: Provide a structured analysis.
                Format exactly as:
                PROFILER: [Text]
                ACTION_AGENT: [Text]
                ARBITER: [Text]
                RESULT: [Short 1-sentence outcome]
                
                Perspective: Keep it story-like as if these are employees talking.<end_of_turn>
                <start_of_turn>model
            """.trimIndent()

            try {
                val response = llmInference?.generateResponse(prompt) ?: ""
                // Clean up literal escape sequences like \n and <end_of_turn>
                val cleaned = response.substringBefore("<end_of_turn>")
                    .replace("\\n", "\n")
                    .trim()

                val profiler = cleaned.substringAfter("PROFILER:", "Analyzing...").substringBefore("ACTION_AGENT:").trim()
                val action = cleaned.substringAfter("ACTION_AGENT:", "Deciding...").substringBefore("ARBITER:").trim()
                val arbiter = cleaned.substringAfter("ARBITER:", "Evaluating...").substringBefore("RESULT:").trim()
                val result = cleaned.substringAfter("RESULT:", "Standing by").trim()

                MultiAgentAnalysis(profiler, action, arbiter, result)
            } catch (e: Exception) {
                MultiAgentAnalysis("Error", "Error", "Error", "AI Error: ${e.message}")
            }
        }
    }

    suspend fun chat(history: String, message: String, fitnessJson: String): String = withContext(Dispatchers.IO) {
        aiMutex.withLock {
            if (llmInference == null) {
                setupModel()
                if (llmInference == null) return@withLock "AI Model missing."
            }

            val prompt = """
                <start_of_turn>user
                You are a professional fitness coach. Help the user based on their fitness data.
                Fitness Data: $fitnessJson
                
                Instruction: Provide a very short, concise response (max 2 sentences).
                
                Chat History:
                $history
                
                User: $message<end_of_turn>
                <start_of_turn>model
            """.trimIndent()

            try {
                llmInference?.generateResponse(prompt) ?: "Error"
            } catch (e: Exception) {
                "Error: ${e.message}"
            }
        }
    }
}
