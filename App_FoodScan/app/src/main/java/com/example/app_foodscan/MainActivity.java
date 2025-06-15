package com.example.app_foodscan;

import android.content.Intent;
import android.os.Bundle;
import android.view.View;
import android.widget.Button;
import androidx.appcompat.app.AppCompatActivity;
import androidx.appcompat.widget.Toolbar; // Importar Toolbar

public class MainActivity extends AppCompatActivity {

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);

        // --- Configuración de la Toolbar ---
        Toolbar toolbar = findViewById(R.id.toolbar);
        setSupportActionBar(toolbar);
        if (getSupportActionBar() != null) {
            getSupportActionBar().setTitle(R.string.app_name); // Establece el título "FoodScan"
            // Si quieres que no haya flecha de vuelta en la pantalla principal
            getSupportActionBar().setDisplayHomeAsUpEnabled(false);
        }
        // --- Fin Configuración de la Toolbar ---

        Button btnAddFood = findViewById(R.id.btnAddFood);
        Button btnViewHistory = findViewById(R.id.btnViewHistory);
        Button btnExit = findViewById(R.id.btnExit); // Asegúrate de que este botón exista en tu XML si lo usas

        btnAddFood.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                Intent intent = new Intent(MainActivity.this, AddFoodActivity.class);
                startActivity(intent);
            }
        });

        btnViewHistory.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                Intent intent = new Intent(MainActivity.this, HistoryActivity.class);
                startActivity(intent);
            }
        });

        btnExit.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                finishAffinity(); // Cierra todas las actividades y sale de la aplicación
            }
        });
    }
}