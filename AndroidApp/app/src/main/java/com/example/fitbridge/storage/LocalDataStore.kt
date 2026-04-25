package com.example.fitbridge.storage

import android.content.Context
import com.example.fitbridge.model.FitnessData
import com.google.gson.Gson
import com.google.gson.reflect.TypeToken
import java.io.File

class LocalDataStore(context: Context) {
    private val file = File(context.filesDir, "fitness_data.json")
    private val gson = Gson()

    fun saveData(data: FitnessData) {
        val history = loadAllData().toMutableList()
        // Add new data at the end
        history.add(data)

        // Keep only last 48 hours of snapshots to avoid file getting too large
        val cutoff = System.currentTimeMillis() / 1000 - (48 * 60 * 60)
        val filteredHistory = history.filter { it.timestamp > cutoff }

        file.writeText(gson.toJson(filteredHistory))
    }

    fun loadAllData(): List<FitnessData> {
        if (!file.exists()) return emptyList()
        return try {
            val json = file.readText()
            val type = object : TypeToken<List<FitnessData>>() {}.type
            gson.fromJson(json, type) ?: emptyList()
        } catch (e: Exception) {
            emptyList()
        }
    }

    fun getLatestData(): FitnessData? {
        return loadAllData().lastOrNull()
    }
}
