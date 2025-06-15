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

    if normalized_name in FOOD_DATABASE:
        return FOOD_DATABASE[normalized_name]

    for db_food_name, db_data in FOOD_DATABASE.items():
        if normalized_name in normalize_food_name(db_food_name) or normalize_food_name(db_food_name) in normalized_name:
            return db_data

    return None


def recalculate_meal_totals(analysis_result):
    """
    Recalcula los totales nutricionales (calorías, proteínas, grasas, carbohidratos)
    para una comida, basándose en las cantidades ajustadas por el usuario (o estimadas).
    Modifica el diccionario analysis_result en su lugar.
    """
    if not analysis_result.get("alimentos"):
        analysis_result["resumen_general"] = "No hay alimentos en esta comida."
        analysis_result["calorias_totales"] = 0.0
        analysis_result["proteinas_totales"] = 0.0
        analysis_result["grasas_totales"] = 0.0
        analysis_result["carbohidratos_totales"] = 0.0
        return

    total_calorias = 0.0
    total_proteinas = 0.0
    total_grasas = 0.0
    total_carbohidratos = 0.0

    for item in analysis_result["alimentos"]:
        cantidad_final_g = item.get("cantidad_usuario_g", item.get("cantidad_original_g", 0))

        if not item.get("nutrientes_por_100g"):
            item["nutrientes_por_100g"] = {
                "calorias": 0.0, "proteinas": 0.0, "grasas": 0.0, "carbohidratos": 0.0
            }

        factor_cantidad = cantidad_final_g / 100.0 if cantidad_final_g > 0 else 0.0

        item["calorias_totales_calculadas"] = round(item["nutrientes_por_100g"].get("calorias", 0.0) * factor_cantidad,
                                                    2)
        item["proteinas_totales_calculadas"] = round(
            item["nutrientes_por_100g"].get("proteinas", 0.0) * factor_cantidad, 2)
        item["grasas_totales_calculadas"] = round(item["nutrientes_por_100g"].get("grasas", 0.0) * factor_cantidad, 2)
        item["carbohidratos_totales_calculadas"] = round(
            item["nutrientes_por_100g"].get("carbohidratos", 0.0) * factor_cantidad, 2)

        total_calorias += item["calorias_totales_calculadas"]
        total_proteinas += item["proteinas_totales_calculadas"]
        total_grasas += item["grasas_totales_calculadas"]
        total_carbohidratos += item["carbohidratos_totales_calculadas"]

    analysis_result["calorias_totales"] = round(total_calorias, 2)
    analysis_result["proteinas_totales"] = round(total_proteinas, 2)
    analysis_result["grasas_totales"] = round(total_grasas, 2)
    analysis_result["carbohidratos_totales"] = round(total_carbohidratos, 2)
    analysis_result["resumen_general"] = (
        f"Calorías: {analysis_result['calorias_totales']} kcal, "
        f"Proteínas: {analysis_result['proteinas_totales']} g, "
        f"Grasas: {analysis_result['grasas_totales']} g, "
        f"Carbohidratos: {analysis_result['carbohidratos_totales']} g"
    )