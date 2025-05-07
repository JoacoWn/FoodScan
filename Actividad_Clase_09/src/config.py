import os

# Rutas de las carpetas
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IMAGE_DIR = os.path.join(BASE_DIR, 'images')
INPUT_DIR = os.path.join(IMAGE_DIR, 'input_images')
PROCESSING_DIR = os.path.join(IMAGE_DIR, 'processing_images')
PROCESSED_DIR = os.path.join(IMAGE_DIR, 'processed_images')
INFRACTIONS_DIR = os.path.join(IMAGE_DIR, 'infracciones_detectadas')
ERROR_DIR = os.path.join(IMAGE_DIR, 'error_images')

# Configuración del monitoreo de imágenes
MONITOR_INTERVAL_SECONDS = 5  # Intervalo de tiempo para revisar nuevas imágenes

# Configuración de la API de Gemini (Google AI)
GEMINI_API_KEY = "AIzaSyDBHci8NClFXNmfiNLArckpsoyRU9TGW4w"  # API key proporcionada [cite: 1]
GEMINI_MODEL_NAME = "gemini-1.5-flash"

# Umbrales de confianza para la detección de infracciones
CONFIDENCE_THRESHOLD_VIOLATION = 0.7  # Umbral mínimo de confianza para considerar una infracción [cite: 1]
CONFIDENCE_THRESHOLD_PLATE = 0.5  # Umbral mínimo de confianza para detectar una patente (opcional, si el modelo lo permite) [cite: 2]

# --- Configuración de MongoDB ---
MONGO_URI = "mongodb://localhost:27017/"  # URI de conexión a tu MongoDB local [cite: 2]
MONGO_DB_NAME = "parking_violations_db"  # Nombre de la base de datos [cite: 2]
MONGO_COLLECTION_NAME = "infractios"  # Nombre de la colección [cite: 2]