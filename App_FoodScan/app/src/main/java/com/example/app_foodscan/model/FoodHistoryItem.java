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

    // --- CAMBIOS AQUÍ: Las claves coinciden con la respuesta REAL del backend ---
    @SerializedName("nombre_general_comida") // Nombre general del plato (ej. "Chorrillana Clásica")
    private String nombreGeneralComida;

    @SerializedName("calorias_totales") // Coincide con 'calorias_totales' del backend
    private float totalCalorias;

    @SerializedName("proteinas_totales") // Coincide con 'proteinas_totales' del backend
    private float totalProteinas;

    @SerializedName("grasas_totales") // Coincide con 'grasas_totales' del backend
    private float totalGrasas;

    @SerializedName("carbohidratos_totales") // Coincide con 'carbohidratos_totales' del backend
    private float totalCarbohidratos;

    // La lista de alimentos detallados ahora se llama "alimentos_detallados" en el backend
    @SerializedName("alimentos_detallados")
    private List<FoodItemDetail> alimentosDetallados; // Usaremos un nuevo modelo FoodItemDetail para esto


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

    public String getNombreGeneralComida() { // Nuevo getter
        return nombreGeneralComida;
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

    public List<FoodItemDetail> getAlimentosDetallados() { // Nuevo getter con nuevo tipo
        return alimentosDetallados;
    }

    // --- Setters (Opcionales, pero buena práctica) ---
    public void setId(String id) { this.id = id; }
    public void setTimestamp(String timestamp) { this.timestamp = timestamp; } // Corregido: eliminado 'void' duplicado
    public void setImageName(String imageName) { this.imageName = imageName; }
    public void setMealType(String mealType) { this.mealType = mealType; }
    public void setNombreGeneralComida(String nombreGeneralComida) { this.nombreGeneralComida = nombreGeneralComida; }
    public void setTotalCalorias(float totalCalorias) { this.totalCalorias = totalCalorias; }
    public void setTotalProteinas(float totalProteinas) { this.totalProteinas = totalProteinas; }
    public void setTotalGrasas(float totalGrasas) { this.totalGrasas = totalGrasas; }
    public void setTotalCarbohidratos(float totalCarbohidratos) { this.totalCarbohidratos = totalCarbohidratos; }
    public void setAlimentosDetallados(List<FoodItemDetail> alimentosDetallados) { this.alimentosDetallados = alimentosDetallados; }
}