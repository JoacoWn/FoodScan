package com.example.app_foodscan.utils;

import android.content.Context;
import android.database.Cursor;
import android.net.Uri;
import android.provider.MediaStore;
import android.util.Log; // Importar Log para depuración

import java.io.File;
import java.io.FileOutputStream; // Para manejar la escritura de archivos
import java.io.InputStream; // Para leer de la URI

/**
 * Clase de utilidad para manejar operaciones relacionadas con imágenes,
 * como la conversión de una Uri a un objeto File.
 */
public class ImageUtils {

    private static final String TAG = "ImageUtils"; // Etiqueta para logs

    /**
     * Convierte una Uri de contenido a un objeto File.
     * Este método es crucial para enviar imágenes a un servidor utilizando Retrofit
     * con MultipartBody, ya que Retrofit necesita un File para crear la parte del cuerpo.
     * @param context El contexto de la aplicación.
     * @param uri La Uri de la imagen.
     * @return Un objeto File que representa la imagen, o null si hay un error.
     */
    public static File getFileFromUri(Context context, Uri uri) {
        if (uri == null) {
            Log.e(TAG, "getFileFromUri: La URI es nula.");
            return null;
        }

        // Intenta obtener la ruta real del archivo si es una URI de archivo o de contenido de la galería
        String filePath = null;
        // Método 1: Intentar obtener la ruta directa del MediaStore
        String[] projection = {MediaStore.Images.Media.DATA};
        Cursor cursor = context.getContentResolver().query(uri, projection, null, null, null);
        if (cursor != null) {
            try {
                if (cursor.moveToFirst()) {
                    int columnIndex = cursor.getColumnIndexOrThrow(MediaStore.Images.Media.DATA);
                    filePath = cursor.getString(columnIndex);
                }
            } finally {
                cursor.close();
            }
        }

        if (filePath != null) {
            // Si la ruta del archivo se obtuvo correctamente, se devuelve un nuevo File
            return new File(filePath);
        } else {
            // Método 2: Si no se pudo obtener la ruta directa (ej. para URIs de Google Photos, Drive),
            // se copia el contenido a un archivo temporal.
            // Esto es más robusto para diferentes tipos de URIs de contenido.
            try {
                InputStream inputStream = context.getContentResolver().openInputStream(uri);
                if (inputStream == null) {
                    Log.e(TAG, "getFileFromUri: No se pudo abrir el InputStream para la URI: " + uri);
                    return null;
                }

                // Crea un archivo temporal en el caché de la aplicación
                String fileName = "upload_image_" + System.currentTimeMillis() + ".jpg";
                File tempFile = new File(context.getCacheDir(), fileName);
                FileOutputStream outputStream = new FileOutputStream(tempFile);

                byte[] buffer = new byte[4 * 1024]; // Buffer de 4KB
                int read;
                while ((read = inputStream.read(buffer)) != -1) {
                    outputStream.write(buffer, 0, read);
                }

                outputStream.flush();
                outputStream.close();
                inputStream.close();

                Log.d(TAG, "getFileFromUri: Archivo temporal creado en: " + tempFile.getAbsolutePath());
                return tempFile;
            } catch (Exception e) {
                Log.e(TAG, "getFileFromUri: Error al copiar la URI a un archivo temporal: " + e.getMessage(), e);
                return null;
            }
        }
    }
}
