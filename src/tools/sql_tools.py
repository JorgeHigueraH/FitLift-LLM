"""Herramientas SQL: los datos personales de entrenamiento solo salen de SQLite."""
import sqlite3
from pathlib import Path
from datetime import date

ROOT = Path(__file__).resolve().parents[2]
DB_PATH = ROOT / "data" / "fitlift.db"
ALIASES = {
    "press de banca": "press banca", "banca": "press banca", "press banca": "press banca",
    "sentadillas": "sentadilla", "sentadilla": "sentadilla", "squat": "sentadilla",
    "peso muerto rumano": "peso muerto rumano", "peso muerto": "peso muerto",
    "leg press": "prensa", "prensa de piernas": "prensa", "prensa": "prensa",
    "press militar": "press militar", "press de hombros": "press militar",
    "remo": "remo", "curl femoral": "curl femoral", "hip thrust": "hip thrust",
    "extensión de cuádriceps": "extensión de cuádriceps", "extension de cuadriceps": "extensión de cuádriceps",
    "elevación de talones": "elevación de talones", "gemelos": "elevación de talones",
}

def ruta_db(): return str(DB_PATH.resolve())
def normalizar_ejercicio(e):
    s = " ".join(str(e or "").lower().strip().split())
    return ALIASES.get(s, s)

def _connect():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    c = sqlite3.connect(str(DB_PATH), timeout=15)
    c.row_factory = sqlite3.Row
    c.execute("PRAGMA foreign_keys=ON")
    return c

def inicializar_db():
    """Realiza una migración segura unificando esquemas y eliminando la restricción UNIQUE."""
    c = _connect()
    try:
        with c:
            schema = c.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='historial'").fetchone()
            if schema and "UNIQUE(fecha,ejercicio)" in schema[0].replace(" ", "").replace("\n", ""):
                c.execute("ALTER TABLE historial RENAME TO historial_old")
            
            c.execute("""CREATE TABLE IF NOT EXISTS historial (
                id INTEGER PRIMARY KEY AUTOINCREMENT, fecha TEXT NOT NULL, ejercicio TEXT NOT NULL,
                peso REAL NOT NULL CHECK(peso>0), series INTEGER NOT NULL CHECK(series>0),
                repeticiones INTEGER NOT NULL CHECK(repeticiones>0), rir INTEGER NOT NULL CHECK(rir BETWEEN 0 AND 10),
                creado_en TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP)""")
            c.execute("CREATE INDEX IF NOT EXISTS idx_historial_ej_fecha ON historial(ejercicio,fecha DESC,id DESC)")

            tables = [r['name'] for r in c.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()]
            
            if "historial_old" in tables:
                c.execute("INSERT INTO historial (fecha, ejercicio, peso, series, repeticiones, rir, creado_en) SELECT fecha, ejercicio, peso, series, repeticiones, rir, creado_en FROM historial_old")
                c.execute("DROP TABLE historial_old")
                
            if "sets" in tables and "workouts" in tables:
                c.execute("""INSERT INTO historial (fecha, ejercicio, peso, series, repeticiones, rir)
                             SELECT w.fecha, s.ejercicio, s.peso_kg, s.series, s.repeticiones, s.rir
                             FROM sets s JOIN workouts w ON s.workout_id = w.id""")
                c.execute("DROP TABLE sets")
                c.execute("DROP TABLE workouts")
    finally:
        c.close()

def _rows(sql, args=()):
    c = _connect()
    try:
        with c:
            return [dict(r) for r in c.execute(sql, args).fetchall()]
    finally:
        c.close()

def listar_ejercicios():
    rows = _rows("SELECT ejercicio, COUNT(*) AS registros FROM historial GROUP BY ejercicio ORDER BY ejercicio COLLATE NOCASE")
    return {"source": "SQLite", "database": ruta_db(), "count": len(rows), "exercises": rows}

def consultar_todo_historial():
    rows = _rows("SELECT id,fecha,ejercicio,peso,series,repeticiones,rir FROM historial ORDER BY fecha DESC,id DESC")
    return {"source": "SQLite", "database": ruta_db(), "session_count": len(rows), "sessions": rows}

def consultar_historial_ejercicio(ejercicio, limite=20):
    e = normalizar_ejercicio(ejercicio)
    rows = _rows("SELECT id,fecha,ejercicio,peso,series,repeticiones,rir FROM historial WHERE lower(trim(ejercicio))=lower(?) ORDER BY fecha DESC,id DESC LIMIT ?", (e, max(1, min(int(limite), 200))))
    return {"source": "SQLite", "exercise": e, "count": len(rows), "sessions": rows}

def consultar_estadisticas():
    total = _rows("SELECT COUNT(*) AS n, COUNT(DISTINCT fecha) AS days, MIN(fecha) AS first_date, MAX(fecha) AS last_date FROM historial")[0]
    exercises = _rows("SELECT ejercicio, COUNT(*) AS registros FROM historial GROUP BY ejercicio ORDER BY registros DESC, ejercicio")
    return {"source": "SQLite", "database": ruta_db(), "summary": total, "by_exercise": exercises}

def consultar_mejor_carga(ejercicio):
    e = normalizar_ejercicio(ejercicio)
    rows = _rows("SELECT id,fecha,ejercicio,peso,series,repeticiones,rir FROM historial WHERE lower(trim(ejercicio))=lower(?) ORDER BY peso DESC,repeticiones DESC,fecha DESC LIMIT 1", (e,))
    return {"source": "SQLite", "exercise": e, "best_load": rows[0] if rows else None, "note": "La mayor carga registrada no equivale necesariamente a un 1RM medido."}

def obtener_ultima_sesion(ejercicio):
    e = normalizar_ejercicio(ejercicio)
    rows = _rows("SELECT id,fecha,ejercicio,peso,series,repeticiones,rir FROM historial WHERE lower(trim(ejercicio))=lower(?) ORDER BY fecha DESC,id DESC LIMIT 1", (e,))
    return rows[0] if rows else None

def registrar_entrenamiento(fecha, ejercicio, peso, series, repeticiones, rir):
    try:
        date.fromisoformat(str(fecha))
        e = normalizar_ejercicio(ejercicio)
        w, sets, reps, r = float(peso), int(series), int(repeticiones), int(rir)
        if not e or w <= 0 or sets <= 0 or reps <= 0 or not 0 <= r <= 10:
            return {"ok": False, "error": "Datos inválidos: peso y series/repeticiones deben ser positivos; RIR entre 0 y 10."}
        
        c = _connect()
        try:
            with c:
                cursor = c.execute("""INSERT INTO historial(fecha,ejercicio,peso,series,repeticiones,rir) VALUES(?,?,?,?,?,?)""",
                    (str(fecha), e, w, sets, reps, r))
                rowid = cursor.lastrowid
                
                row = c.execute("SELECT fecha,ejercicio,peso,series,repeticiones,rir FROM historial WHERE id=?", (rowid,)).fetchone()
                if not row: return {"ok": False, "error": "La escritura no se pudo verificar en SQLite tras la inserción."}
                return {"ok": True, "operation": "inserted_record", "verified": dict(row), "database": ruta_db(), "warning": None}
        finally:
            c.close()
    except Exception as exc:
        return {"ok": False, "error": f"{type(exc).__name__}: {exc}"}

def previsualizar_borrado(fecha=None, ejercicios=None, todos=False):
    ejercicios = [normalizar_ejercicio(x) for x in (ejercicios or []) if str(x).strip()]
    if not todos and not fecha and not ejercicios:
        return {"ok": False, "error": "Filtro insuficiente: especifica fecha, ejercicios o todos=True.", "records": []}
    clauses, params = [], []
    if not todos and fecha:
        try: date.fromisoformat(str(fecha))
        except ValueError: return {"ok": False, "error": "Fecha inválida; usa YYYY-MM-DD.", "records": []}
        clauses.append("fecha=?"); params.append(str(fecha))
    if not todos and ejercicios:
        clauses.append("lower(trim(ejercicio)) IN (" + ",".join("?" for _ in ejercicios) + ")")
        params.extend([x.lower() for x in ejercicios])
    where = " AND ".join(clauses) if clauses else "1=1"
    rows = _rows(f"SELECT id,fecha,ejercicio,peso,series,repeticiones,rir FROM historial WHERE {where} ORDER BY fecha DESC,id DESC", tuple(params))
    return {"ok": True, "operation": "preview_delete", "database": ruta_db(), "count": len(rows), "records": rows,
            "scope": {"date": fecha, "exercises": ejercicios, "all_records": bool(todos)}}

def borrar_registros_por_ids(ids):
    clean = sorted({int(x) for x in (ids or []) if str(x).isdigit()})
    if not clean:
        return {"ok": False, "error": "No hay IDs válidos para borrar.", "deleted_count": 0}
    placeholders = ",".join("?" for _ in clean)
    
    c = _connect()
    try:
        with c:
            before = [dict(r) for r in c.execute(
                f"SELECT id,fecha,ejercicio,peso,series,repeticiones,rir FROM historial WHERE id IN ({placeholders}) ORDER BY id", clean).fetchall()]
            if len(before) != len(clean):
                return {"ok": False, "error": "Los registros han cambiado desde la previsualización; no se borró nada.", "deleted_count": 0}
            c.execute(f"DELETE FROM historial WHERE id IN ({placeholders})", clean)
            remaining = c.execute(f"SELECT COUNT(*) FROM historial WHERE id IN ({placeholders})", clean).fetchone()[0]
        return {"ok": remaining == 0, "operation": "delete", "deleted_count": len(before) if remaining == 0 else 0,
                "deleted_records": before if remaining == 0 else [], "remaining_matching_ids": remaining, "database": ruta_db()}
    finally:
        c.close()