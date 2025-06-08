from datetime import datetime
from pymongo import MongoClient
from pymongo.errors import PyMongoError
from bson.objectid import ObjectId
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

    # ASEGÚRATE DE QUE ESTA LÍNEA ESTÉ ASÍ EN TU data_logger.py
    def log_meal(self, image_name, section, food_items, user=None):
        if self.collection is None:
            print("X No hay conexión a MongoDB activa.")
            return False

        doc = {
            "timestamp": datetime.now(),
            "image_name": image_name,
            "seccion": section,
            "alimentos": food_items,
            "user": user  # Añadir el campo de usuario
        }

        try:
            result = self.collection.insert_one(doc)
            print(f"[{image_name}] Comida registrada en MongoDB con ID: {result.inserted_id}")
            return True
        except PyMongoError as e:
            print(f"❌ Error de PyMongo: {e}")
            return False
        except Exception as e:
            print(f"❌ Error inesperado al guardar: {e}")
            return False

    def delete_meal(self, meal_id):
        if self.collection is None:
            print("X No hay conexión a MongoDB activa.")
            return False
        try:
            if not isinstance(meal_id, ObjectId):
                meal_id = ObjectId(meal_id)

            result = self.collection.delete_one({"_id": meal_id})
            if result.deleted_count == 1:
                print(f"✅ Registro con ID {meal_id} eliminado exitosamente.")
                return True
            else:
                print(f"X No se encontró el registro con ID {meal_id}.")
                return False
        except PyMongoError as e:
            print(f"❌ Error de PyMongo al eliminar: {e}")
            return False
        except Exception as e:
            print(f"❌ Error inesperado al eliminar: {e}")
            return False

    def close_connection(self):
        if self.client is not None:
            self.client.close()
            print("✅ Conexión a MongoDB cerrada.")