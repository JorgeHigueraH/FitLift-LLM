import sqlite3
import os
from datetime import datetime, timedelta

def init_db():
    os.makedirs('data', exist_ok=True)
    db_path = 'data/fitlift.db'
    
    conexion = sqlite3.connect(db_path)
    cursor = conexion.cursor()

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS workouts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        fecha DATE NOT NULL,
        grupo_muscular TEXT NOT NULL,
        fatiga_percebida INTEGER CHECK(fatiga_percebida BETWEEN 1 AND 10)
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS sets (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        workout_id INTEGER,
        ejercicio TEXT NOT NULL,
        peso_kg REAL NOT NULL,
        series INTEGER NOT NULL,
        repeticiones INTEGER NOT NULL,
        rir INTEGER,
        FOREIGN KEY(workout_id) REFERENCES workouts(id)
    )
    ''')


    cursor.execute("SELECT COUNT(*) FROM workouts")
    if cursor.fetchone()[0] == 0:
        print("Inyectando historial de prueba para Press Banca...")
        
        fecha_1 = (datetime.now() - timedelta(days=14)).strftime('%Y-%m-%d')
        cursor.execute("INSERT INTO workouts (fecha, grupo_muscular, fatiga_percebida) VALUES (?, ?, ?)", (fecha_1, 'Pecho', 6))
        w_id_1 = cursor.lastrowid
        cursor.execute("INSERT INTO sets (workout_id, ejercicio, peso_kg, series, repeticiones, rir) VALUES (?, ?, ?, ?, ?, ?)", (w_id_1, 'Press Banca', 110.0, 3, 4, 2))

        fecha_2 = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
        cursor.execute("INSERT INTO workouts (fecha, grupo_muscular, fatiga_percebida) VALUES (?, ?, ?)", (fecha_2, 'Pecho', 7))
        w_id_2 = cursor.lastrowid
        cursor.execute("INSERT INTO sets (workout_id, ejercicio, peso_kg, series, repeticiones, rir) VALUES (?, ?, ?, ?, ?, ?)", (w_id_2, 'Press Banca', 110.0, 3, 5, 1))
        
        fecha_3 = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
        cursor.execute("INSERT INTO workouts (fecha, grupo_muscular, fatiga_percebida) VALUES (?, ?, ?)", (fecha_3, 'Pecho', 8))
        w_id_3 = cursor.lastrowid
        cursor.execute("INSERT INTO sets (workout_id, ejercicio, peso_kg, series, repeticiones, rir) VALUES (?, ?, ?, ?, ?, ?)", (w_id_3, 'Press Banca', 110.0, 3, 6, 1))

        conexion.commit()
        print("Datos inyectados correctamente.")
    else:
        print("La base de datos ya existe y tiene registros.")

    conexion.close()
    print(f"Base de datos operativa en: {db_path}")

if __name__ == "__main__":
    init_db()