package com.example.fitbridge.api

import com.example.fitbridge.model.FitnessData
import retrofit2.Response
import retrofit2.http.Body
import retrofit2.http.POST

interface FitnessApi {
    @POST("data")
    suspend fun sendFitnessData(@Body data: FitnessData): Response<Map<String, String>>
}
