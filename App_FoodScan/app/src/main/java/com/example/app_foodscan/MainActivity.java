package com.example.app_foodscan;

import android.content.Intent;
import android.os.Bundle;
import android.view.View;
import android.widget.Button;

import androidx.appcompat.app.AppCompatActivity;
import androidx.appcompat.widget.Toolbar; // Importar Toolbar

public class MainActivity extends AppCompatActivity {

    private Button btnAddFood;
    private Button btnHistory;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);

        // --- Configuración de la Toolbar (NUEVO) ---
        Toolbar toolbar = findViewById(R.id.toolbar);
        setSupportActionBar(toolbar);
        if (getSupportActionBar() != null) {
            // En MainActivity, no establecemos un título de acción bar estándar
            // porque usaremos un TextView personalizado dentro de la Toolbar para el logo de texto.
            getSupportActionBar().setDisplayShowTitleEnabled(false); // Deshabilita el título por defecto
            getSupportActionBar().setDisplayHomeAsUpEnabled(false); // Asegúrate de que el botón de volver no aparezca en la pantalla principal
        }
        // --- Fin Configuración de la Toolbar ---

        btnAddFood = findViewById(R.id.btnAddFood);
        btnHistory = findViewById(R.id.btnHistory);

        btnAddFood.setOnClickListener(v -> {
            Intent intent = new Intent(MainActivity.this, AddFoodActivity.class);
            startActivity(intent);
        });

        btnHistory.setOnClickListener(v -> {
            Intent intent = new Intent(MainActivity.this, HistoryActivity.class);
            startActivity(intent);
        });
    }
}