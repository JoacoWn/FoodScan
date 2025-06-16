# src/food_utils.py
# CAMBIO: Importar food_database desde el paquete src
from src.food_database import FOOD_DATABASE


def normalize_food_name(name):
    """Normaliza un nombre de alimento para facilitar la búsqueda."""
    return name.lower().strip()


def get_food_data_from_db(food_name):
    """
    Busca un alimento en FOOD_DATABASE y devuelve sus datos nutricionales.
    Intenta una coincidencia exacta normalizada y luego una parcial.
    """
    normalized_name = normalize_food_name(food_name)

    # Coincidencia exacta primero
    if normalized_name in FOOD_DATABASE:
        return FOOD_DATABASE[normalized_name]

    # Coincidencia parcial: si el nombre de Gemini está contenido en la clave, o viceversa
    # Esto puede devolver la primera coincidencia, lo cual es razonable para una base de datos de este tipo.
    for db_food_name, db_data in FOOD_DATABASE.items():
        if normalized_name in normalize_food_name(db_food_name) or normalize_food_name(db_food_name) in normalized_name:
            return db_data

    return None

# NOTA IMPORTANTE: La función 'recalculate_meal_totals' ha sido eliminada.
# La lógica de cálculo de totales ahora reside completamente en 'app.py'
# para integrar los resultados de Gemini con tu base de datos local de manera eficiente.