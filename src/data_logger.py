import os
from datetime import datetime
from pymongo import MongoClient, errors
from bson.objectid import ObjectId
from src.config import MONGO_URI, MONGO_DB_NAME, MONGO_COLLECTION_NAME

class DataLogger:
    def __init__(self):
        self.mongo_uri = MONGO_URI
        self.db_name = MONGO_DB_NAME
        self.collection_name = MONGO_COLLECTION_NAME

        if not self.mongo_uri:
            raise ValueError("MONGO_URI no está configurado. Asegúrate de tener un archivo .env o configurarlo en config.py.")
        self.db = None
        self.client = None
        self.collection = None
        self._connect_to_mongodb()

    def _connect_to_mongodb(self):
        """Intenta conectar a MongoDB."""
        try:
            self.client = MongoClient(self.mongo_uri)
            self.client.admin.command('ping')
            self.db = self.client[self.db_name]
            self.collection = self.db[self.collection_name]
            print("Conexión a MongoDB establecida con éxito.")
        except errors.ConnectionFailure as e:
            print(f"Error de conexión a MongoDB: {e}")
            self.db = None
            self.client = None
            self.collection = None
        except Exception as e:
            print(f"Ocurrió un error inesperado al conectar a MongoDB: {e}")
            self.db = None
            self.client = None
            self.collection = None

    def log_food_entry(self, analysis_result, image_name, meal_type, log_time=None):
        """
        Registra una entrada de comida en la base de datos.
        analysis_result debe ser un diccionario con el formato esperado.
        """
        if self.collection is None:
            print("Error: No hay conexión a la base de datos para registrar la entrada.")
            return False

        if log_time is None:
            log_time = datetime.now()

        if "alimentos" not in analysis_result:
            print("Error: 'alimentos' no encontrado en analysis_result.")
            return False

        food_entry = {
            "timestamp": log_time,
            "image_name": image_name,
            "meal_type": meal_type,
            "alimentos": analysis_result.get("alimentos", []),
            "resumen_general": analysis_result.get("resumen_general", "Sin resumen."),
            "calorias_totales_comida": analysis_result.get("calorias_totales", 0.0),
            "proteinas_totales_comida": analysis_result.get("proteinas_totales", 0.0),
            "grasas_totales_comida": analysis_result.get("grasas_totales", 0.0),
            "carbohidratos_totales_comida": analysis_result.get("carbohidratos_totales", 0.0)
        }

        try:
            result = self.collection.insert_one(food_entry)
            print(f"Entrada de comida registrada con ID: {result.inserted_id}")
            return True
        except Exception as e:
            print(f"Error al registrar la entrada de comida: {e}")
            return False

    def get_food_entries(self, start_date=None, end_date=None, meal_type=None, query_filter=None):
        """
        Obtiene entradas de comida de la base de datos con filtros opcionales.
        Devuelve una lista de diccionarios, tal como están en MongoDB.
        La conversión de ObjectId/datetime a string se hará en el Flask app.py.
        start_date, end_date: objetos datetime para filtrar por rango de fecha.
        meal_type: string para filtrar por tipo de comida (ej. "desayuno").
        query_filter: diccionario adicional para filtros personalizados (ej. {"user": "nombre"}).
        """
        if self.collection is None:
            print("Error: No hay conexión a la base de datos para obtener entradas.")
            return []

        query = {}

        if query_filter:
            query.update(query_filter)

        if start_date and end_date:
            query["timestamp"] = {"$gte": start_date, "$lte": end_date}
        elif start_date:
            query["timestamp"] = {"$gte": start_date}
        elif end_date:
            query["timestamp"] = {"$lte": end_date}

        if meal_type:
            query["meal_type"] = meal_type

        try:
            # Ordenar por timestamp descendente para ver las más recientes primero
            entries = list(self.collection.find(query).sort("timestamp", -1))
            return entries
        except Exception as e:
            print(f"Error al obtener entradas de comida: {e}")
            return []

    def get_summary_by_date(self, target_date):
        """
        Calcula el resumen nutricional (calorías, proteínas, grasas, carbohidratos)
        para un día específico.
        target_date: objeto datetime que representa el día a resumir.
        """
        if self.collection is None:
            print("Error: No hay conexión a la base de datos para obtener el resumen.")
            return None

        start_of_day = datetime(target_date.year, target_date.month, target_date.day, 0, 0, 0)
        end_of_day = datetime(target_date.year, target_date.month, target_date.day, 23, 59, 59, 999999)

        query = {
            "timestamp": {"$gte": start_of_day, "$lte": end_of_day}
        }

        try:
            daily_entries = self.collection.find(query)

            total_calorias = 0.0
            total_proteinas = 0.0
            total_grasas = 0.0
            total_carbohidratos = 0.0

            for entry in daily_entries:
                total_calorias += entry.get("calorias_totales_comida", 0.0)
                total_proteinas += entry.get("proteinas_totales_comida", 0.0)
                total_grasas += entry.get("grasas_totales_comida", 0.0)
                total_carbohidratos += entry.get("carbohidratos_totales_comida", 0.0)

            return {
                "date": target_date.strftime("%Y-%m-%d"),
                "total_calorias": round(total_calorias, 2),
                "total_proteinas": round(total_proteinas, 2),
                "total_grasas": round(total_grasas, 2),
                "total_carbohidratos": round(total_carbohidratos, 2)
            }
        except Exception as e:
            print(f"Error al obtener el resumen diario: {e}")
            return None

    def delete_food_entry(self, entry_id):
        """
        Elimina una entrada de comida de la base de datos por su _id.
        entry_id: El ID de la entrada a eliminar (puede ser un string o ObjectId).
        """
        if self.collection is None:
            print("Error: No hay conexión a la base de datos para eliminar la entrada.")
            return False

        try:
            if not isinstance(entry_id, ObjectId):
                entry_id = ObjectId(str(entry_id))

            result = self.collection.delete_one({"_id": entry_id})
            if result.deleted_count == 1:
                print(f"Entrada con ID {entry_id} eliminada con éxito.")
                return True
            else:
                print(f"No se encontró la entrada con ID {entry_id} para eliminar.")
                return False
        except errors.InvalidId:
            print(f"Error: El ID '{entry_id}' no es un ObjectId válido.")
            return False
        except Exception as e:
            print(f"Error al eliminar la entrada de comida: {e}")
            return False

    def close_connection(self):
        """Cierra la conexión a la base de datos MongoDB."""
        if self.client:
            self.client.close()
            print("Conexión a MongoDB cerrada.")