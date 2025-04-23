package com.example.tuxfly  // Asegúrate de que coincida con tu paquete real

import android.graphics.*
import kotlin.random.Random

class Obstacle(
    private val screenWidth: Int,
    private val screenHeight: Int,
    private val pipeBitmap: Bitmap
) {
    private val gap = 500  // Espacio entre tubos
    private val speed = 12 // Velocidad de desplazamiento

    var x = screenWidth.toFloat()
    private var y = Random.nextInt(gap, screenHeight - gap).toFloat()
    var isScored = false

    fun update() {
        x -= speed
    }

    fun isOffScreen(): Boolean = x + pipeBitmap.width < 0

    fun getTopPipe(): Rect {
        return Rect(x.toInt(), 0, (x + pipeBitmap.width).toInt(), (y - gap/2).toInt())
    }

    fun getBottomPipe(): Rect {
        return Rect(x.toInt(), (y + gap/2).toInt(), (x + pipeBitmap.width).toInt(), screenHeight)
    }

    fun draw(canvas: Canvas) {
        // Tubo superior (invertido)
        canvas.drawBitmap(
            pipeBitmap,
            null,
            getTopPipe(),
            null
        )

        // Tubo inferior
        canvas.drawBitmap(
            pipeBitmap,
            null,
            getBottomPipe(),
            null
        )
    }
}