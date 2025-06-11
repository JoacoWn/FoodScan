import os
import shutil
# Se corrigieron los nombres de las variables importadas para que coincidan con config.py
from config import INPUT_IMAGE_DIR, PROCESSING_IMAGE_DIR, PROCESSED_IMAGE_DIR, ERROR_IMAGE_DIR

class ImageManager:
    def __init__(self):
        # Ahora estas variables internas apuntan a los nombres correctos de config.py
        self.input_dir = INPUT_IMAGE_DIR
        self.processing_dir = PROCESSING_IMAGE_DIR
        self.processed_dir = PROCESSED_IMAGE_DIR
        self.error_dir = ERROR_IMAGE_DIR
        self._ensure_directories_exist()

    def _ensure_directories_exist(self):
        """Crea las carpetas necesarias si no existen."""
        for directory in [self.input_dir, self.processing_dir,
                          self.processed_dir, self.error_dir]:
            os.makedirs(directory, exist_ok=True)

    def get_new_images(self):
        """Devuelve lista de imágenes en input_images/"""
        return [
            f for f in os.listdir(self.input_dir)
            if os.path.isfile(os.path.join(self.input_dir, f)) and
            f.lower().endswith(('.jpg', '.jpeg', '.png'))
        ]

    def move_to_processing(self, image_name):
        """Mueve la imagen a processing_images/"""
        src = os.path.join(self.input_dir, image_name)
        dst = os.path.join(self.processing_dir, image_name)
        try:
            shutil.move(src, dst)
            print(f"📥 {image_name} → carpeta de procesamiento.")
            return dst
        except Exception as e:
            print(f"❌ Error al mover {image_name} a procesamiento: {e}")
            return None

    def move_to_processed(self, image_name):
        """Mueve la imagen a processed_images/"""
        src = os.path.join(self.processing_dir, image_name)
        dst = os.path.join(self.processed_dir, image_name)
        try:
            shutil.move(src, dst)
            print(f"✅ {image_name} → carpeta de procesados.")
        except Exception as e:
            print(f"❌ Error al mover {image_name} a procesados: {e}")

    def move_to_error(self, image_name):
        """Mueve la imagen a error_images/"""
        src = os.path.join(self.processing_dir, image_name)
        dst = os.path.join(self.error_dir, image_name)
        try:
            shutil.move(src, dst)
            print(f"🟥 {image_name} → carpeta de errores.")
        except Exception as e:
            print(f"❌ Error al mover {image_name} a errores: {e}")