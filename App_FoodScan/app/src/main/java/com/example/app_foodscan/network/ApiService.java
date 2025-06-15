package com.example.app_foodscan.network;

import com.example.app_foodscan.model.FoodResult;
import com.example.app_foodscan.model.FoodHistoryItem; // Importar el nuevo modelo de historial
import java.util.List; // Importar para listas

import okhttp3.MultipartBody;
import okhttp3.RequestBody;
import retrofit2.Call;
import retrofit2.http.GET; // Importar GET para el historial
import retrofit2.http.Multipart;
import retrofit2.http.POST;
import retrofit2.http.Part;

/**
 * Interfaz Retrofit que define los endpoints de la API de tu backend Flask.
 */
public interface ApiService {

    /**
     * Endpoint para subir una imagen y el tipo de comida para análisis.
     * @param image El archivo de imagen como MultipartBody.Part.
     * @param mealType El tipo de comida (desayuno, almuerzo, etc.) como RequestBody.
     * @return Un objeto Call de Retrofit que devuelve un FoodResult.
     */
    @Multipart
    @POST("/analizar")
    Call<FoodResult> uploadImage(@Part MultipartBody.Part image, @Part("meal_type") RequestBody mealType);

    /**
     * NUEVO ENDPOINT: Obtiene el historial completo de comidas registradas.
     * @return Un objeto Call de Retrofit que devuelve una lista de FoodHistoryItem.
     */
    @GET("/historial")
    Call<List<FoodHistoryItem>> getFoodHistory();
}
