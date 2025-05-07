package com.example.sensores

import android.app.Activity
import android.media.MediaPlayer
import android.os.Bundle
import android.widget.Button
import android.widget.TextView
import android.hardware.Sensor
import android.hardware.SensorEvent
import android.hardware.SensorEventListener
import android.hardware.SensorManager
import android.view.WindowManager

class MainActivity : Activity(), SensorEventListener {

    private lateinit var sensorManager: SensorManager
    private var accelerometer: Sensor? = null
    private var gyroscope: Sensor? = null

    private lateinit var statusText: TextView
    private lateinit var orientationText: TextView
    private lateinit var coordsText: TextView
    private lateinit var resetButton: Button
    private lateinit var ballView: BallView

    private var stablePlayer: MediaPlayer? = null
    private var movePlayer: MediaPlayer? = null

    private var isStable = true

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        window.addFlags(WindowManager.LayoutParams.FLAG_KEEP_SCREEN_ON)
        setContentView(R.layout.activity_main)

        statusText = findViewById(R.id.statusText)
        orientationText = findViewById(R.id.orientationText)
        coordsText = findViewById(R.id.coordsText)
        resetButton = findViewById(R.id.resetButton)
        ballView = findViewById(R.id.ballView)

        stablePlayer = MediaPlayer.create(this, R.raw.estable)
        movePlayer = MediaPlayer.create(this, R.raw.movimiento)

        sensorManager = getSystemService(SENSOR_SERVICE) as SensorManager
        accelerometer = sensorManager.getDefaultSensor(Sensor.TYPE_ACCELEROMETER)
        gyroscope = sensorManager.getDefaultSensor(Sensor.TYPE_GYROSCOPE)

        resetButton.setOnClickListener {
            isStable = true
            statusText.text = "Estable"
            movePlayer?.pause()
            movePlayer?.seekTo(0)
        }
    }

    override fun onResume() {
        super.onResume()
        accelerometer?.also {
            sensorManager.registerListener(this, it, SensorManager.SENSOR_DELAY_GAME)
        }
        gyroscope?.also {
            sensorManager.registerListener(this, it, SensorManager.SENSOR_DELAY_GAME)
        }
    }

    override fun onPause() {
        super.onPause()
        sensorManager.unregisterListener(this)
    }

    override fun onSensorChanged(event: SensorEvent?) {
        event?.let {
            if (it.sensor.type == Sensor.TYPE_ACCELEROMETER) {
                val x = it.values[0]
                val y = it.values[1]
                val z = it.values[2]

                // Mostrar coordenadas
                coordsText.text = "X: %.2f, Y: %.2f, Z: %.2f".format(x, y, z)

                // Mover bola visual
                ballView.updatePosition(-x, y)

                val isNowStable = z > 9 && Math.abs(x) < 1 && Math.abs(y) < 1

                if (isNowStable && !isStable) {
                    stablePlayer?.start()
                    movePlayer?.pause()
                    movePlayer?.seekTo(0)
                    statusText.text = "Estable"
                    isStable = true
                } else if (!isNowStable && isStable) {
                    movePlayer?.start()
                    statusText.text = "En Movimiento"
                    isStable = false
                }

                orientationText.text = when {
                    Math.abs(x) > Math.abs(y) -> if (x > 0) "Horizontal Izquierda" else "Horizontal Derecha"
                    else -> if (y > 0) "Vertical Arriba" else "Vertical Abajo"
                }
            }

            if (it.sensor.type == Sensor.TYPE_GYROSCOPE) {
                val rotation = Math.abs(it.values[0]) + Math.abs(it.values[1]) + Math.abs(it.values[2])
                if (rotation > 2.0f && isStable) {
                    movePlayer?.start()
                    statusText.text = "En Movimiento"
                    isStable = false
                }
            }
        }
    }

    override fun onAccuracyChanged(sensor: Sensor?, accuracy: Int) {}
}
