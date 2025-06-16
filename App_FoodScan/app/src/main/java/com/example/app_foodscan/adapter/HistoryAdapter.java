package com.example.app_foodscan.adapter;

import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.TextView;
import androidx.annotation.NonNull;
import androidx.recyclerview.widget.RecyclerView;

import com.example.app_foodscan.R;
import com.example.app_foodscan.model.FoodHistoryItem;
import com.example.app_foodscan.model.FoodItemDetail; // ¡IMPORTANTE: Usar FoodItemDetail!
import java.text.ParseException;
import java.text.SimpleDateFormat;
import java.util.ArrayList;
import java.util.Date;
import java.util.List;
import java.util.Locale;

/**
 * Adaptador para mostrar el historial de comidas en un RecyclerView.
 * NOTA: Este adaptador es para el diseño original de lista plana del historial.
 * Para el nuevo diseño agrupado por día/comida, se usa DailyHistoryAdapter.
 */
public class HistoryAdapter extends RecyclerView.Adapter<HistoryAdapter.HistoryViewHolder> {

    private List<FoodHistoryItem> historyList;

    public HistoryAdapter(List<FoodHistoryItem> historyList) {
        this.historyList = historyList;
        if (this.historyList == null) {
            this.historyList = new ArrayList<>(); // Asegurarse de que no sea null
        }
    }

    // Actualiza los datos del adaptador
    public void setHistoryList(List<FoodHistoryItem> newHistoryList) {
        this.historyList.clear();
        if (newHistoryList != null) {
            this.historyList.addAll(newHistoryList);
        }
        notifyDataSetChanged(); // Notifica al RecyclerView que los datos han cambiado
    }

    @NonNull
    @Override
    public HistoryViewHolder onCreateViewHolder(@NonNull ViewGroup parent, int viewType) {
        // Infla el layout para cada item del historial
        View view = LayoutInflater.from(parent.getContext()).inflate(R.layout.item_history_food, parent, false);
        return new HistoryViewHolder(view);
    }

    @Override
    public void onBindViewHolder(@NonNull HistoryViewHolder holder, int position) {
        FoodHistoryItem currentItem = historyList.get(position);
        holder.bind(currentItem);
    }

    @Override
    public int getItemCount() {
        return historyList.size();
    }

    /**
     * ViewHolder para cada item del historial.
     */
    static class HistoryViewHolder extends RecyclerView.ViewHolder {
        TextView tvHistoryTimestamp;
        TextView tvHistoryMealType;
        TextView tvHistoryFoodSummary;
        TextView tvHistoryTotalCalories;
        TextView tvHistoryTotalProteins;
        TextView tvHistoryTotalFats;
        TextView tvHistoryTotalCarbs;

        public HistoryViewHolder(@NonNull View itemView) {
            super(itemView);
            tvHistoryTimestamp = itemView.findViewById(R.id.tvHistoryTimestamp);
            tvHistoryMealType = itemView.findViewById(R.id.tvHistoryMealType);
            tvHistoryFoodSummary = itemView.findViewById(R.id.tvHistoryFoodSummary);
            tvHistoryTotalCalories = itemView.findViewById(R.id.tvHistoryTotalCalories);
            tvHistoryTotalProteins = itemView.findViewById(R.id.tvHistoryTotalProteins);
            tvHistoryTotalFats = itemView.findViewById(R.id.tvHistoryTotalFats);
            tvHistoryTotalCarbs = itemView.findViewById(R.id.tvHistoryTotalCarbs);
        }

        public void bind(FoodHistoryItem item) {
            // Formatear la fecha y hora
            String formattedTimestamp = "N/A";
            try {
                // El formato de timestamp de MongoDB puede variar. Asegúrate de que este sea el correcto.
                // Ejemplo: "2023-10-26T10:30:00.123456"
                SimpleDateFormat isoFormatter = new SimpleDateFormat("yyyy-MM-dd'T'HH:mm:ss.SSSSSS", Locale.getDefault());
                Date date = isoFormatter.parse(item.getTimestamp());
                SimpleDateFormat displayFormatter = new SimpleDateFormat("dd/MM/yyyy HH:mm", Locale.getDefault());
                formattedTimestamp = displayFormatter.format(date);
            } catch (ParseException | NullPointerException e) {
                e.printStackTrace();
                // Si hay un error, usa el timestamp tal cual viene o un mensaje de error.
                formattedTimestamp = item.getTimestamp() != null ? item.getTimestamp() : "Formato de fecha inválido";
            }
            tvHistoryTimestamp.setText(String.format("Fecha y Hora: %s", formattedTimestamp));

            // Tipo de comida
            tvHistoryMealType.setText(String.format("Tipo de Comida: %s", capitalizeFirstLetter(item.getMealType())));

            // Resumen de alimentos (ej. "Pan Blanco, Mandarina, etc.")
            StringBuilder foodSummary = new StringBuilder();
            // --- CAMBIO CLAVE AQUÍ: usar getAlimentosDetallados() y FoodItemDetail ---
            if (item.getAlimentosDetallados() != null && !item.getAlimentosDetallados().isEmpty()) {
                for (int i = 0; i < item.getAlimentosDetallados().size(); i++) {
                    FoodItemDetail food = item.getAlimentosDetallados().get(i); // ¡Ahora es FoodItemDetail!
                    foodSummary.append(food.getNombreAlimento()); // ¡Ahora es getNombreAlimento()!
                    if (i < item.getAlimentosDetallados().size() - 1) { // Usar getAlimentosDetallados().size()
                        foodSummary.append(", ");
                    }
                }
            } else {
                // Si no hay alimentos detallados, pero sí un nombre general de comida
                if (item.getNombreGeneralComida() != null && !item.getNombreGeneralComida().isEmpty()) {
                    foodSummary.append(item.getNombreGeneralComida());
                } else {
                    foodSummary.append("Sin alimentos detallados");
                }
            }
            tvHistoryFoodSummary.setText(String.format("Alimentos: %s", foodSummary.toString()));


            // Totales nutricionales
            tvHistoryTotalCalories.setText(String.format(Locale.getDefault(), "Calorías: %.2f kcal", item.getTotalCalorias()));
            tvHistoryTotalProteins.setText(String.format(Locale.getDefault(), "Proteínas: %.2f g", item.getTotalProteinas()));
            tvHistoryTotalFats.setText(String.format(Locale.getDefault(), "Grasas: %.2f g", item.getTotalGrasas()));
            tvHistoryTotalCarbs.setText(String.format(Locale.getDefault(), "Carbohidratos: %.2f g", item.getTotalCarbohidratos()));
        }

        // Método auxiliar para capitalizar la primera letra (ej. "desayuno" -> "Desayuno")
        private String capitalizeFirstLetter(String text) {
            if (text == null || text.isEmpty()) {
                return text;
            }
            return text.substring(0, 1).toUpperCase() + text.substring(1);
        }
    }
}