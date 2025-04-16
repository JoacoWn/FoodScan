# cliente_tareas.py
import requests

class ML_TodoCliente:
    def __init__(self, url_base, rut_usuario):
        self.url_base = url_base
        self.rut = rut_usuario

    def ver_tareas(self):
        try:
            resp = requests.get(f"{self.url_base}/todos/{self.rut}")
            return resp.json().get("tareas", [])
        except Exception as e:
            print(f"Error al obtener tareas: {e}")
            return []

    def agregar_tarea(self, titulo, descripcion):
        payload = {
            "rut": self.rut,
            "titulo": titulo,
            "descripcion": descripcion
        }
        try:
            resp = requests.post(f"{self.url_base}/todos", json=payload)
            return resp.json()
        except Exception as e:
            print(f"Error al agregar tarea: {e}")
            return {}

    def actualizar_tarea(self, id_tarea, titulo=None, descripcion=None, completada=None):
        payload = {}
        if titulo: payload["titulo"] = titulo
        if descripcion: payload["descripcion"] = descripcion
        if completada is not None: payload["completada"] = completada
        try:
            resp = requests.put(f"{self.url_base}/todos/{id_tarea}", json=payload)
            return resp.json()
        except Exception as e:
            print(f"Error al actualizar tarea: {e}")
            return {}

    def eliminar_tarea(self, id_tarea):
        try:
            resp = requests.delete(f"{self.url_base}/todos/{id_tarea}")
            return resp.json()
        except Exception as e:
            print(f"Error al eliminar tarea: {e}")
            return {}

def mostrar_tareas(lista):
    print("\n📋 Tareas:")
    for t in lista:
        estado = "✅" if t['completada'] else "❌"
        print(f"ID: {t['id']} - {estado} {t['titulo']} | {t['descripcion']}")

if __name__ == '__main__':
    RUT = input("Ingrese su RUT (sin puntos ni guión): ").strip()
    cliente = ML_TodoCliente("http://54.83.182.183:8081", RUT)

    while True:
        print("\n--- Menú ---")
        print("1. Ver tareas")
        print("2. Agregar tarea")
        print("3. Actualizar tarea")
        print("4. Eliminar tarea")
        print("5. Salir")
        op = input("Seleccione opción: ")

        if op == '1':
            tareas = cliente.ver_tareas()
            mostrar_tareas(tareas)
        elif op == '2':
            titulo = input("Título: ")
            descripcion = input("Descripción: ")
            print(cliente.agregar_tarea(titulo, descripcion))
        elif op == '3':
            id_tarea = input("ID de la tarea: ")
            nueva_desc = input("Nueva descripción (vacío si no): ")
            nuevo_titulo = input("Nuevo título (vacío si no): ")
            estado = input("¿Completada? (s/n): ").lower()
            completada = True if estado == 's' else False if estado == 'n' else None
            print(cliente.actualizar_tarea(id_tarea, nuevo_titulo or None, nueva_desc or None, completada))
        elif op == '4':
            id_tarea = input("ID de la tarea: ")
            print(cliente.eliminar_tarea(id_tarea))
        elif op == '5':
            print("Hasta la próxima 🚀")
            break
        else:
            print("Opción inválida.")
