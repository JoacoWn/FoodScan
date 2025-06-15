// ApiClient.java
package com.example.app_foodscan.network;

import retrofit2.Retrofit;
import retrofit2.converter.gson.GsonConverterFactory;

/**
 * Cliente Retrofit para configurar y obtener la instancia de la API.
 * Se utiliza un patrón Singleton para asegurar que solo haya una instancia de Retrofit.
 */
public class ApiClient {

    private static Retrofit retrofit = null;

    /**
     * Obtiene la instancia de Retrofit configurada. Si no existe, la crea.
     * @return La instancia de Retrofit.
     */
    public static Retrofit getClient() {
        if (retrofit == null) {
            // Crea una nueva instancia de Retrofit
            retrofit = new Retrofit.Builder()
                    // ¡ACTUALIZA ESTA URL CON EL DNS PÚBLICO DE TU INSTANCIA EC2 Y EL PUERTO 5000!
                    .baseUrl("http://ec2-34-227-214-191.compute-1.amazonaws.com:5000/") // <--- ¡ESTA ES LA LÍNEA CLAVE!
                    // Añade un convertidor para manejar JSON usando Gson
                    .addConverterFactory(GsonConverterFactory.create())
                    .build();
        }
        return retrofit;
    }
}