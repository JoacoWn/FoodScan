package com.example.app_foodscan.model;

import com.google.gson.annotations.SerializedName;
import java.io.Serializable;
import java.util.List;

/**
 * Clase de modelo para mapear la respuesta JSON del servidor Flask.
 * Representa el resultado del análisis de una comida completa.
 * Las variables y sus anotaciones @SerializedName deben coincidir exactamente
 * con las claves del JSON que devuelve tu backend para el resumen general.
 */
public class FoodResult implements Serializable {

    @SerializedName("nombre")
    private String nombre; // Nombre general de la comida (ej. "Comida Analizada")

    @SerializedName("calorias")
    private float calorias; // Calorías totales de la comida

    // =========================================================================
    // ¡¡¡CAMPOS FALTANTES QUE CAUSABAN EL PROBLEMA DE 0.00g EN LOS TOTALES!!!
    // Asegúrate de que estos campos y sus @SerializedName estén presentes.
    @SerializedName("proteinas")
    private float proteinasTotales; // Proteínas totales de la comida

    @SerializedName("grasas")
    private float grasasTotales;     // Grasas totales de la comida

    @SerializedName("carbohidratos")
    private float carbohidratosTotales; // Carbohidratos totales de la comida
    // =========================================================================

    // Lista de alimentos detallados individuales
    @SerializedName("alimentos_detallados")
    private List<FoodItem> alimentosDetallados;

    // Constructor vacío (requerido por Gson para la deserialización)
    public FoodResult() {
    }

    // --- Getters ---
    public String getNombre() {
        return nombre;
    }

    public float getCalorias() {
        return calorias;
    }

    // =========================================================================
    // ¡¡¡Getters para los nuevos campos totales!!!
    public float getProteinasTotales() {
        return proteinasTotales;
    }

    public float getGrasasTotales() {
        return grasasTotales;
    }

    public float getCarbohidratosTotales() {
        return carbohidratosTotales;
    }
    // =========================================================================

    public List<FoodItem> getAlimentosDetallados() {
        return alimentosDetallados;
    }

    // --- Setters (incluidos para completitud, aunque Gson los maneja) ---
    public void setNombre(String nombre) {
        this.nombre = nombre;
    }

    public void setCalorias(float calorias) {
        this.calorias = calorias;
    }

    // =========================================================================
    // ¡¡¡Setters para los nuevos campos totales!!!
    public void setProteinasTotales(float proteinasTotales) {
        this.proteinasTotales = proteinasTotales;
    }

    public void setGrasasTotales(float grasasTotales) {
        this.grasasTotales = grasasTotales;
    }

    public void setCarbohidratosTotales(float carbohidratosTotales) {
        this.carbohidratosTotales = carbohidratosTotales;
    }
    // =========================================================================

    public void setAlimentosDetallados(List<FoodItem> alimentosDetallados) {
        this.alimentosDetallados = alimentosDetallados;
    }
}