package com.example.tuxfly

import android.graphics.Canvas
import android.view.SurfaceHolder

class GameThread(
    private val surfaceHolder: SurfaceHolder,
    private val gameView: GameView
) : Thread() {

    private var running = false
    private val targetFPS = 60

    fun setRunning(isRunning: Boolean) {
        running = isRunning
    }

    override fun run() {
        var canvas: Canvas?

        while (running) {
            val startTime = System.nanoTime()
            canvas = null

            try {
                canvas = surfaceHolder.lockCanvas()
                synchronized(surfaceHolder) {
                    gameView.update()
                    gameView.draw(canvas)
                }
            } finally {
                if (canvas != null) {
                    surfaceHolder.unlockCanvasAndPost(canvas)
                }
            }

            val timeMillis = (System.nanoTime() - startTime) / 1_000_000
            val waitTime = (1000 / targetFPS - timeMillis).coerceAtLeast(0)

            try {
                sleep(waitTime)
            } catch (e: InterruptedException) {
                e.printStackTrace()
            }
        }
    }
}
