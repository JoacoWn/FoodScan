import os

from datetime import datetime

from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, PyMongoError

from src.config import MONGO_URI, MONGO_DB_NAME, MONGO_COLLECTION_NAME


class DataLogger:
    def __init__(self):
        self.client = None
        self.db = None
        self.collection = None
        self._connect_to_mongodb()

    def _connect_to_mongodb(self):
        """Intenta conectar a la base de datos MongoDB."""
        try:
            self.client = MongoClient(MONGO_URI)
            # La siguiente línea forzará la conexión para verificarla
            self.client.admin.command('ping')
            self.db = self.client[MONGO_DB_NAME]
            self.collection = self.db[MONGO_COLLECTION_NAME]
            print(f"Conexión a MongoDB establecida: {MONGO_URI} | Base de datos: {MONGO_DB_NAME} | Colección: {MONGO_COLLECTION_NAME}")
        except ConnectionFailure as e:
            print(f"Error de conexión a MongoDB: {e}")
            self.client = None
            self.db = None
            self.collection = None
        except PyMongoError as e:
            print(f"Error general de PyMongo al conectar: {e}")
            self.client = None
            self.db = None
            self.collection = None
        except Exception as e:
            print(f"Error inesperado al conectar a MongoDB: {e}")
            self.client = None
            self.db = None
            self.collection = None

    def log_infraction(self, image_name, infraction_data):
        """
        Registra una infracción en la colección de MongoDB.
        infraction_data debe ser un diccionario con los detalles de la infracción.
        """
        if not self.collection:
            print("No hay conexión activa a MongoDB. No se pudo registrar la infracción.")
            return False

        # Asegurarse de que infraction_data sea un diccionario
        if not isinstance(infraction_data, dict):
            print(f"Datos de infracción inválidos para {image_name}: {infraction_data}")
            return False

        # Preparar el documento a insertar con los nuevos campos
        document = {
            "timestamp": datetime.now(),
            "image_name": image_name,
            "infraccion_detectada": infraction_data.get("is_illegally_parked", False), # Cambiado a 'is_illegally_parked' para coincidir con GeminiClient
            "tipo_infraccion": infraction_data.get("reason", "desconocido"), # Cambiado a 'reason'
            "patente": infraction_data.get("detected_license_plate", "no_visible"), # Cambiado a 'detected_license_plate'
            "color_vehiculo": infraction_data.get("color_vehiculo", "desconocido"), # Nuevo campo
            "marca_vehiculo": infraction_data.get("marca_vehiculo", "desconocida"), # Nuevo campo
            "confianza_infraccion": infraction_data.get("illegal_parking_confidence", 0.0), # Cambiado a 'illegal_parking_confidence'
            "confianza_patente": infraction_data.get("license_plate_confidence", 0.0) # Cambiado a 'license_plate_confidence'
        }

        try:
            result = self.collection.insert_one(document)
            print(f"Infracción para {image_name} registrada en MongoDB con ID: {result.inserted_id}")
            return True
        except PyMongoError as e:
            print(f"Error al insertar la infracción para {image_name} en MongoDB: {e}")
            return False
        except Exception as e:
            print(f"Error inesperado al registrar la infracción para {image_name}: {e}")
            return False

    def close_connection(self):
        """Cierra la conexión con MongoDB."""
        if self.client:
            self.client.close()
            print("Conexión a MongoDB cerrada.")