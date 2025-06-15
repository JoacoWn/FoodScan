import os
from dotenv import load_dotenv
import google.generativeai as genai

# Carga las variables de entorno del archivo .env
load_dotenv()

# --- Configuración de MongoDB ---
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
MONGO_DB_NAME = os.getenv("MONGO_DB_NAME", "foodscan_db")
MONGO_COLLECTION_NAME = os.getenv("MONGO_COLLECTION_NAME", "food_entries")

# --- Configuración de OpenRouter API para Gemini ---
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
GEMINI_MODEL_NAME = "google/gemini-2.5-flash-preview"

# Asegúrate de que la API Key esté cargada
if not OPENROUTER_API_KEY:
    raise ValueError("OPENROUTER_API_KEY no encontrada en el archivo .env. Por favor, configúrala.")

# --- Configuración del monitoreo de imágenes (mantener para ImageManager, aunque Flask recibe directo) ---
MONITOR_INTERVAL_SECONDS = 5 # Mantener si se usa para otras partes, pero no crítico para Flask API

# --- Secciones de comida ---
FOOD_SECTIONS = ["desayuno", "almuerzo", "aperitivo", "cena"] # ¡APERITIVO AÑADIDO Y CENA EN LUGAR DE ONCE!

# Rutas de imágenes (relativas al directorio raíz del proyecto)
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..')) # La raíz del proyecto FoodScan

INPUT_IMAGE_DIR = os.path.join(BASE_DIR, 'images', 'input_images')
PROCESSING_IMAGE_DIR = os.path.join(BASE_DIR, 'images', 'processing_images')
PROCESSED_IMAGE_DIR = os.path.join(BASE_DIR, 'images', 'processed_images')
ERROR_IMAGE_DIR = os.path.join(BASE_DIR, 'images', 'error_images')

# Crea los directorios si no existen al iniciar el backend
for _dir in [INPUT_IMAGE_DIR, PROCESSING_IMAGE_DIR, PROCESSED_IMAGE_DIR, ERROR_IMAGE_DIR]:
    os.makedirs(_dir, exist_ok=True)