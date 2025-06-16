// ApiClient.java
package com.example.app_foodscan.network;

import okhttp3.OkHttpClient; // Importa OkHttpClient
import okhttp3.logging.HttpLoggingInterceptor; // Importa HttpLoggingInterceptor
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
    public static ApiService getClient() {
        if (retrofit == null) {
            // Crea un interceptor para loggear las peticiones y respuestas HTTP
            HttpLoggingInterceptor logging = new HttpLoggingInterceptor();
            // Establece el nivel de logging a BODY para ver los cuerpos de solicitud y respuesta
            logging.setLevel(HttpLoggingInterceptor.Level.BODY);

            // Construye el cliente OkHttpClient y añade el interceptor
            OkHttpClient.Builder httpClient = new OkHttpClient.Builder();
            httpClient.addInterceptor(logging); // Añade el interceptor al cliente HTTP

            // Crea una nueva instancia de Retrofit
            retrofit = new Retrofit.Builder()
                    // ¡ACTUALIZA ESTA URL CON EL DNS PÚBLICO DE TU INSTANCIA EC2 Y EL PUERTO 5000!
                    .baseUrl("http://ec2-34-227-214-191.compute-1.amazonaws.com:5000/") // <--- ¡ESTA ES LA LÍNEA CLAVE!
                    // Añade un convertidor para manejar JSON usando Gson
                    .addConverterFactory(GsonConverterFactory.create())
                    .client(httpClient.build()) // Asigna el cliente OkHttpClient con el interceptor
                    .build();
        }
        return retrofit.create(ApiService.class); // Asegúrate de que esto devuelve ApiService
    }
}