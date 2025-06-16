package com.example.app_foodscan.network;

import com.example.app_foodscan.model.FoodHistoryItem;
import com.example.app_foodscan.model.FoodResult;
import java.util.List;
import okhttp3.MultipartBody;
import okhttp3.RequestBody;
import retrofit2.Call;
import retrofit2.http.DELETE;
import retrofit2.http.GET;
import retrofit2.http.Multipart;
import retrofit2.http.POST;
import retrofit2.http.Part;
import retrofit2.http.Path;
import retrofit2.http.Query; // Importa Query por si lo necesitas más adelante

public interface ApiService {

    @Multipart
    @POST("/analizar")
    Call<FoodResult> analyzeImage(
            @Part MultipartBody.Part image,
            @Part("meal_type") RequestBody mealType
    );

    @GET("/historial")
    Call<List<FoodHistoryItem>> getFoodHistory();

    @DELETE("/historial/{id}")
    Call<Void> deleteFoodHistoryItem(@Path("id") String itemId);

    // Opcional: Si implementas historial por fecha en el backend
    // @GET("/historial_por_fecha")
    // Call<List<FoodHistoryItem>> getFoodHistoryByDate(@Query("date") String date);
}