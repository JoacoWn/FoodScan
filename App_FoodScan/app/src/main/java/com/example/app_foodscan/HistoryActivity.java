package com.example.app_foodscan;

import android.app.AlertDialog;
import android.app.DatePickerDialog;
import android.content.Context;
import android.content.SharedPreferences;
import android.os.Bundle;
import android.view.MenuItem;
import android.view.View;
import android.widget.Button;
import android.widget.EditText;
import android.widget.ImageButton;
import android.widget.ProgressBar;
import android.widget.TextView;
import android.widget.Toast;

import androidx.annotation.NonNull;
import androidx.appcompat.app.AppCompatActivity;
import androidx.appcompat.widget.Toolbar;
import androidx.core.content.ContextCompat;
import androidx.recyclerview.widget.LinearLayoutManager;
import androidx.recyclerview.widget.RecyclerView;

import com.example.app_foodscan.adapter.MealSectionAdapter;
import com.example.app_foodscan.model.DailyMealSummary;
import com.example.app_foodscan.model.FoodHistoryItem;
import com.example.app_foodscan.network.ApiClient;
import com.example.app_foodscan.network.ApiService;

import java.text.ParseException;
import java.text.SimpleDateFormat;
import java.util.ArrayList;
import java.util.Calendar;
import java.util.Collections;
import java.util.Comparator;
import java.util.Date;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Locale;
import java.util.Map;
import java.util.TimeZone;

import retrofit2.Call;
import retrofit2.Callback;
import retrofit2.Response;

// Implementa la interfaz del listener que ahora está en MealSectionAdapter
public class HistoryActivity extends AppCompatActivity implements MealSectionAdapter.OnFoodItemDeleteListener {

    private TextView tvCaloriesConsumed, tvCaloriesGoal, tvCaloriesDiff;
    private ProgressBar pbCalories, pbProteins, pbFats, pbCarbs;
    private TextView tvProteinsSummary, tvFatsSummary, tvCarbsSummary;
    private Button btnSetGoals;

    private ImageButton btnPrevDay, btnNextDay;
    private TextView tvCurrentDate;

    private RecyclerView rvMealSections;
    private MealSectionAdapter mealSectionAdapter;
    private TextView tvNoHistoryMessage;
    private ProgressBar historyProgressBar;

    private ApiService apiService;

    private Calendar currentSelectedDate;

    private float dailyCaloriesGoal = 2000;
    private float dailyProteinsGoal = 100;
    private float dailyFatsGoal = 70;
    private float dailyCarbsGoal = 250;

    private SharedPreferences sharedPreferences;
    private static final String PREFS_NAME = "FoodScanGoals";
    private static final String KEY_CALORIES_GOAL = "calories_goal";
    private static final String KEY_PROTEINS_GOAL = "proteins_goal";
    private static final String KEY_FATS_GOAL = "fats_goal";
    private static final String KEY_CARBS_GOAL = "carbs_goal";

    private SimpleDateFormat uiDateFormat;
    private SimpleDateFormat backendCompareDateFormat;
    private SimpleDateFormat backendIsoParseFormat;


    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_history);

        Toolbar toolbar = findViewById(R.id.toolbar);
        setSupportActionBar(toolbar);
        if (getSupportActionBar() != null) {
            getSupportActionBar().setTitle("Mi Historial Nutricional");
            getSupportActionBar().setDisplayHomeAsUpEnabled(true);
        }

        tvCaloriesConsumed = findViewById(R.id.tv_calories_consumed);
        tvCaloriesGoal = findViewById(R.id.tv_calories_goal);
        tvCaloriesDiff = findViewById(R.id.tv_calories_diff);
        pbCalories = findViewById(R.id.pb_calories);
        pbProteins = findViewById(R.id.pb_proteins);
        pbFats = findViewById(R.id.pb_fats);
        pbCarbs = findViewById(R.id.pb_carbs);
        tvProteinsSummary = findViewById(R.id.tv_proteins_summary);
        tvFatsSummary = findViewById(R.id.tv_fats_summary);
        tvCarbsSummary = findViewById(R.id.tv_carbs_summary);
        btnSetGoals = findViewById(R.id.btn_set_goals);

        btnPrevDay = findViewById(R.id.btn_prev_day);
        btnNextDay = findViewById(R.id.btn_next_day);
        tvCurrentDate = findViewById(R.id.tv_current_date);

        rvMealSections = findViewById(R.id.rv_meal_sections);
        tvNoHistoryMessage = findViewById(R.id.tvNoHistoryMessage);
        historyProgressBar = findViewById(R.id.historyProgressBar);

        apiService = ApiClient.getClient();

        sharedPreferences = getSharedPreferences(PREFS_NAME, Context.MODE_PRIVATE);
        loadDailyGoals();

        currentSelectedDate = Calendar.getInstance();

        mealSectionAdapter = new MealSectionAdapter(new ArrayList<>());
        rvMealSections.setLayoutManager(new LinearLayoutManager(this));
        rvMealSections.setAdapter(mealSectionAdapter);

        // ¡IMPORTANTE! Asignar el listener al adaptador
        // La referencia al listener es ahora directa a MealSectionAdapter.OnFoodItemDeleteListener
        mealSectionAdapter.setOnFoodItemDeleteListener(this); // 'this' porque HistoryActivity implementa el listener

        uiDateFormat = new SimpleDateFormat("EEEE, dd 'de' MMMM", new Locale("es", "ES"));
        backendCompareDateFormat = new SimpleDateFormat("yyyy-MM-dd", Locale.getDefault());
        backendIsoParseFormat = new SimpleDateFormat("yyyy-MM-dd'T'HH:mm:ss.SSSSSS", Locale.getDefault());
        backendIsoParseFormat.setTimeZone(TimeZone.getTimeZone("UTC"));

        btnPrevDay.setOnClickListener(v -> changeDay(-1));
        btnNextDay.setOnClickListener(v -> changeDay(1));
        tvCurrentDate.setOnClickListener(v -> showDatePicker());
        btnSetGoals.setOnClickListener(v -> showGoalSettingDialog());

        updateDateDisplay();
        loadFoodHistoryForSelectedDate();
    }

    @Override
    public boolean onOptionsItemSelected(@NonNull MenuItem item) {
        if (item.getItemId() == android.R.id.home) {
            onBackPressed();
            return true;
        }
        return super.onOptionsItemSelected(item);
    }

    private void changeDay(int days) {
        currentSelectedDate.add(Calendar.DAY_OF_YEAR, days);
        updateDateDisplay();
        loadFoodHistoryForSelectedDate();
    }

    private void showDatePicker() {
        int year = currentSelectedDate.get(Calendar.YEAR);
        int month = currentSelectedDate.get(Calendar.MONTH);
        int day = currentSelectedDate.get(Calendar.DAY_OF_MONTH);

        DatePickerDialog datePickerDialog = new DatePickerDialog(this,
                (view, selectedYear, selectedMonth, selectedDay) -> {
                    currentSelectedDate.set(selectedYear, selectedMonth, selectedDay);
                    updateDateDisplay();
                    loadFoodHistoryForSelectedDate();
                }, year, month, day);
        datePickerDialog.show();
    }

    private void updateDateDisplay() {
        tvCurrentDate.setText(uiDateFormat.format(currentSelectedDate.getTime()));
    }

    private void loadDailyGoals() {
        dailyCaloriesGoal = sharedPreferences.getFloat(KEY_CALORIES_GOAL, 2000);
        dailyProteinsGoal = sharedPreferences.getFloat(KEY_PROTEINS_GOAL, 100);
        dailyFatsGoal = sharedPreferences.getFloat(KEY_FATS_GOAL, 70);
        dailyCarbsGoal = sharedPreferences.getFloat(KEY_CARBS_GOAL, 250);
        updateGoalDisplays();
    }

    private void saveDailyGoals() {
        SharedPreferences.Editor editor = sharedPreferences.edit();
        editor.putFloat(KEY_CALORIES_GOAL, dailyCaloriesGoal);
        editor.putFloat(KEY_PROTEINS_GOAL, dailyProteinsGoal);
        editor.putFloat(KEY_FATS_GOAL, dailyFatsGoal);
        editor.putFloat(KEY_CARBS_GOAL, dailyCarbsGoal);
        editor.apply();
        Toast.makeText(this, getString(R.string.toast_goals_saved), Toast.LENGTH_SHORT).show();
        updateGoalDisplays();
        loadFoodHistoryForSelectedDate();
    }

    private void showGoalSettingDialog() {
        AlertDialog.Builder builder = new AlertDialog.Builder(this);
        builder.setTitle(getString(R.string.dialog_set_goals_title));

        View dialogView = getLayoutInflater().inflate(R.layout.dialog_set_goals, null);
        builder.setView(dialogView);

        final EditText etCalories = dialogView.findViewById(R.id.et_goal_calories);
        final EditText etProteins = dialogView.findViewById(R.id.et_goal_proteins);
        final EditText etFats = dialogView.findViewById(R.id.et_goal_fats);
        final EditText etCarbs = dialogView.findViewById(R.id.et_goal_carbs);

        etCalories.setText(String.valueOf((int) dailyCaloriesGoal));
        etProteins.setText(String.valueOf((int) dailyProteinsGoal));
        etFats.setText(String.valueOf((int) dailyFatsGoal));
        etCarbs.setText(String.valueOf((int) dailyCarbsGoal));

        builder.setPositiveButton(getString(R.string.button_save_goals), (dialog, which) -> {
            try {
                dailyCaloriesGoal = Float.parseFloat(etCalories.getText().toString());
                dailyProteinsGoal = Float.parseFloat(etProteins.getText().toString());
                dailyFatsGoal = Float.parseFloat(etFats.getText().toString());
                dailyCarbsGoal = Float.parseFloat(etCarbs.getText().toString());
                saveDailyGoals();
            } catch (NumberFormatException e) {
                Toast.makeText(HistoryActivity.this, getString(R.string.toast_invalid_number_input), Toast.LENGTH_SHORT).show();
            }
        });
        builder.setNegativeButton(getString(R.string.button_cancel_goals), (dialog, which) -> dialog.cancel());

        builder.show();
    }

    private void updateGoalDisplays() {
        tvCaloriesGoal.setText(String.format(Locale.getDefault(), "%.0f", dailyCaloriesGoal));
    }

    private void loadFoodHistoryForSelectedDate() {
        historyProgressBar.setVisibility(View.VISIBLE);
        tvNoHistoryMessage.setVisibility(View.GONE);
        rvMealSections.setVisibility(View.GONE);

        apiService.getFoodHistory().enqueue(new Callback<List<FoodHistoryItem>>() {
            @Override
            public void onResponse(Call<List<FoodHistoryItem>> call, Response<List<FoodHistoryItem>> response) {
                historyProgressBar.setVisibility(View.GONE);

                if (response.isSuccessful() && response.body() != null) {
                    List<FoodHistoryItem> fetchedHistory = response.body();
                    processAndDisplayHistory(fetchedHistory);
                } else {
                    String errorMessage = getString(R.string.error_loading_history) + ": " + response.code();
                    try {
                        if (response.errorBody() != null) {
                            errorMessage += "\n" + response.errorBody().string();
                        }
                    } catch (Exception e) {
                        e.printStackTrace();
                    }
                    Toast.makeText(HistoryActivity.this, errorMessage, Toast.LENGTH_LONG).show();
                    tvNoHistoryMessage.setText(getString(R.string.error_loading_history));
                    tvNoHistoryMessage.setVisibility(View.VISIBLE);
                }
            }

            @Override
            public void onFailure(Call<List<FoodHistoryItem>> call, Throwable t) {
                historyProgressBar.setVisibility(View.GONE);
                Toast.makeText(HistoryActivity.this, getString(R.string.connection_error_history) + ": " + t.getMessage(), Toast.LENGTH_LONG).show();
                t.printStackTrace();
                tvNoHistoryMessage.setText(getString(R.string.connection_error_history));
                tvNoHistoryMessage.setVisibility(View.VISIBLE);
            }
        });
    }

    private void processAndDisplayHistory(List<FoodHistoryItem> allHistoryItems) {
        String selectedDateString = backendCompareDateFormat.format(currentSelectedDate.getTime());

        List<FoodHistoryItem> filteredItemsForSelectedDate = new ArrayList<>();
        for (FoodHistoryItem item : allHistoryItems) {
            try {
                Date itemDate = backendIsoParseFormat.parse(item.getTimestamp());
                String itemDateString = backendCompareDateFormat.format(itemDate);

                if (itemDateString.equals(selectedDateString)) {
                    filteredItemsForSelectedDate.add(item);
                }
            } catch (ParseException e) {
                e.printStackTrace();
            }
        }

        Collections.sort(filteredItemsForSelectedDate, Comparator.comparing(FoodHistoryItem::getTimestamp));

        DailyMealSummary dailySummary = new DailyMealSummary(selectedDateString);
        LinkedHashMap<String, DailyMealSummary.MealSection> mealSectionsMap = new LinkedHashMap<>();

        String[] predefinedMealTypes = {"desayuno", "almuerzo", "merienda", "cena", "snack", "otro"};
        for (String type : predefinedMealTypes) {
            String capitalizedType = type.substring(0, 1).toUpperCase(Locale.getDefault()) + type.substring(1);
            mealSectionsMap.put(type, new DailyMealSummary.MealSection(capitalizedType));
        }

        for (FoodHistoryItem item : filteredItemsForSelectedDate) {
            dailySummary.setTotalDailyCalories(dailySummary.getTotalDailyCalories() + item.getTotalCalorias());
            dailySummary.setTotalDailyProteins(dailySummary.getTotalDailyProteins() + item.getTotalProteinas());
            dailySummary.setTotalDailyFats(dailySummary.getTotalDailyFats() + item.getTotalGrasas());
            dailySummary.setTotalDailyCarbs(dailySummary.getTotalDailyCarbs() + item.getTotalCarbohidratos());

            String mealType = item.getMealType().toLowerCase(Locale.getDefault());
            if (!mealSectionsMap.containsKey(mealType)) {
                String capitalizedMealType = mealType.substring(0, 1).toUpperCase(Locale.getDefault()) + mealType.substring(1);
                mealSectionsMap.put(mealType, new DailyMealSummary.MealSection(capitalizedMealType));
            }
            mealSectionsMap.get(mealType).addFoodItem(item);
        }

        List<DailyMealSummary.MealSection> finalMealSections = new ArrayList<>();
        for (String typeKey : predefinedMealTypes) {
            DailyMealSummary.MealSection section = mealSectionsMap.get(typeKey);
            if (section != null && !section.getFoodItems().isEmpty()) {
                finalMealSections.add(section);
            }
        }
        for (Map.Entry<String, DailyMealSummary.MealSection> entry : mealSectionsMap.entrySet()) {
            if (!predefinedMealTypesContain(predefinedMealTypes, entry.getKey()) && !entry.getValue().getFoodItems().isEmpty()) {
                finalMealSections.add(entry.getValue());
            }
        }


        dailySummary.setMealSections(finalMealSections);

        updateDailySummaryUI(dailySummary);

        if (!finalMealSections.isEmpty()) {
            mealSectionAdapter.setMealSections(finalMealSections);
            rvMealSections.setVisibility(View.VISIBLE);
            tvNoHistoryMessage.setVisibility(View.GONE);
        } else {
            mealSectionAdapter.setMealSections(new ArrayList<>());
            tvNoHistoryMessage.setText(getString(R.string.no_history_for_this_day));
            tvNoHistoryMessage.setVisibility(View.VISIBLE);
            rvMealSections.setVisibility(View.GONE);
        }
    }

    private void updateDailySummaryUI(DailyMealSummary summary) {
        tvCaloriesConsumed.setText(String.format(Locale.getDefault(), "%.0f", summary.getTotalDailyCalories()));
        tvCaloriesGoal.setText(String.format(Locale.getDefault(), "%.0f", dailyCaloriesGoal));

        float remainingCalories = dailyCaloriesGoal - summary.getTotalDailyCalories();
        if (remainingCalories >= 0) {
            tvCaloriesDiff.setText(String.format(Locale.getDefault(), "+%.0f", remainingCalories));
            tvCaloriesDiff.setTextColor(ContextCompat.getColor(this, R.color.mellowYellow));
        } else {
            tvCaloriesDiff.setText(String.format(Locale.getDefault(), "%.0f", remainingCalories));
            tvCaloriesDiff.setTextColor(ContextCompat.getColor(this, android.R.color.holo_red_light));
        }

        int caloriesProgress = (int) ((summary.getTotalDailyCalories() / dailyCaloriesGoal) * 100);
        pbCalories.setProgress(Math.min(caloriesProgress, 100));

        tvProteinsSummary.setText(String.format(Locale.getDefault(), "%.1fg / %.1fg", summary.getTotalDailyProteins(), dailyProteinsGoal));
        int proteinsProgress = (int) ((summary.getTotalDailyProteins() / dailyProteinsGoal) * 100);
        pbProteins.setProgress(Math.min(proteinsProgress, 100));

        tvFatsSummary.setText(String.format(Locale.getDefault(), "%.1fg / %.1fg", summary.getTotalDailyFats(), dailyFatsGoal));
        int fatsProgress = (int) ((summary.getTotalDailyFats() / dailyFatsGoal) * 100);
        pbFats.setProgress(Math.min(fatsProgress, 100));

        tvCarbsSummary.setText(String.format(Locale.getDefault(), "%.1fg / %.1fg", summary.getTotalDailyCarbs(), dailyCarbsGoal));
        int carbsProgress = (int) ((summary.getTotalDailyCarbs() / dailyCarbsGoal) * 100);
        pbCarbs.setProgress(Math.min(carbsProgress, 100));
    }

    private boolean predefinedMealTypesContain(String[] predefinedTypes, String mealType) {
        for (String type : predefinedTypes) {
            if (type.equalsIgnoreCase(mealType)) {
                return true;
            }
        }
        return false;
    }

    // --- NUEVA IMPLEMENTACIÓN DEL LISTENER DE ELIMINACIÓN ---
    // Ahora implementa la interfaz directamente de MealSectionAdapter
    @Override
    public void onFoodItemDelete(FoodHistoryItem itemToDelete) {
        new AlertDialog.Builder(this)
                .setTitle(getString(R.string.dialog_delete_item_title))
                .setMessage(getString(R.string.dialog_delete_item_message, itemToDelete.getNombreGeneralComida()))
                .setPositiveButton(getString(R.string.button_delete), (dialog, which) -> {
                    // Si el usuario confirma, llamamos al método de eliminación de la API
                    deleteFoodHistoryItem(itemToDelete.getId());
                })
                .setNegativeButton(getString(R.string.button_cancel_goals), null)
                .show();
    }

    private void deleteFoodHistoryItem(String itemId) {
        // Asegúrate de que itemId no sea nulo antes de hacer la llamada
        if (itemId == null || itemId.isEmpty()) {
            Toast.makeText(this, "Error: ID de elemento no válido para eliminar.", Toast.LENGTH_SHORT).show();
            return;
        }

        apiService.deleteFoodHistoryItem(itemId).enqueue(new Callback<Void>() {
            @Override
            public void onResponse(Call<Void> call, Response<Void> response) {
                if (response.isSuccessful()) {
                    Toast.makeText(HistoryActivity.this, getString(R.string.toast_item_deleted_success), Toast.LENGTH_SHORT).show();
                    // Vuelve a cargar el historial para actualizar la UI y los resúmenes
                    loadFoodHistoryForSelectedDate();
                } else {
                    String errorMessage = getString(R.string.error_deleting_item) + ": " + response.code();
                    try {
                        if (response.errorBody() != null) {
                            errorMessage += "\n" + response.errorBody().string();
                        }
                    } catch (Exception e) {
                        e.printStackTrace();
                    }
                    Toast.makeText(HistoryActivity.this, errorMessage, Toast.LENGTH_LONG).show();
                }
            }

            @Override
            public void onFailure(Call<Void> call, Throwable t) {
                Toast.makeText(HistoryActivity.this, getString(R.string.connection_error_delete_item) + ": " + t.getMessage(), Toast.LENGTH_LONG).show();
                t.printStackTrace();
            }
        });
    }
    // --- FIN NUEVA IMPLEMENTACIÓN ---
}