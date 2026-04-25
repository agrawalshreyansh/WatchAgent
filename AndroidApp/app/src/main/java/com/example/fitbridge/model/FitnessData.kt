package com.example.fitbridge.model

import com.google.gson.annotations.SerializedName

data class FitnessData(
    @SerializedName("heart_rate") val heartRate: Float,
    @SerializedName("steps") val steps: Int,
    @SerializedName("spo2") val spo2: Float,
    @SerializedName("sleep_hours") val sleepHours: Float,
    @SerializedName("workouts") val workouts: List<String>,
    @SerializedName("timestamp") val timestamp: Long,
    // Historical data for charts (optional for backend, used for UI)
    val heartRateHistory: List<DataPoint> = emptyList(),
    val stepHistory: List<DataPoint> = emptyList()
)

data class DataPoint(
    val timestamp: Long,
    val value: Float
)
