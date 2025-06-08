# Variables de configuración para FoodScan

# Configuración de rutas de directorios
# Configuración de rutas de directorios
INPUT_DIR = "../images/input_images/"  # <-- Añade '../'
PROCESSING_DIR = "../images/processing_images/" # <-- Añade '../'
PROCESSED_DIR = "../images/processed_images/"   # <-- Añade '../'
ERROR_DIR = "../images/error_images/"         # <-- Añade '../'

# Intervalo de monitoreo de nuevas imágenes (en segundos)
MONITOR_INTERVAL_SECONDS = 5

# Secciones de comida (ej. desayuno, almuerzo, once)
FOOD_SECTIONS = ["desayuno", "almuerzo", "once"]

# Configuración de MongoDB
MONGO_URI = "mongodb://localhost:27017/" # URI de conexión a tu instancia de MongoDB
MONGO_DB_NAME = "foodscan_db"            # Nombre de la base de datos
MONGO_COLLECTION_NAME = "meals"          # Nombre de la colección

# Clave de API de Google Gemini
# ¡ADVERTENCIA! No compartas tu clave de API. Guárdala de forma segura.
# Puedes obtener una en https://aistudio.google.com/
GEMINI_API_KEY = "AIzaSyDBHci8NClFXNmfiNLArckpsoyRU9TGW4w" # Reemplaza con tu clave real

# Modelo de Gemini a usar
GEMINI_MODEL_NAME = "gemini-1.5-flash"

# Flag para el tutorial inicial (True significa que se mostrará la primera vez)
INITIAL_SCAN = True # Este flag se usará si no hay un archivo de "first run"