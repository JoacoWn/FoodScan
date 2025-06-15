package com.example.app_foodscan.model;

import com.google.gson.annotations.SerializedName;
import java.io.Serializable;

/**
 * Clase de modelo para mapear cada alimento individual dentro de la lista 'alimentos_detallados'
 * de la respuesta JSON del servidor Flask.
 * Las variables y sus anotaciones @SerializedName deben coincidir exactamente
 * con las claves de cada objeto de alimento dentro de la lista.
 */
public class FoodItem implements Serializable {

    @SerializedName("nombre")
    private String nombre; // Nombre del alimento individual (ej. "Pan Blanco")

    @SerializedName("cantidad_g")
    private float cantidad_g; // Cantidad estimada en gramos (peso aproximado)

    @SerializedName("calorias")
    private float calorias; // Calorías calculadas para este alimento individual

    @SerializedName("proteinas")
    private float proteinas; // Proteínas calculadas para este alimento individual

    @SerializedName("grasas")
    private float grasas;    // Grasas calculadas para este alimento individual

    @SerializedName("carbohidratos")
    private float carbohidratos; // Carbohidratos calculados para este alimento individual

    @SerializedName("es_estimado")
    private boolean es_estimado; // Indica si los nutrientes fueron estimados por IA

    // Constructor vacío (requerido por Gson para la deserialización)
    public FoodItem() {
    }

    // --- Getters ---
    public String getNombre() {
        return nombre;
    }

    public float getCantidad_g() {
        return cantidad_g;
    }

    public float getCalorias() {
        return calorias;
    }

    public float getProteinas() {
        return proteinas;
    }

    public float getGrasas() {
        return grasas;
    }

    public float getCarbohidratos() {
        return carbohidratos;
    }

    public boolean isEs_estimado() {
        return es_estimado;
    }

    // --- Setters (incluidos para completitud, aunque Gson los maneja) ---
    public void setNombre(String nombre) {
        this.nombre = nombre;
    }

    public void setCantidad_g(float cantidad_g) {
        this.cantidad_g = cantidad_g;
    }

    public void setCalorias(float calorias) {
        this.calorias = calorias;
    }

    public void setProteinas(float proteinas) {
        this.proteinas = proteinas;
    }

    public void setGrasas(float grasas) {
        this.grasas = grasas;
    }

    public void setCarbohidratos(float carbohidratos) {
        this.carbohidratos = carbohidratos;
    }

    public void setEs_estimado(boolean es_estimado) {
        this.es_estimado = es_estimado;
    }
}