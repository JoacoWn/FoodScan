import os

# === Rutas de carpetas ===
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
IMAGE_DIR = os.path.join(BASE_DIR, '..', 'images')

INPUT_DIR = os.path.join(IMAGE_DIR, 'input_images')
PROCESSING_DIR = os.path.join(IMAGE_DIR, 'processing_images')
PROCESSED_DIR = os.path.join(IMAGE_DIR, 'processed_images')
ERROR_DIR = os.path.join(IMAGE_DIR, 'error_images')

# === Intervalo de escaneo de nuevas imágenes (segundos) ===
MONITOR_INTERVAL_SECONDS = 5

# === API Gemini ===
GEMINI_API_KEY = "AIzaSyDBHci8NClFXNmfiNLArckpsoyRU9TGW4w"  # <- reemplaza con tu clave
GEMINI_MODEL_NAME = "gemini-1.5-flash"

# === MongoDB ===
MONGO_URI = "mongodb://localhost:27017/"
MONGO_DB_NAME = "foodscan_db"
MONGO_COLLECTION_NAME = "daily_meals"

# === Secciones válidas para la comida ===
FOOD_SECTIONS = ["desayuno", "almuerzo", "once"]
