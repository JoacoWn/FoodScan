package com.example.app_foodscan;

import android.os.Bundle;
import android.view.MenuItem; // Importar MenuItem para manejar el botón de vuelta
import android.view.View;
import android.widget.ProgressBar;
import android.widget.TextView;
import android.widget.Toast;

import androidx.annotation.NonNull;
import androidx.appcompat.app.AppCompatActivity;
import androidx.appcompat.widget.Toolbar; // Importar Toolbar
import androidx.recyclerview.widget.LinearLayoutManager;
import androidx.recyclerview.widget.RecyclerView;

import com.example.app_foodscan.adapter.HistoryAdapter;
import com.example.app_foodscan.model.FoodHistoryItem;
import com.example.app_foodscan.network.ApiClient;
import com.example.app_foodscan.network.ApiService;

import java.util.ArrayList;
import java.util.List;

import retrofit2.Call;
import retrofit2.Callback;
import retrofit2.Response;

public class HistoryActivity extends AppCompatActivity {

    private RecyclerView recyclerViewHistory;
    private HistoryAdapter historyAdapter;
    private List<FoodHistoryItem> historyList; // Esta lista se gestiona internamente por el adaptador ahora
    private ProgressBar historyProgressBar;
    private TextView tvNoHistoryMessage;
    private ApiService apiService;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_history);

        // --- Configuración de la Toolbar (NUEVO) ---
        Toolbar toolbar = findViewById(R.id.toolbar);
        setSupportActionBar(toolbar);
        if (getSupportActionBar() != null) {
            getSupportActionBar().setTitle("Historial de Comidas"); // Título específico para esta Activity
            getSupportActionBar().setDisplayHomeAsUpEnabled(true); // Habilita el botón de volver (flecha)
        }
        // --- Fin Configuración de la Toolbar ---

        recyclerViewHistory = findViewById(R.id.recyclerViewHistory);
        historyProgressBar = findViewById(R.id.historyProgressBar);
        tvNoHistoryMessage = findViewById(R.id.tvNoHistoryMessage);

        apiService = ApiClient.getClient().create(ApiService.class);

        // Configurar RecyclerView
        historyList = new ArrayList<>(); // Aunque se pasa al adaptador, el adaptador lo gestiona.
        historyAdapter = new HistoryAdapter(historyList); // Pasa la lista inicial vacía
        recyclerViewHistory.setLayoutManager(new LinearLayoutManager(this));
        recyclerViewHistory.setAdapter(historyAdapter);

        // Cargar el historial al iniciar la actividad
        loadFoodHistory();
    }

    // --- Método para manejar el clic en el botón de vuelta de la Toolbar (NUEVO) ---
    @Override
    public boolean onOptionsItemSelected(@NonNull MenuItem item) {
        if (item.getItemId() == android.R.id.home) {
            onBackPressed(); // Simula el comportamiento del botón Atrás
            return true;
        }
        return super.onOptionsItemSelected(item);
    }
    // --- Fin Método para manejar el clic en el botón de vuelta de la Toolbar ---

    private void loadFoodHistory() {
        historyProgressBar.setVisibility(View.VISIBLE); // Mostrar ProgressBar
        tvNoHistoryMessage.setVisibility(View.GONE); // Ocultar mensaje de no historial
        recyclerViewHistory.setVisibility(View.GONE); // Ocultar RecyclerView durante la carga

        apiService.getFoodHistory().enqueue(new Callback<List<FoodHistoryItem>>() {
            @Override
            public void onResponse(Call<List<FoodHistoryItem>> call, Response<List<FoodHistoryItem>> response) {
                historyProgressBar.setVisibility(View.GONE); // Ocultar ProgressBar

                if (response.isSuccessful() && response.body() != null) {
                    List<FoodHistoryItem> fetchedHistory = response.body();
                    if (!fetchedHistory.isEmpty()) {
                        historyAdapter.setHistoryList(fetchedHistory); // Actualiza los datos en el adaptador
                        recyclerViewHistory.setVisibility(View.VISIBLE); // Mostrar RecyclerView
                        tvNoHistoryMessage.setVisibility(View.GONE); // Asegurarse de que el mensaje de no historial esté oculto
                    } else {
                        tvNoHistoryMessage.setText(R.string.no_history_yet); // Usa la cadena de recursos
                        tvNoHistoryMessage.setVisibility(View.VISIBLE); // Mostrar mensaje de no historial
                        recyclerViewHistory.setVisibility(View.GONE); // Ocultar RecyclerView
                    }
                } else {
                    String errorMessage = "Error al cargar historial: " + response.code();
                    try {
                        if (response.errorBody() != null) {
                            errorMessage += "\n" + response.errorBody().string();
                        }
                    } catch (Exception e) {
                        e.printStackTrace();
                    }
                    Toast.makeText(HistoryActivity.this, errorMessage, Toast.LENGTH_LONG).show();
                    tvNoHistoryMessage.setText(getString(R.string.error_loading_history)); // Mensaje de error más específico
                    tvNoHistoryMessage.setVisibility(View.VISIBLE); // Mostrar mensaje de no historial en caso de error
                }
            }

            @Override
            public void onFailure(Call<List<FoodHistoryItem>> call, Throwable t) {
                historyProgressBar.setVisibility(View.GONE); // Ocultar ProgressBar
                Toast.makeText(HistoryActivity.this, "Fallo de conexión al cargar historial: " + t.getMessage(), Toast.LENGTH_LONG).show();
                t.printStackTrace();
                tvNoHistoryMessage.setText(getString(R.string.connection_error_history)); // Usa la cadena de recursos
                tvNoHistoryMessage.setVisibility(View.VISIBLE); // Mostrar mensaje de no historial en caso de fallo de conexión
            }
        });
    }
}