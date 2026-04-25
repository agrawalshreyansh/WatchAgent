package com.example.fitbridge.worker

import android.content.Context
import androidx.work.CoroutineWorker
import androidx.work.WorkerParameters
import com.example.fitbridge.FitnessRepository

class FitnessWorker(context: Context, params: WorkerParameters) : CoroutineWorker(context, params) {
    override suspend fun doWork(): Result {
        val repository = FitnessRepository(applicationContext)
        repository.fetchAndSendData()
        return Result.success()
    }
}
