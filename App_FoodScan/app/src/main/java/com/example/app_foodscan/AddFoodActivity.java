package com.example.app_foodscan;

import android.Manifest;
import android.app.Activity;
import android.content.Intent;
import android.content.pm.PackageManager;
import android.net.Uri;
import android.os.Build;
import android.os.Bundle;
import android.os.Environment;
import android.provider.MediaStore;
import android.view.MenuItem; // ¡Importante: Importar MenuItem para el botón de volver!
import android.view.View;
import android.widget.Button;
import android.widget.ImageView;
import android.widget.ProgressBar;
import android.widget.RadioGroup;
import android.widget.RadioButton;
import android.widget.Toast;

import androidx.annotation.NonNull;
import androidx.annotation.Nullable;
import androidx.appcompat.app.AppCompatActivity;
import androidx.appcompat.widget.Toolbar; // ¡Importante: Importar Toolbar!
import androidx.core.app.ActivityCompat;
import androidx.core.content.ContextCompat;
import androidx.core.content.FileProvider;

import com.example.app_foodscan.model.FoodResult;
import com.example.app_foodscan.network.ApiClient;
import com.example.app_foodscan.network.ApiService;
import com.example.app_foodscan.utils.ImageUtils;

import java.io.File;
import java.io.IOException;
import java.text.SimpleDateFormat;
import java.util.Date;
import java.util.Locale;

import okhttp3.MediaType;
import okhttp3.MultipartBody;
import okhttp3.RequestBody;
import retrofit2.Call;
import retrofit2.Callback;
import retrofit2.Response;

public class AddFoodActivity extends AppCompatActivity {

    // Códigos de solicitud para Intents
    private static final int REQUEST_IMAGE_CAPTURE = 1;
    private static final int REQUEST_PICK_IMAGE = 2;

    // Códigos de solicitud para permisos
    private static final int PERMISSION_REQUEST_CAMERA = 100;
    private static final int PERMISSION_REQUEST_STORAGE = 101;

    // Vistas de la UI
    private Button btnCaptureImage;
    private Button btnSelectFromGallery;
    private Button btnProcessImage;
    private RadioGroup radioGroupMealType;
    private ImageView imageViewPreview;
    private ProgressBar progressBar;

    // URI para la imagen capturada por la cámara (temporal)
    private Uri currentPhotoUri;
    // URI para la imagen seleccionada de la galería o capturada
    private Uri selectedImageUri;

    // Servicio para la API
    private ApiService apiService;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_add_food);

        // --- Configuración de la Toolbar (NUEVO) ---
        Toolbar toolbar = findViewById(R.id.toolbar);
        setSupportActionBar(toolbar);
        if (getSupportActionBar() != null) {
            getSupportActionBar().setTitle("Agregar Nueva Comida"); // Título para esta Activity
            getSupportActionBar().setDisplayHomeAsUpEnabled(true); // Habilita el botón de volver (flecha)
        }
        // --- Fin Configuración de la Toolbar ---

        // Inicializar vistas
        btnCaptureImage = findViewById(R.id.btnCaptureImage);
        btnSelectFromGallery = findViewById(R.id.btnSelectFromGallery);
        btnProcessImage = findViewById(R.id.btnProcessImage);
        radioGroupMealType = findViewById(R.id.radioGroupMealType);
        imageViewPreview = findViewById(R.id.imageViewPreview);
        progressBar = findViewById(R.id.progressBar);

        // Inicializar ApiService
        apiService = ApiClient.getClient();

        // Configurar listeners de botones
        btnCaptureImage.setOnClickListener(v -> checkCameraPermissionAndCaptureImage());
        btnSelectFromGallery.setOnClickListener(v -> checkStoragePermissionAndPickImage());
        btnProcessImage.setOnClickListener(v -> uploadImage());

        // Deshabilitar el botón de procesar inicialmente
        btnProcessImage.setEnabled(false);
        progressBar.setVisibility(View.GONE);
    }

    // --- Método para manejar el clic en el botón de vuelta de la Toolbar (NUEVO) ---
    @Override
    public boolean onOptionsItemSelected(@NonNull MenuItem item) {
        if (item.getItemId() == android.R.id.home) {
            onBackPressed(); // Simula el comportamiento del botón Atrás
            return true;
        }
        return super.onOptionsItemSelected(item);
    }
    // --- Fin Método para manejar el clic en el botón de vuelta de la Toolbar ---

    // --- Métodos de Permisos ---

    private void checkCameraPermissionAndCaptureImage() {
        if (ContextCompat.checkSelfPermission(this, Manifest.permission.CAMERA) != PackageManager.PERMISSION_GRANTED) {
            ActivityCompat.requestPermissions(this, new String[]{Manifest.permission.CAMERA}, PERMISSION_REQUEST_CAMERA);
        } else {
            dispatchTakePictureIntent();
        }
    }

    private void checkStoragePermissionAndPickImage() {
        if (Build.VERSION.SDK_INT <= Build.VERSION_CODES.P && ContextCompat.checkSelfPermission(this, Manifest.permission.READ_EXTERNAL_STORAGE) != PackageManager.PERMISSION_GRANTED) {
            ActivityCompat.requestPermissions(this, new String[]{Manifest.permission.READ_EXTERNAL_STORAGE}, PERMISSION_REQUEST_STORAGE);
        } else {
            openGallery();
        }
    }

    @Override
    public void onRequestPermissionsResult(int requestCode, @NonNull String[] permissions, @NonNull int[] grantResults) {
        super.onRequestPermissionsResult(requestCode, permissions, grantResults);
        if (requestCode == PERMISSION_REQUEST_CAMERA) {
            if (grantResults.length > 0 && grantResults[0] == PackageManager.PERMISSION_GRANTED) {
                dispatchTakePictureIntent();
            } else {
                Toast.makeText(this, "Permiso de cámara denegado. No se puede tomar foto.", Toast.LENGTH_SHORT).show();
            }
        } else if (requestCode == PERMISSION_REQUEST_STORAGE) {
            if (grantResults.length > 0 && grantResults[0] == PackageManager.PERMISSION_GRANTED) {
                openGallery();
            } else {
                Toast.makeText(this, "Permiso de almacenamiento denegado. No se puede seleccionar imagen.", Toast.LENGTH_SHORT).show();
            }
        }
    }

    // --- Métodos para Lanzar Intents ---

    private void dispatchTakePictureIntent() {
        Intent takePictureIntent = new Intent(MediaStore.ACTION_IMAGE_CAPTURE);
        if (takePictureIntent.resolveActivity(getPackageManager()) != null) {
            File photoFile = null;
            try {
                photoFile = createImageFile();
            } catch (IOException ex) {
                Toast.makeText(this, "Error al crear archivo de imagen: " + ex.getMessage(), Toast.LENGTH_SHORT).show();
            }
            if (photoFile != null) {
                currentPhotoUri = FileProvider.getUriForFile(this,
                        getApplicationContext().getPackageName() + ".fileprovider",
                        photoFile);
                takePictureIntent.putExtra(MediaStore.EXTRA_OUTPUT, currentPhotoUri);
                startActivityForResult(takePictureIntent, REQUEST_IMAGE_CAPTURE);
            }
        } else {
            Toast.makeText(this, "No se encontró aplicación de cámara.", Toast.LENGTH_SHORT).show();
        }
    }

    private void openGallery() {
        Intent pickImageIntent = new Intent(Intent.ACTION_PICK, MediaStore.Images.Media.EXTERNAL_CONTENT_URI);
        startActivityForResult(pickImageIntent, REQUEST_PICK_IMAGE);
    }

    // --- Manejo de Resultados de Intents ---

    @Override
    protected void onActivityResult(int requestCode, int resultCode, @Nullable Intent data) {
        super.onActivityResult(requestCode, resultCode, data);
        if (resultCode == RESULT_OK) {
            if (requestCode == REQUEST_IMAGE_CAPTURE) {
                selectedImageUri = currentPhotoUri;
                imageViewPreview.setImageURI(selectedImageUri);
                imageViewPreview.setVisibility(View.VISIBLE);
                btnProcessImage.setEnabled(true);
                Toast.makeText(this, "Imagen capturada lista para procesar.", Toast.LENGTH_SHORT).show();
            } else if (requestCode == REQUEST_PICK_IMAGE && data != null) {
                selectedImageUri = data.getData();
                imageViewPreview.setImageURI(selectedImageUri);
                imageViewPreview.setVisibility(View.VISIBLE);
                btnProcessImage.setEnabled(true);
                Toast.makeText(this, "Imagen seleccionada lista para procesar.", Toast.LENGTH_SHORT).show();
            }
        } else if (resultCode == RESULT_CANCELED) {
            Toast.makeText(this, "Acción de selección/captura de imagen cancelada.", Toast.LENGTH_SHORT).show();
            btnProcessImage.setEnabled(false);
            imageViewPreview.setVisibility(View.GONE);
        }
    }

    // --- Método Auxiliar para Crear Archivo de Imagen ---

    private File createImageFile() throws IOException {
        String timeStamp = new SimpleDateFormat("yyyyMMdd_HHmmss", Locale.getDefault()).format(new Date());
        String imageFileName = "JPEG_" + timeStamp + "_";
        File storageDir = getExternalFilesDir(Environment.DIRECTORY_PICTURES);
        File image = File.createTempFile(
                imageFileName,
                ".jpg",
                storageDir
        );
        return image;
    }

    // --- Lógica de Subida de Imagen ---

    private void uploadImage() {
        if (selectedImageUri == null) {
            Toast.makeText(this, "No hay imagen seleccionada para procesar.", Toast.LENGTH_SHORT).show();
            return;
        }

        progressBar.setVisibility(View.VISIBLE);
        btnProcessImage.setEnabled(false);

        String mealType = getSelectedMealType();
        if (mealType == null) {
            Toast.makeText(this, "Por favor, selecciona un tipo de comida.", Toast.LENGTH_SHORT).show();
            progressBar.setVisibility(View.GONE);
            btnProcessImage.setEnabled(true);
            return;
        }

        File imageFile = ImageUtils.getFileFromUri(this, selectedImageUri);
        if (imageFile == null) {
            Toast.makeText(this, "Error al obtener el archivo de imagen.", Toast.LENGTH_SHORT).show();
            progressBar.setVisibility(View.GONE);
            btnProcessImage.setEnabled(true);
            return;
        }

        RequestBody requestFile = RequestBody.create(MediaType.parse("image/*"), imageFile);
        MultipartBody.Part body = MultipartBody.Part.createFormData("image", imageFile.getName(), requestFile);

        RequestBody mealTypeRequestBody = RequestBody.create(MediaType.parse("text/plain"), mealType);

        Call<FoodResult> call = apiService.analyzeImage(body, mealTypeRequestBody);
        call.enqueue(new Callback<FoodResult>() {
            @Override
            public void onResponse(Call<FoodResult> call, Response<FoodResult> response) {
                progressBar.setVisibility(View.GONE);
                btnProcessImage.setEnabled(true);

                if (response.isSuccessful() && response.body() != null) {
                    FoodResult result = response.body();
                    Intent intent = new Intent(AddFoodActivity.this, ResultActivity.class);
                    intent.putExtra("foodResult", result); // Pasa el OBJETO FoodResult completo
                    startActivity(intent);
                    imageViewPreview.setVisibility(View.GONE);
                    selectedImageUri = null;
                    Toast.makeText(AddFoodActivity.this, "Análisis completado.", Toast.LENGTH_SHORT).show();
                } else {
                    String errorMessage = "Error del servidor: " + response.code();
                    try {
                        if (response.errorBody() != null) {
                            errorMessage += "\n" + response.errorBody().string();
                        }
                    } catch (IOException e) {
                        e.printStackTrace();
                    }
                    Toast.makeText(AddFoodActivity.this, errorMessage, Toast.LENGTH_LONG).show();
                }
            }

            @Override
            public void onFailure(Call<FoodResult> call, Throwable t) {
                progressBar.setVisibility(View.GONE);
                btnProcessImage.setEnabled(true);
                Toast.makeText(AddFoodActivity.this, "Fallo en conexión: " + t.getMessage(), Toast.LENGTH_LONG).show();
                t.printStackTrace();
            }
        });
    }

    /**
     * Obtiene el tipo de comida seleccionado del RadioGroup.
     * @return El string del tipo de comida seleccionado o null si no se seleccionó ninguno.
     */
    private String getSelectedMealType() {
        int selectedId = radioGroupMealType.getCheckedRadioButtonId();
        if (selectedId != -1) {
            RadioButton selectedRadioButton = findViewById(selectedId);
            // Mapea el texto del RadioButton a las claves de tu backend (desayuno, almuerzo, aperitivo, cena)
            String text = selectedRadioButton.getText().toString();
            switch (text) {
                case "Desayuno": return "desayuno";
                case "Almuerzo": return "almuerzo";
                case "Snack/Aperitivo": return "aperitivo";
                case "Cena": return "cena";
                default: return "desconocido"; // Fallback
            }
        }
        return null;
    }
}