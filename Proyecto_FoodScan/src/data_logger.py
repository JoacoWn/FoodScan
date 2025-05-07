from datetime import datetime
from pymongo import MongoClient
from pymongo.errors import PyMongoError
from config import MONGO_URI, MONGO_DB_NAME, MONGO_COLLECTION_NAME

class DataLogger:
    def __init__(self):
        try:
            self.client = MongoClient(MONGO_URI)
            self.client.admin.command('ping')  # Verificar conexión
            self.db = self.client[MONGO_DB_NAME]
            self.collection = self.db[MONGO_COLLECTION_NAME]
            print(f"✅ Conectado a MongoDB local en {MONGO_URI}")
        except Exception as e:
            print(f"❌ ERROR al conectar a MongoDB: {e}")
            self.client = None
            self.collection = None

    def log_meal(self, image_name, section, food_items):
        if self.collection is None:
            print("❌ No hay conexión a MongoDB activa.")
            return False

        doc = {
            "timestamp": datetime.now(),
            "image_name": image_name,
            "seccion": section,
            "alimentos": food_items
        }

        try:
            result = self.collection.insert_one(doc)
            print(f"[{image_name}] 🍽️ Comida registrada en MongoDB con ID: {result.inserted_id}")
            return True
        except PyMongoError as e:
            print(f"❌ Error de PyMongo: {e}")
            return False
        except Exception as e:
            print(f"❌ Error inesperado al guardar: {e}")
            return False

    def close_connection(self):
        if self.client is not None:
            self.client.close()
            print("🔌 Conexión a MongoDB cerrada.")
