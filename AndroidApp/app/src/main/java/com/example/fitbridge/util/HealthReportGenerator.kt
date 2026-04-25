package com.example.fitbridge.util

import android.content.Context
import android.graphics.Canvas
import android.graphics.Color
import android.graphics.Paint
import android.graphics.pdf.PdfDocument
import android.os.Environment
import android.widget.Toast
import com.example.fitbridge.FitnessViewModel
import java.io.File
import java.io.FileOutputStream
import java.text.SimpleDateFormat
import java.util.*

object HealthReportGenerator {

    fun generatePdfReport(context: Context, viewModel: FitnessViewModel) {
        val pdfDocument = PdfDocument()
        val pageInfo = PdfDocument.PageInfo.Builder(595, 842, 1).create() // A4 size
        val page = pdfDocument.startPage(pageInfo)
        val canvas: Canvas = page.canvas
        val paint = Paint()
        val titlePaint = Paint().apply {
            textSize = 24f
            isFakeBoldText = true
            color = Color.BLACK
        }
        val textPaint = Paint().apply {
            textSize = 14f
            color = Color.BLACK
        }
        val labelPaint = Paint().apply {
            textSize = 16f
            isFakeBoldText = true
            color = Color.BLACK
        }

        var yPos = 50f

        // Header
        canvas.drawText("FitBridge Health Report", 50f, yPos, titlePaint)
        yPos += 30f
        canvas.drawText("Generated on: ${SimpleDateFormat("MMM dd, yyyy HH:mm", Locale.getDefault()).format(Date())}", 50f, yPos, textPaint)
        yPos += 50f

        // Summary Section
        canvas.drawText("Daily Summary", 50f, yPos, labelPaint)
        yPos += 25f
        canvas.drawText("Heart Rate: ${viewModel.heartRate.toInt()} bpm", 70f, yPos, textPaint)
        yPos += 20f
        canvas.drawText("Steps: ${viewModel.steps}", 70f, yPos, textPaint)
        yPos += 20f
        canvas.drawText("Oxygen (SpO2): ${viewModel.spo2.toInt()}%", 70f, yPos, textPaint)
        yPos += 20f
        canvas.drawText("Sleep: ${viewModel.sleepHours} hours", 70f, yPos, textPaint)
        yPos += 40f

        // AI Analysis - Three Agents
        canvas.drawText("WatchAgent OS Analysis", 50f, yPos, labelPaint)
        yPos += 25f
        canvas.drawText("Profiler [Observer]:", 70f, yPos, labelPaint.apply { textSize = 12f })
        yPos += 18f
        for (line in viewModel.profilerAgentLog.chunked(75)) {
            canvas.drawText(line, 80f, yPos, textPaint)
            yPos += 15f
        }
        yPos += 10f

        canvas.drawText("Action Agent [Urgency]:", 70f, yPos, labelPaint)
        yPos += 18f
        for (line in viewModel.actionAgentLog.chunked(75)) {
            canvas.drawText(line, 80f, yPos, textPaint)
            yPos += 15f
        }
        yPos += 10f

        canvas.drawText("Arbiter [Wisdom]:", 70f, yPos, labelPaint)
        yPos += 18f
        for (line in viewModel.arbiterAgentLog.chunked(75)) {
            canvas.drawText(line, 80f, yPos, textPaint)
            yPos += 15f
        }
        yPos += 25f

        // Final Verdict
        canvas.drawText("Final Verdict", 50f, yPos, labelPaint.apply { textSize = 16f })
        yPos += 25f
        for (line in viewModel.prescription.chunked(70)) {
            canvas.drawText(line, 70f, yPos, textPaint)
            yPos += 20f
        }
        yPos += 20f

        // Recommendations
        if (viewModel.recommendations.isNotEmpty()) {
            canvas.drawText("Top Recommendations", 50f, yPos, labelPaint)
            yPos += 25f
            for (rec in viewModel.recommendations.take(5)) {
                canvas.drawText("• $rec", 70f, yPos, textPaint)
                yPos += 20f
            }
        }

        pdfDocument.finishPage(page)

        // Save the file
        val directory = context.getExternalFilesDir(Environment.DIRECTORY_DOCUMENTS)
        val file = File(directory, "HealthReport_${System.currentTimeMillis()}.pdf")

        try {
            pdfDocument.writeTo(FileOutputStream(file))
            Toast.makeText(context, "Report saved: ${file.name}", Toast.LENGTH_LONG).show()
        } catch (e: Exception) {
            e.printStackTrace()
            Toast.makeText(context, "Error generating report", Toast.LENGTH_SHORT).show()
        } finally {
            pdfDocument.close()
        }
    }
}
