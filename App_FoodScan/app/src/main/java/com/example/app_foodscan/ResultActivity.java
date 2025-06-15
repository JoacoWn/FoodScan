package com.example.app_foodscan;

import android.os.Bundle;
import android.view.MenuItem; // Importar MenuItem para el botón de vuelta
import android.view.View;
import android.widget.LinearLayout;
import android.widget.TextView;
import android.widget.Toast;
import android.graphics.Typeface;
import android.util.TypedValue; // Importar TypedValue para convertir dp a px

import androidx.annotation.NonNull;
import androidx.appcompat.app.AppCompatActivity;
import androidx.appcompat.widget.Toolbar; // Importar Toolbar
import androidx.cardview.widget.CardView; // Importar CardView
import androidx.core.content.ContextCompat;

import com.example.app_foodscan.model.FoodItem;
import com.example.app_foodscan.model.FoodResult;

import java.util.List;
import java.util.Locale; // Importar Locale para String.format

/**
 * ResultActivity muestra la información nutricional recibida desde el backend Flask.
 * Muestra un resumen total y un desglose por cada alimento identificado.
 */
public class ResultActivity extends AppCompatActivity {

    private TextView tvOverallFoodName;
    private TextView tvOverallCalories;
    private TextView tvOverallProteins;
    private TextView tvOverallFats;
    private TextView tvOverallCarbs;
    private LinearLayout foodItemsContainer;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_result);

        // --- Configuración de la Toolbar (NUEVO) ---
        Toolbar toolbar = findViewById(R.id.toolbar);
        setSupportActionBar(toolbar);
        if (getSupportActionBar() != null) {
            getSupportActionBar().setTitle("Resultados del Análisis"); // Título específico
            getSupportActionBar().setDisplayHomeAsUpEnabled(true); // Habilita el botón de volver
        }
        // --- Fin Configuración de la Toolbar ---

        // Inicializa las vistas del resumen general
        tvOverallFoodName = findViewById(R.id.tvOverallFoodName);
        tvOverallCalories = findViewById(R.id.tvOverallCalories);
        tvOverallProteins = findViewById(R.id.tvOverallProteins);
        tvOverallFats = findViewById(R.id.tvOverallFats);
        tvOverallCarbs = findViewById(R.id.tvOverallCarbs);

        // Inicializa el contenedor dinámico para los alimentos individuales
        foodItemsContainer = findViewById(R.id.food_items_container);

        // Obtiene el objeto FoodResult completo del Intent
        FoodResult result = (FoodResult) getIntent().getSerializableExtra("foodResult");

        if (result != null) {
            // Muestra el resumen general de la comida
            tvOverallFoodName.setText("Comida: " + result.getNombre());
            tvOverallCalories.setText(String.format(Locale.getDefault(), "Calorías Totales: %.2f kcal", result.getCalorias()));
            tvOverallProteins.setText(String.format(Locale.getDefault(), "Proteínas Totales: %.2f g", result.getProteinasTotales()));
            tvOverallFats.setText(String.format(Locale.getDefault(), "Grasas Totales: %.2f g", result.getGrasasTotales()));
            tvOverallCarbs.setText(String.format(Locale.getDefault(), "Carbohidratos Totales: %.2f g", result.getCarbohidratosTotales()));

            // Procesa y muestra los alimentos detallados individualmente
            List<FoodItem> detailedFoods = result.getAlimentosDetallados();
            if (detailedFoods != null && !detailedFoods.isEmpty()) {
                for (FoodItem item : detailedFoods) {
                    addFoodItemToContainer(item); // Llama a un método para añadir cada alimento
                }
            } else {
                Toast.makeText(this, "No se encontraron detalles de alimentos.", Toast.LENGTH_LONG).show();
            }
        } else {
            Toast.makeText(this, "No se recibió ningún resultado de análisis.", Toast.LENGTH_LONG).show();
        }
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


    /**
     * Método auxiliar para añadir la información detallada de un FoodItem al contenedor.
     * Crea y popula TextViews dentro de una CardView para el nombre, peso aproximado,
     * calorías, proteínas, grasas y carbohidratos.
     */
    private void addFoodItemToContainer(FoodItem item) {
        // --- Comienza la creación de CardView (NUEVO) ---
        CardView foodCard = new CardView(this);
        LinearLayout.LayoutParams cardParams = new LinearLayout.LayoutParams(
                LinearLayout.LayoutParams.MATCH_PARENT,
                LinearLayout.LayoutParams.WRAP_CONTENT
        );
        // Convertir dp a píxeles para el margen inferior
        int marginDp = 16; // Aumentado ligeramente para mejor separación
        int marginPx = (int) TypedValue.applyDimension(TypedValue.COMPLEX_UNIT_DIP, marginDp, getResources().getDisplayMetrics());
        cardParams.setMargins(0, 0, 0, marginPx);
        foodCard.setLayoutParams(cardParams);

        // Configurar propiedades de la CardView
        foodCard.setRadius(TypedValue.applyDimension(TypedValue.COMPLEX_UNIT_DIP, 12, getResources().getDisplayMetrics())); // Radio de esquina
        foodCard.setCardElevation(TypedValue.applyDimension(TypedValue.COMPLEX_UNIT_DIP, 6, getResources().getDisplayMetrics())); // Elevación de sombra
        foodCard.setCardBackgroundColor(ContextCompat.getColor(this, R.color.white)); // Color de fondo blanco

        // Layout interno para el contenido de la CardView
        LinearLayout innerLayout = new LinearLayout(this);
        innerLayout.setOrientation(LinearLayout.VERTICAL);
        // Convertir dp a píxeles para el padding interno
        int paddingDp = 16;
        int paddingPx = (int) TypedValue.applyDimension(TypedValue.COMPLEX_UNIT_DIP, paddingDp, getResources().getDisplayMetrics());
        innerLayout.setPadding(paddingPx, paddingPx, paddingPx, paddingPx);

        // Añadir el innerLayout a la CardView
        foodCard.addView(innerLayout);
        // --- Termina la creación de CardView ---


        // 1. Nombre del alimento
        TextView nameTv = new TextView(this);
        nameTv.setText(item.getNombre());
        nameTv.setTextSize(TypedValue.COMPLEX_UNIT_SP, 18); // Usar TypedValue para SP
        nameTv.setTypeface(null, Typeface.BOLD);
        nameTv.setTextColor(ContextCompat.getColor(this, R.color.charcoalText)); // Usar color de paleta
        nameTv.setPadding(0,0,0, (int) TypedValue.applyDimension(TypedValue.COMPLEX_UNIT_DIP, 4, getResources().getDisplayMetrics())); // Espacio debajo
        innerLayout.addView(nameTv); // Añadir a innerLayout

        // 2. Peso Aproximado en gramos
        TextView quantityTv = new TextView(this);
        quantityTv.setText(String.format(Locale.getDefault(), "Peso Aproximado: %.0f g", item.getCantidad_g()));
        quantityTv.setTextSize(TypedValue.COMPLEX_UNIT_SP, 16);
        quantityTv.setPadding(0,0,0, (int) TypedValue.applyDimension(TypedValue.COMPLEX_UNIT_DIP, 4, getResources().getDisplayMetrics()));
        innerLayout.addView(quantityTv);

        // 3. Calorías del item
        TextView caloriesTv = new TextView(this);
        caloriesTv.setText(String.format(Locale.getDefault(), "Calorías: %.2f kcal", item.getCalorias()));
        caloriesTv.setTextSize(TypedValue.COMPLEX_UNIT_SP, 14);
        caloriesTv.setTextColor(ContextCompat.getColor(this, R.color.deepGreen)); // Color de paleta
        innerLayout.addView(caloriesTv);

        // 4. Proteínas del item
        TextView proteinTv = new TextView(this);
        proteinTv.setText(String.format(Locale.getDefault(), "Proteínas: %.2f g", item.getProteinas()));
        proteinTv.setTextSize(TypedValue.COMPLEX_UNIT_SP, 14);
        innerLayout.addView(proteinTv);

        // 5. Grasas del item
        TextView fatsTv = new TextView(this);
        fatsTv.setText(String.format(Locale.getDefault(), "Grasas: %.2f g", item.getGrasas()));
        fatsTv.setTextSize(TypedValue.COMPLEX_UNIT_SP, 14);
        innerLayout.addView(fatsTv);

        // 6. Carbohidratos del item
        TextView carbsTv = new TextView(this);
        carbsTv.setText(String.format(Locale.getDefault(), "Carbohidratos: %.2f g", item.getCarbohidratos()));
        carbsTv.setTextSize(TypedValue.COMPLEX_UNIT_SP, 14);
        innerLayout.addView(carbsTv);

        // 7. Indicador de "Estimado por IA" (si aplica)
        if (item.isEs_estimado()) {
            TextView estimatedTv = new TextView(this);
            estimatedTv.setText("  (Estimado por IA)");
            estimatedTv.setTextSize(TypedValue.COMPLEX_UNIT_SP, 12);
            estimatedTv.setTextColor(ContextCompat.getColor(this, android.R.color.darker_gray));
            estimatedTv.setPadding(0, (int) TypedValue.applyDimension(TypedValue.COMPLEX_UNIT_DIP, 8, getResources().getDisplayMetrics()), 0, 0); // Espacio superior
            innerLayout.addView(estimatedTv);
        }

        // Añade la CardView completa de este item al contenedor principal
        foodItemsContainer.addView(foodCard);
    }

    /**
     * Método llamado cuando se hace clic en el botón "Volver" en activity_result.xml.
     * Cierra esta actividad y regresa a la actividad anterior.
     * @param view La vista que fue clicada (el botón "Volver").
     */
    public void goBack(View view) {
        finish();
    }
}