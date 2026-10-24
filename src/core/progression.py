from src.tools.sql_tools import obtener_ultima_sesion, normalizar_ejercicio

def datos_para_progresion(ejercicio):
    """Devuelve datos para que el LLM razone sobre la progresión; no impone una respuesta fija."""
    e = normalizar_ejercicio(ejercicio)
    last = obtener_ultima_sesion(e)
    if not last:
        return {"ok": False, "exercise": e, "reason": "No existe una sesión registrada para este ejercicio."}
    return {"ok": True, "source": "SQLite", "exercise": e, "last_session": last,
            "guardrails": ["No afirmar que se conoce el programa completo, el dolor, la fatiga o el RIR objetivo si no se han aportado.",
                           "Proponer una progresión condicional y explicar la evidencia disponible.",
                           "No aumentar carga automáticamente si la sesión fue muy próxima al fallo o la técnica no fue confirmada."]}
