package com.example.app_foodscan.utils;

import android.content.Context;
import android.database.Cursor;
import android.net.Uri;
import android.provider.MediaStore;
import android.util.Log; // Importar Log para depuración

import java.io.File;
import java.io.FileOutputStream; // Para manejar la escritura de archivos
import java.io.IOException; // Importar IOException
import java.io.InputStream; // Para leer de la URI

/**
 * Clase de utilidad para manejar operaciones relacionadas con imágenes,
 * como la conversión de una Uri a un objeto File.
 * Este método es crucial para enviar imágenes a un servidor utilizando Retrofit
 * con MultipartBody, ya que Retrofit necesita un File para crear la parte del cuerpo.
 */
public class ImageUtils {

    private static final String TAG = "ImageUtils"; // Etiqueta para logs

    public static File getFileFromUri(Context context, Uri uri) {
        if (uri == null) {
            Log.e(TAG, "getFileFromUri: La URI es nula.");
            return null;
        }

        // ¡IMPORTANTE! Para compatibilidad con Android 10+ (API 29+) y FileProvider,
        // la forma más robusta es copiar el InputStream a un archivo temporal.
        // Intentar obtener _data directamente puede fallar y causar la excepción.
        // Por lo tanto, priorizamos el enfoque de InputStream.

        try {
            InputStream inputStream = context.getContentResolver().openInputStream(uri);
            if (inputStream == null) {
                Log.e(TAG, "getFileFromUri: No se pudo abrir el InputStream para la URI: " + uri);
                return null;
            }

            // Determinar la extensión del archivo.
            // Para URIs de la cámara o galería, el ContentResolver puede dar el tipo MIME.
            String fileExtension = ".jpg"; // Default
            String mimeType = context.getContentResolver().getType(uri);
            if (mimeType != null && mimeType.startsWith("image/")) {
                String[] parts = mimeType.split("/");
                if (parts.length > 1) {
                    fileExtension = "." + parts[1]; // Ej. ".png", ".jpeg"
                }
            }

            // Crea un archivo temporal en el directorio de caché de la aplicación.
            // Los archivos en cacheDir son ideales para datos temporales que se pueden borrar.
            String fileName = "upload_image_" + System.currentTimeMillis() + fileExtension;
            File tempFile = new File(context.getCacheDir(), fileName);

            // Log para depuración
            Log.d(TAG, "getFileFromUri: Intentando copiar URI a archivo temporal: " + tempFile.getAbsolutePath());

            FileOutputStream outputStream = new FileOutputStream(tempFile);
            byte[] buffer = new byte[4 * 1024]; // Buffer de 4KB para copiar
            int read;
            while ((read = inputStream.read(buffer)) != -1) {
                outputStream.write(buffer, 0, read);
            }

            outputStream.flush();
            outputStream.close();
            inputStream.close();

            Log.d(TAG, "getFileFromUri: Archivo temporal creado con éxito en: " + tempFile.getAbsolutePath());
            return tempFile;

        } catch (IOException e) {
            // Manejo de errores si hay un problema al leer de la URI o escribir al archivo
            Log.e(TAG, "getFileFromUri: Error de I/O al copiar la URI a un archivo temporal: " + e.getMessage(), e);
            return null;
        } catch (SecurityException e) {
            // Esto puede ocurrir si no hay permisos adecuados para leer la URI
            Log.e(TAG, "getFileFromUri: Error de seguridad al acceder a la URI: " + e.getMessage(), e);
            return null;
        } catch (Exception e) {
            // Captura cualquier otra excepción inesperada
            Log.e(TAG, "getFileFromUri: Error inesperado al procesar URI: " + e.getMessage(), e);
            return null;
        }
        // Ya no necesitamos el código original que intentaba obtener la columna _data
        // porque ese enfoque es propenso a fallar con FileProvider y versiones recientes de Android.
    }
}