package com.example.sensores

import android.content.Context
import android.graphics.Canvas
import android.graphics.Color
import android.graphics.Paint
import android.util.AttributeSet
import android.view.View

class BallView @JvmOverloads constructor(
    context: Context, attrs: AttributeSet? = null
) : View(context, attrs) {

    private val ballPaint = Paint().apply {
        color = Color.BLUE
        isAntiAlias = true
    }

    private var posX = 0f
    private var posY = 0f

    override fun onDraw(canvas: Canvas) {
        super.onDraw(canvas)
        val centerX = width / 2f
        val centerY = height / 2f
        canvas.drawCircle(centerX + posX, centerY + posY, 50f, ballPaint)
    }

    fun updatePosition(accelX: Float, accelY: Float) {
        posX = accelX * 30
        posY = accelY * 30
        invalidate()
    }
}
