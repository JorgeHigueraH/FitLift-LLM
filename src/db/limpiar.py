"""
Herramienta de inspección segura. No borra registros automáticamente.
Uso: python limpiar.py
"""
from src.tools.sql_tools import DB_PATH, inicializar_db
import sqlite3

def inspeccionar_historial():
    inicializar_db()
    with sqlite3.connect(str(DB_PATH)) as conn:
        conn.row_factory = sqlite3.Row
        rows = conn.execute("""
            SELECT id, fecha, ejercicio, peso, series, repeticiones, rir, creado_en
            FROM historial ORDER BY fecha DESC, id DESC LIMIT 100
        """).fetchall()
    if not rows:
        print("No hay registros.")
        return
    for row in rows:
        print(dict(row))
    print("\nNo se ha borrado ni modificado ningún dato.")
    print("Haz una copia de data/fitlift.db antes de corregir manualmente registros incorrectos.")

if __name__ == "__main__":
    inspeccionar_historial()
