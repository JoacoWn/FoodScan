package com.example.app_flask;

import android.os.Bundle;
import android.util.Log;
import android.view.View;
import android.widget.Button;
import android.widget.TextView;

import androidx.appcompat.app.AppCompatActivity;

import com.android.volley.Request;
import com.android.volley.RequestQueue;
import com.android.volley.Response;
import com.android.volley.VolleyError;
import com.android.volley.toolbox.StringRequest;
import com.android.volley.toolbox.Volley;

import org.json.JSONException;
import org.json.JSONObject;

public class MainActivity extends AppCompatActivity {

    private static final String TAG = "MainActivity";
    private Button buttonFetchData;
    private TextView textViewResponse;
    private RequestQueue requestQueue;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);

        buttonFetchData = findViewById(R.id.button_fetch_data);
        textViewResponse = findViewById(R.id.textView_response);
        requestQueue = Volley.newRequestQueue(this);

        buttonFetchData.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                fetchDataFromFlask();
            }
        });
    }

    private void fetchDataFromFlask() {
        String url = "http://100.27.56.5:8081/api/datos"; // tu IP actual

        StringRequest stringRequest = new StringRequest(Request.Method.GET, url,
                new Response.Listener<String>() {
                    @Override
                    public void onResponse(String response) {
                        Log.d(TAG, "Response: " + response);
                        try {
                            JSONObject jsonObject = new JSONObject(response);
                            String nombre = jsonObject.getString("nombre");
                            String correo = jsonObject.getString("correo");
                            String numero = jsonObject.getString("numero");

                            String resultado = "Nombre: " + nombre
                                    + "\nCorreo: " + correo + "\nNúmero: " + numero;
                            textViewResponse.setText(resultado);
                        } catch (JSONException e) {
                            e.printStackTrace();
                            textViewResponse.setText("Error al parsear JSON");
                            Log.e(TAG, "Error al parsear JSON", e);
                        }
                    }
                },
                new Response.ErrorListener() {
                    @Override
                    public void onErrorResponse(VolleyError error) {
                        textViewResponse.setText("Error al obtener datos");
                        Log.e(TAG, "Error al obtener datos", error);
                    }
                });

        requestQueue.add(stringRequest);
    }
}
