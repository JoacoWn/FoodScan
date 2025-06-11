from flask import Flask, request, jsonify
import sqlite3
from datetime import datetime

app = Flask(__name__)
DB_NAME = "RAK11200_Joan.db"  # Usa tu nombre de equipo


def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
                   CREATE TABLE IF NOT EXISTS mediciones
                   (
                       id
                       INTEGER
                       PRIMARY
                       KEY
                       AUTOINCREMENT,
                       time
                       INTEGER,
                       medicion
                       INTEGER,
                       nombrenodo
                       TEXT,
                       hora_recepcion
                       TEXT
                   )
                   ''')
    conn.commit()
    conn.close()


@app.route('/api/data', methods=['POST'])
def save_data():
    data = request.get_json()
    hora_recepcion = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
                   INSERT INTO mediciones (time, medicion, nombrenodo, hora_recepcion)
                   VALUES (?, ?, ?, ?)
                   ''', (data['time'], data['medicion'], data['nombrenodo'], hora_recepcion))
    conn.commit()
    conn.close()

    print(f"Dato recibido: {data} | Hora recepción: {hora_recepcion}")
    return jsonify({"status": "success"}), 200


if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5000)