package com.example.tuxfly

import android.content.Context
import android.graphics.*
import android.media.*
import android.view.*

class GameView(context: Context) : SurfaceView(context), SurfaceHolder.Callback {
    private val thread: GameThread
    private val tuxFrames = Array(4) {
        BitmapFactory.decodeResource(resources,
            when(it) {
                0 -> R.drawable.tux_frame1
                1 -> R.drawable.tux_frame2
                2 -> R.drawable.tux_frame3
                else -> R.drawable.tux_frame4
            }
        )
    }
    private var frameIndex = 0
    private var frameCounter = 0

    // Tux properties
    private var tuxX = 200f
    private var tuxY = 500f
    private var tuxVelocity = 0f
    private val gravity = 1.2f
    private val jumpForce = -25f

    // Game elements
    private val obstacles = mutableListOf<Obstacle>()
    private lateinit var pipeBitmap: Bitmap
    private var score = 0
    private val scorePaint = Paint().apply {
        color = Color.WHITE
        textSize = 80f
        typeface = Typeface.DEFAULT_BOLD
    }
    private var isGameOver = false

    // Audio
    private val soundPool: SoundPool
    private val soundJump: Int
    private val soundCrash: Int
    private val mediaPlayer: MediaPlayer

    init {
        holder.addCallback(this)
        thread = GameThread(holder, this)

        // Carga de assets
        pipeBitmap = BitmapFactory.decodeResource(resources, R.drawable.pipe)

        // Configuración de audio
        soundPool = SoundPool.Builder().setMaxStreams(3).build()
        soundJump = soundPool.load(context, R.raw.boton_tuxfly, 1)
        soundCrash = soundPool.load(context, R.raw.choque_tuxfly, 1)

        mediaPlayer = MediaPlayer.create(context, R.raw.musica_fondo_tux).apply {
            isLooping = true
            start()
        }

        isFocusable = true
    }

    // ... (Los métodos surfaceCreated/destroyed/changed se mantienen igual que antes)

    override fun onTouchEvent(event: MotionEvent?): Boolean {
        if (event?.action == MotionEvent.ACTION_DOWN) {
            if (!isGameOver) {
                tuxVelocity = jumpForce
                soundPool.play(soundJump, 1f, 1f, 0, 0, 1f)
            } else {
                // Reiniciar juego
                resetGame()
            }
        }
        return true
    }

    private fun resetGame() {
        tuxY = 500f
        tuxVelocity = 0f
        obstacles.clear()
        score = 0
        isGameOver = false
        frameCounter = 0
    }

    fun update() {
        if (isGameOver) return

        // Física de Tux
        tuxVelocity += gravity
        tuxY += tuxVelocity

        // Animación
        frameCounter++
        if (frameCounter >= 5) {
            frameIndex = (frameIndex + 1) % tuxFrames.size
            frameCounter = 0
        }

        // Generación de obstáculos
        if (frameCounter % 90 == 0) {
            obstacles.add(Obstacle(width, height, pipeBitmap))
        }

        // Actualizar obstáculos
        val iterator = obstacles.iterator()
        while (iterator.hasNext()) {
            val obs = iterator.next()
            obs.update()

            // Colisiones
            val tuxRect = RectF(tuxX, tuxY, tuxX + tuxFrames[0].width, tuxY + tuxFrames[0].height)
            if (tuxRect.intersect(obs.getTopPipe().toRectF()) ||
                tuxRect.intersect(obs.getBottomPipe().toRectF())) {
                isGameOver = true
                soundPool.play(soundCrash, 1f, 1f, 0, 0, 1f)
            }

            // Puntuación
            if (!obs.isScored && obs.x + pipeBitmap.width < tuxX) {
                score++
                obs.isScored = true
            }

            // Eliminar obstáculos fuera de pantalla
            if (obs.isOffScreen()) iterator.remove()
        }

        // Límites de pantalla
        if (tuxY < 0) tuxY = 0f
        if (tuxY > height - tuxFrames[0].height) {
            tuxY = height - tuxFrames[0].height.toFloat()
            isGameOver = true
        }
    }

    override fun draw(canvas: Canvas?) {
        super.draw(canvas)
        canvas?.apply {
            // Fondo
            drawColor(Color.parseColor("#87CEEB"))  // Cielo azul

            // Menú inicial
            if (score == 0 && !isGameOver && tuxY == 500f) {
                val logo = BitmapFactory.decodeResource(resources, R.drawable.logo_ufro)
                drawBitmap(logo, (width - logo.width) / 2f, 200f, null)
                drawText("Toca para empezar", width / 2f - 150f, 500f, scorePaint)
                return
            }

            // Obstáculos
            obstacles.forEach { it.draw(this) }

            // Tux
            drawBitmap(tuxFrames[frameIndex], tuxX, tuxY, null)

            // Puntuación
            drawText("Puntos: $score", 50f, 100f, scorePaint)

            // Game Over
            if (isGameOver) {
                drawText("GAME OVER", width / 2f - 150f, height / 2f, scorePaint)
                drawText("Toca para reiniciar", width / 2f - 200f, height / 2f + 100f, scorePaint)
            }
        }
    }
}