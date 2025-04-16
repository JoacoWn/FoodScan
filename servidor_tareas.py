# servidor_tareas.py
from flask import Flask, request, jsonify
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Reemplaza con tu URI de MongoDB (Mongo Atlas o EC2 local)
app.config["MONGO_URI"] = "mongodb+srv://jarriagada13:mVSgVtnMhuEtWs7q@cluster0.uguaj1f.mongodb.net/taller_computacion?retryWrites=true&w=majority"

mongo = PyMongo(app)
coleccion_tareas = mongo.db.tareas

# Rutas

# Obtener todas las tareas por RUT
@app.route('/todos/<rut>', methods=['GET'])
def obtener_tareas(rut):
    tareas = []
    for tarea in coleccion_tareas.find({"rut": rut}):
        tareas.append({
            "id": str(tarea["_id"]),
            "titulo": tarea["titulo"],
            "descripcion": tarea["descripcion"],
            "completada": tarea["completada"]
        })
    return jsonify({"tareas": tareas})

# Crear nueva tarea
@app.route('/todos', methods=['POST'])
def agregar_tarea():
    datos = request.get_json()
    if not all(k in datos for k in ("rut", "titulo", "descripcion")):
        return jsonify({"error": "Faltan campos obligatorios"}), 400

    nueva_tarea = {
        "rut": datos["rut"],
        "titulo": datos["titulo"],
        "descripcion": datos["descripcion"],
        "completada": False
    }
    resultado = coleccion_tareas.insert_one(nueva_tarea)
    return jsonify({"id": str(resultado.inserted_id)}), 201

# Actualizar tarea
@app.route('/todos/<id_tarea>', methods=['PUT'])
def actualizar_tarea(id_tarea):
    datos = request.get_json()
    campos = {}
    if "titulo" in datos:
        campos["titulo"] = datos["titulo"]
    if "descripcion" in datos:
        campos["descripcion"] = datos["descripcion"]
    if "completada" in datos:
        campos["completada"] = datos["completada"]
    if not campos:
        return jsonify({"error": "No hay datos para actualizar"}), 400

    resultado = coleccion_tareas.update_one(
        {"_id": ObjectId(id_tarea)},
        {"$set": campos}
    )
    if resultado.matched_count == 0:
        return jsonify({"error": "Tarea no encontrada"}), 404
    return jsonify({"resultado": "Tarea actualizada correctamente"})

# Eliminar tarea
@app.route('/todos/<id_tarea>', methods=['DELETE'])
def eliminar_tarea(id_tarea):
    resultado = coleccion_tareas.delete_one({"_id": ObjectId(id_tarea)})
    if resultado.deleted_count == 0:
        return jsonify({"error": "Tarea no encontrada"}), 404
    return jsonify({"resultado": "Tarea eliminada correctamente"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8081, debug=True)
