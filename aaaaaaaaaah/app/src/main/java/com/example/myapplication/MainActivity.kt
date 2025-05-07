package com.example.myapplication

import android.os.Bundle
import android.util.Log
import androidx.appcompat.app.AppCompatActivity
import retrofit2.*
import retrofit2.converter.gson.GsonConverterFactory
import retrofit2.http.*

data class Post(
    val id: Int,
    val userId: Int,
    val title: String,
    val body: String
)

interface ApiService {
    @GET("/posts")
    fun getPosts(): Call<List<Post>>

    @POST("/posts")
    fun createPost(@Body post: Post): Call<Post>

    @PUT("/posts/{id}")
    fun updatePost(@Path("id") postId: Int, @Body post: Post): Call<Post>

    @DELETE("/posts/{id}")
    fun deletePost(@Path("id") postId: Int): Call<Void>
}

class MainActivity : AppCompatActivity() {

    private val baseUrl = "http://<tu-ip-o-dominio>:5000"  // Reemplaza con la IP o dominio de tu servidor Flask

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        val retrofit = Retrofit.Builder()
            .baseUrl(baseUrl)
            .addConverterFactory(GsonConverterFactory.create())
            .build()

        val apiService = retrofit.create(ApiService::class.java)

        // Obtener todos los posts
        getPosts(apiService)

        // Crear un nuevo post
        val newPost = Post(0, 1, "Nuevo Título", "Contenido del post.")
        createPost(apiService, newPost)

        // Actualizar un post existente
        val updatedPost = Post(1, 1, "Título actualizado", "Contenido actualizado")
        updatePost(apiService, 1, updatedPost)

        // Eliminar un post
        deletePost(apiService, 1)
    }

    private fun getPosts(apiService: ApiService) {
        val call = apiService.getPosts()
        call.enqueue(object : Callback<List<Post>> {
            override fun onResponse(call: Call<List<Post>>, response: Response<List<Post>>) {
                if (response.isSuccessful) {
                    val posts = response.body()
                    Log.d("API", "Posts: $posts")
                } else {
                    Log.e("API", "Error: ${response.code()}")
                }
            }

            override fun onFailure(call: Call<List<Post>>, t: Throwable) {
                Log.e("API", "Fallo en la solicitud: ${t.message}")
            }
        })
    }

    private fun createPost(apiService: ApiService, post: Post) {
        val call = apiService.createPost(post)
        call.enqueue(object : Callback<Post> {
            override fun onResponse(call: Call<Post>, response: Response<Post>) {
                if (response.isSuccessful) {
                    val createdPost = response.body()
                    Log.d("API", "Post creado: ${createdPost?.title}")
                } else {
                    Log.e("API", "Error al crear post: ${response.code()}")
                }
            }

            override fun onFailure(call: Call<Post>, t: Throwable) {
                Log.e("API", "Fallo en la solicitud: ${t.message}")
            }
        })
    }

    private fun updatePost(apiService: ApiService, postId: Int, post: Post) {
        val call = apiService.updatePost(postId, post)
        call.enqueue(object : Callback<Post> {
            override fun onResponse(call: Call<Post>, response: Response<Post>) {
                if (response.isSuccessful) {
                    val updatedPost = response.body()
                    Log.d("API", "Post actualizado: ${updatedPost?.title}")
                } else {
                    Log.e("API", "Error al actualizar post: ${response.code()}")
                }
            }

            override fun onFailure(call: Call<Post>, t: Throwable) {
                Log.e("API", "Fallo en la solicitud: ${t.message}")
            }
        })
    }

    private fun deletePost(apiService: ApiService, postId: Int) {
        val call = apiService.deletePost(postId)
        call.enqueue(object : Callback<Void> {
            override fun onResponse(call: Call<Void>, response: Response<Void>) {
                if (response.isSuccessful) {
                    Log.d("API", "Post eliminado con éxito.")
                } else {
                    Log.e("API", "Error al eliminar post: ${response.code()}")
                }
            }

            override fun onFailure(call: Call<Void>, t: Throwable) {
                Log.e("API", "Fallo en la solicitud: ${t.message}")
            }
        })
    }
}

