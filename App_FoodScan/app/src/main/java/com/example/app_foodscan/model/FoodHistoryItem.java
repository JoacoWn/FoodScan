package com.example.app_foodscan.model;

import com.google.gson.annotations.SerializedName;
import java.io.Serializable;
import java.util.List;

/**
 * Clase de modelo para representar una entrada de historial de comida
 * tal como se almacena y recupera de MongoDB a través del backend Flask.
 * Nota: Los IDs de MongoDB (_id) se serializarán como String.
 * Los timestamps se serializarán como String en formato ISO 8601.
 */
public class FoodHistoryItem implements Serializable {

    @SerializedName("_id")
    private String id; // El ObjectId de MongoDB convertido a String

    @SerializedName("timestamp")
    private String timestamp; // Fecha y hora de la entrada, como String ISO 8601

    @SerializedName("image_name")
    private String imageName;

    @SerializedName("meal_type")
    private String mealType; // Tipo de comida (desayuno, almuerzo, etc.)

    // Campos para el resumen nutricional total de la comida registrada
    @SerializedName("calorias_totales_comida")
    private float totalCalorias;

    @SerializedName("proteinas_totales_comida")
    private float totalProteinas;

    @SerializedName("grasas_totales_comida")
    private float totalGrasas;

    @SerializedName("carbohidratos_totales_comida")
    private float totalCarbohidratos;

    // Lista de alimentos individuales dentro de esta entrada de comida (puede ser simplificada para el historial)
    // Usaremos FoodItem ya existente, pero puede que no necesitemos todos sus detalles para el historial
    @SerializedName("alimentos")
    private List<FoodItem> alimentos;

    // Resumen general de la comida (ej. "Sin resumen.")
    @SerializedName("resumen_general")
    private String resumenGeneral;


    // Constructor vacío (requerido por Gson)
    public FoodHistoryItem() {
    }

    // --- Getters ---
    public String getId() {
        return id;
    }

    public String getTimestamp() {
        return timestamp;
    }

    public String getImageName() {
        return imageName;
    }

    public String getMealType() {
        return mealType;
    }

    public float getTotalCalorias() {
        return totalCalorias;
    }

    public float getTotalProteinas() {
        return totalProteinas;
    }

    public float getTotalGrasas() {
        return totalGrasas;
    }

    public float getTotalCarbohidratos() {
        return totalCarbohidratos;
    }

    public List<FoodItem> getAlimentos() {
        return alimentos;
    }

    public String getResumenGeneral() {
        return resumenGeneral;
    }

    // --- Setters (Opcionales, pero buena práctica) ---
    public void setId(String id) { this.id = id; }
    public void setTimestamp(String timestamp) { this.timestamp = timestamp; }
    public void setImageName(String imageName) { this.imageName = imageName; }
    public void setMealType(String mealType) { this.mealType = mealType; }
    public void setTotalCalorias(float totalCalorias) { this.totalCalorias = totalCalorias; }
    public void setTotalProteinas(float totalProteinas) { this.totalProteinas = totalProteinas; }
    public void setTotalGrasas(float totalGrasas) { this.totalGrasas = totalGrasas; }
    public void setTotalCarbohidratos(float totalCarbohidratos) { this.totalCarbohidratos = totalCarbohidratos; }
    public void setAlimentos(List<FoodItem> alimentos) { this.alimentos = alimentos; }
    public void setResumenGeneral(String resumenGeneral) { this.resumenGeneral = resumenGeneral; }
}
