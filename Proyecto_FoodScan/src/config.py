import os
from dotenv import load_dotenv
import google.generativeai as genai

# Carga las variables de entorno del archivo .env
load_dotenv()

# --- Configuración de MongoDB ---
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
MONGO_DB_NAME = os.getenv("MONGO_DB_NAME", "foodscan_db")
MONGO_COLLECTION_NAME = os.getenv("MONGO_COLLECTION_NAME", "food_entries")

# --- Configuración de Gemini API ---
# La API Key se carga del archivo .env
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Asegúrate de que la API Key esté cargada antes de configurar genai
if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY no encontrada en el archivo .env. Por favor, configúrala.")

# Configura la API de Gemini globalmente.
# Esta línea solo necesita estar aquí una vez.
genai.configure(api_key=GEMINI_API_KEY)

# Nombre del modelo de Gemini
# ¡UTILIZA EL NUEVO MODELO PROPORCIONADO AQUÍ!
GEMINI_MODEL_NAME = "gemini-1.5-pro" # <--- CAMBIA ESTA LÍNEA

# --- Configuración del monitoreo de imágenes (si aún es relevante para alguna parte) ---
MONITOR_INTERVAL_SECONDS = 5

# --- Secciones de comida ---
FOOD_SECTIONS = ["desayuno", "almuerzo", "once"] # 'once' abarca cena

# Rutas de imágenes (deberían ser relativas al directorio raíz del proyecto)
# Estas rutas se usan en ImageManager
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
INPUT_IMAGE_DIR = os.path.join(BASE_DIR, 'images', 'input_images')
PROCESSING_IMAGE_DIR = os.path.join(BASE_DIR, 'images', 'processing_images')
PROCESSED_IMAGE_DIR = os.path.join(BASE_DIR, 'images', 'processed_images')
ERROR_IMAGE_DIR = os.path.join(BASE_DIR, 'images', 'error_images')

# Crea los directorios si no existen
for _dir in [INPUT_IMAGE_DIR, PROCESSING_IMAGE_DIR, PROCESSED_IMAGE_DIR, ERROR_IMAGE_DIR]:
    os.makedirs(_dir, exist_ok=True)