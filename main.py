"""FitLift-LLM con LangGraph: planificación dinámica, herramientas verificables y borrado con aprobación."""
from __future__ import annotations

import json
import os
import re
from datetime import date, datetime
from pathlib import Path
from typing import Any, Literal, TypedDict

from dotenv import load_dotenv
from langchain_ollama import ChatOllama
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, START, StateGraph
from langgraph.types import Command, interrupt

from src.tools.sql_tools import (
    inicializar_db, listar_ejercicios, consultar_todo_historial,
    consultar_historial_ejercicio, consultar_estadisticas, consultar_mejor_carga,
    registrar_entrenamiento, ruta_db, previsualizar_borrado, borrar_registros_por_ids,
)
from src.tools.rag_tools import buscar_evidencia, estado_coleccion
from src.core.progression import datos_para_progresion

ROOT = Path(__file__).resolve().parent
load_dotenv(ROOT / ".env")
MODEL = os.getenv("FITLIFT_MODEL", "qwen2.5:7b")
MAX_HISTORY = int(os.getenv("FITLIFT_MAX_HISTORY", "16"))
MAX_TOOL_STEPS = 3

TOOLS = [
 {"name":"current_date","description":"Fecha/hora local actual para preguntas temporales.","arguments":{"type":"object","properties":{},"required":[]}},
 {"name":"training_history_all","description":"Consulta todos los entrenamientos reales en SQLite. Para qué entrenó hoy, todos los ejercicios o historial completo.","arguments":{"type":"object","properties":{},"required":[]}},
 {"name":"training_exercises","description":"Lista nombres de ejercicios presentes realmente en SQLite y número de registros.","arguments":{"type":"object","properties":{},"required":[]}},
 {"name":"training_statistics","description":"Estadísticas exactas: número de registros, fechas y ejercicios.","arguments":{"type":"object","properties":{},"required":[]}},
 {"name":"exercise_history","description":"Historial de un ejercicio concreto.","arguments":{"type":"object","properties":{"exercise":{"type":"string"},"limit":{"type":"integer"}},"required":["exercise"]}},
 {"name":"best_load","description":"Mayor carga registrada para un ejercicio.","arguments":{"type":"object","properties":{"exercise":{"type":"string"}},"required":["exercise"]}},
 {"name":"record_training","description":"Guarda entrenamiento si fecha, ejercicio, peso kg, series, repeticiones y RIR están presentes. Nunca inventes campos.","arguments":{"type":"object","properties":{"date":{"type":"string"},"exercise":{"type":"string"},"weight_kg":{"type":"number"},"sets":{"type":"integer"},"reps":{"type":"integer"},"rir":{"type":"integer"}},"required":["date","exercise","weight_kg","sets","reps","rir"]}},
 {"name":"search_science","description":"Busca fragmentos reales de documentos indexados en ChromaDB para preguntas científicas de entrenamiento.","arguments":{"type":"object","properties":{"query":{"type":"string"},"k":{"type":"integer"}},"required":["query"]}},
 {"name":"progression_data","description":"Obtiene el último registro real de un ejercicio y guardarraíles para razonar la progresión.","arguments":{"type":"object","properties":{"exercise":{"type":"string"}},"required":["exercise"]}},
 {"name":"delete_training_records","description":"Previsualiza, nunca borra directamente, registros personales. Usa all_records=true solo si piden borrar todo el historial personal. Puedes filtrar por fecha y/o ejercicios.","arguments":{"type":"object","properties":{"date":{"type":["string","null"]},"exercises":{"type":"array","items":{"type":"string"}},"all_records":{"type":"boolean"}},"required":["date","exercises","all_records"]}},
]
TOOL_BY_NAME = {x["name"]: x for x in TOOLS}

PLANNER_SYSTEM = """Eres el planificador de FitLift-LLM. Devuelve SOLO JSON válido:
{"steps":[{"tool":"nombre","arguments":{}}],"need_clarification":null,"answer_without_tools":false}
Si falta un dato imprescindible: {"steps":[],"need_clarification":"pregunta concreta","answer_without_tools":false}

REGLAS DE INTENCIÓN:
1. No planifiques herramientas que no sean indispensables. Máximo 3.
2. NUNCA combines una herramienta de consultar con una de borrar en un solo paso.
3. Para borrar, usa delete_training_records OBLIGATORIAMENTE para previsualizar antes.
4. Para progresiones (qué peso hacer hoy) usa 'progression_data'.
5. Para registrar, usa 'record_training', pero solo si tienes Fecha, Ejercicio, Peso, Series, Repes y RIR.
Herramientas y esquemas disponibles:\n""" + json.dumps(TOOLS, ensure_ascii=False)

RESPONSE_SYSTEM = """Eres Iron-AI, asistente de fuerza, hipertrofia y biomecánica. Responde en español de España, de forma directa y útil.
REGLAS ESTRICTAS DE RESPUESTA:
1. VERACIDAD SQL: SQLite es la única fuente de verdad. No inventes registros, si no hay registros, afirma categóricamente que no existen. No afirmes que se ejecutó una inserción o borrado si el JSON de herramienta no muestra 'ok: True' con evidencia.
2. JUSTIFICACIÓN DE PROGRESIÓN: Si propones subir carga, debes obligatoriamente basarte en el RIR y las series del último registro real de SQLite devuelto. Si el RIR fue muy bajo (0-1), sugiere precaución y no aumentes automáticamente.
3. EVIDENCIA RAG: Cita conclusiones científicas SOLO si aparecen textualmente en los fragmentos RAG. Si la evidencia indexada recuperada no es concluyente (ej. sobre fallo muscular), debes indicar: "La evidencia recuperada no es concluyente sobre este punto", sin inventar teorías.
No muestres JSON interno ni nombres de funciones."""

class FitLiftState(TypedDict, total=False):
    user_input: str
    history: list[dict[str, str]]
    plan: dict[str, Any]
    tool_results: list[dict[str, Any]]
    answer: str
    pending_delete: dict[str, Any] | None
    approval_decision: str | None
    error: str | None
    turn_date: str

def _invoke(llm, prompt: str) -> str:
    return str(llm.invoke(prompt).content).strip()

def _parse_json(raw: str) -> dict[str, Any]:
    s = raw.strip()
    if s.startswith("```"):
        s = re.sub(r"^```(?:json)?\s*", "", s, flags=re.I)
        s = re.sub(r"\s*```$", "", s)
    a, b = s.find("{"), s.rfind("}")
    if a < 0 or b <= a: raise ValueError("El modelo no devolvió un objeto JSON")
    obj = json.loads(s[a:b + 1])
    if not isinstance(obj, dict): raise ValueError("Plan JSON no es un objeto")
    return obj

def _compact_history(history: list[dict[str, str]]) -> str:
    return "\n".join(f"{m.get('role','').upper()}: {m.get('content','')}" for m in history[-MAX_HISTORY:])

def _summarize_rows(rows: list[dict[str, Any]]) -> str:
    return "\n".join(f"- ID {r['id']}: {r['fecha']} | {r['ejercicio']} | {r['series']}x{r['repeticiones']} @ {r['peso']} kg | RIR {r['rir']}" for r in rows)

def execute_tool(name: str, args: dict[str, Any]) -> dict[str, Any]:
    args = args if isinstance(args, dict) else {}
    if name == "current_date": return {"date": date.today().isoformat(), "local_datetime": datetime.now().astimezone().isoformat()}
    if name == "training_history_all": return consultar_todo_historial()
    if name == "training_exercises": return listar_ejercicios()
    if name == "training_statistics": return consultar_estadisticas()
    if name == "exercise_history": return consultar_historial_ejercicio(args.get("exercise", ""), args.get("limit", 20))
    if name == "best_load": return consultar_mejor_carga(args.get("exercise", ""))
    if name == "record_training":
        required = ["date", "exercise", "weight_kg", "sets", "reps", "rir"]
        missing = [k for k in required if k not in args or args[k] is None]
        if missing: return {"ok": False, "missing_fields": missing, "error": "No se guardó nada; faltan campos obligatorios."}
        return registrar_entrenamiento(args["date"], args["exercise"], args["weight_kg"], args["sets"], args["reps"], args["rir"])
    if name == "search_science": return buscar_evidencia(args.get("query", ""), args.get("k", 6))
    if name == "progression_data": return datos_para_progresion(args.get("exercise", ""))
    if name == "delete_training_records":
        return previsualizar_borrado(args.get("date"), args.get("exercises", []), bool(args.get("all_records", False)))
    return {"ok": False, "error": f"Herramienta desconocida: {name}"}

def _valid_plan(plan: dict[str, Any]) -> dict[str, Any]:
    steps = plan.get("steps", [])
    if not isinstance(steps, list): raise ValueError("steps debe ser una lista")
    clean = []
    for step in steps[:MAX_TOOL_STEPS]:
        if not isinstance(step, dict) or step.get("tool") not in TOOL_BY_NAME:
            raise ValueError("El modelo seleccionó una herramienta no permitida")
        args = step.get("arguments", {})
        if not isinstance(args, dict): raise ValueError("Los argumentos de una herramienta deben ser un objeto")
        clean.append({"tool": step["tool"], "arguments": args})
    clarification = plan.get("need_clarification")
    if clarification is not None and not isinstance(clarification, str): raise ValueError("need_clarification debe ser texto o null")
    return {"steps": clean, "need_clarification": clarification, "answer_without_tools": bool(plan.get("answer_without_tools", False))}

def _explicit_confirmation(value: Any) -> Literal["confirm", "cancel", "other"]:
    s = " ".join(str(value or "").lower().strip().split())
    s = re.sub(r"[.!¡¿?]+", "", s)
    if s in {"sí", "si", "confirmo", "confirmar", "sí, borra", "si borra", "adelante", "hazlo", "bórralos", "borralos", "elimínalos", "eliminalos", "sí, elimina", "si elimina"}: return "confirm"
    if s in {"no", "no borres", "cancelar", "cancela", "mejor no", "déjalo", "dejalo", "no lo hagas", "no los borres"}: return "cancel"
    return "other"

def build_graph(llm):
    def plan_node(state: FitLiftState):
        today = date.today().isoformat()
        prompt = (f"{PLANNER_SYSTEM}\nFecha local actual: {today}\nConversación reciente:\n"
                  f"{_compact_history(state.get('history', []))}\nPetición actual: {state.get('user_input','')}\nDevuelve solo JSON.")
        try:
            plan = _valid_plan(_parse_json(_invoke(llm, prompt)))
            return {"plan": plan, "error": None, "turn_date": today}
        except Exception as exc:
            return {"plan": {"steps": [], "need_clarification": None, "answer_without_tools": False}, "error": f"No he podido interpretar de forma segura la petición ({type(exc).__name__}: {exc})."}

    def execute_node(state: FitLiftState):
        results = []
        for step in state.get("plan", {}).get("steps", []):
            name, args = step["tool"], step.get("arguments", {})
            try: result = execute_tool(name, args)
            except Exception as exc: result = {"ok": False, "error": f"{type(exc).__name__}: {exc}"}
            results.append({"tool": name, "result": result})
            if name == "delete_training_records":
                if not isinstance(result, dict) or not result.get("ok") or result.get("count", 0) == 0: continue
                records = result.get("records", [])
                if not records or any("id" not in r for r in records): return {"tool_results": results + [{"error": "Sin IDs verificables; borrado bloqueado."}]}
                pending = {"ids": [int(r["id"]) for r in records], "records": records, "database": result.get("database"), "scope": result.get("scope")}
                return {"tool_results": results, "pending_delete": pending, "answer": None}
        return {"tool_results": results, "pending_delete": None}

    def approval_node(state: FitLiftState):
        pending = state.get("pending_delete") or {}
        reply = interrupt({"kind": "delete_confirmation", "count": len(pending.get("ids", [])),
                           "records": pending.get("records", []), "database": pending.get("database"),
                           "message": "Confirma si quieres eliminar exactamente estos registros."})
        return {"approval_decision": _explicit_confirmation(reply)}

    def route_after_plan(state: FitLiftState) -> str:
        if state.get("error"): return "respond"
        if state.get("plan", {}).get("need_clarification"): return "respond"
        if state.get("plan", {}).get("steps"): return "execute"
        return "respond"

    def route_after_execute(state: FitLiftState) -> str:
        if state.get("pending_delete"): return "approval"
        return "respond"

    def route_after_approval(state: FitLiftState) -> str:
        return "delete" if state.get("approval_decision") == "confirm" else "respond"

    def delete_node(state: FitLiftState):
        pending = state.get("pending_delete") or {}
        result = borrar_registros_por_ids(pending.get("ids", []))
        if result.get("ok") and result.get("deleted_count") == len(pending.get("ids", [])):
            text = "Borrado verificado en SQLite. Se eliminaron estos registros:\n" + _summarize_rows(result.get("deleted_records", []))
        else:
            text = "No puedo confirmar que se haya completado el borrado. Detalle: " + str(result.get("error", "la verificación no coincide"))
        return {"answer": text, "pending_delete": None, "tool_results": state.get("tool_results", []) + [{"tool":"delete_by_previewed_ids", "result":result}]}

    def respond_node(state: FitLiftState):
        if state.get("error"): return {"answer": state["error"]}
        plan = state.get("plan", {})
        
        # Procesar cancelaciones antes del LLM
        if state.get("approval_decision") == "cancel": return {"answer": "Operación cancelada. No se ha borrado ningún registro."}
        if state.get("approval_decision") == "other" and state.get("pending_delete"):
            return {"answer": "No he recibido una confirmación explícita. La operación se ha cancelado."}
        
        clarification = plan.get("need_clarification")
        if clarification: return {"answer": clarification}
        
        results = state.get("tool_results", [])
        for item in results:
            if item.get("tool") == "delete_training_records":
                r = item.get("result", {})
                if r.get("ok") and r.get("count", 0) == 0: return {"answer": "No he encontrado registros que coincidan con esos filtros. No se ha borrado nada."}
                if not r.get("ok"): return {"answer": "No he podido preparar el borrado. Detalle: " + str(r.get("error", "error desconocido"))}
                
        prompt = (f"{RESPONSE_SYSTEM}\nFecha local: {state.get('turn_date', date.today().isoformat())}\n"
                  f"Conversación reciente:\n{_compact_history(state.get('history', []))}\n"
                  f"Petición actual: {state.get('user_input','')}\nResultados de herramientas ejecutadas:\n"
                  f"{json.dumps(results, ensure_ascii=False, default=str)}\n"
                  "Responde a la petición actual. No afirmes acciones que no aparezcan verificadas en los resultados.")
        try: answer = _invoke(llm, prompt)
        except Exception as exc: answer = f"Error invocando a Ollama ({type(exc).__name__}: {exc})."
        return {"answer": answer}

    graph = StateGraph(FitLiftState)
    graph.add_node("plan", plan_node)
    graph.add_node("execute", execute_node)
    graph.add_node("approval", approval_node)
    graph.add_node("delete", delete_node)
    graph.add_node("respond", respond_node)
    graph.add_edge(START, "plan")
    graph.add_conditional_edges("plan", route_after_plan, {"execute":"execute", "respond":"respond"})
    graph.add_conditional_edges("execute", route_after_execute, {"approval":"approval", "respond":"respond"})
    graph.add_conditional_edges("approval", route_after_approval, {"delete":"delete", "respond":"respond"})
    graph.add_edge("delete", "respond")
    graph.add_edge("respond", END)
    return graph.compile(checkpointer=MemorySaver())

def _format_interrupt(payload: dict[str, Any]) -> str:
    records = payload.get("records", [])
    return (f"He encontrado {len(records)} registro(s). Aún no he borrado nada.\n"
            f"{_summarize_rows(records)}\n\n¿Confirmas que elimine exactamente estos registros? Escribe 'sí' para confirmar o 'no' para cancelar.")

def main():
    inicializar_db()
    llm = ChatOllama(model=MODEL, temperature=0)
    graph = build_graph(llm)
    thread_id = os.getenv("FITLIFT_THREAD_ID", "fitlift-console-session")
    config = {"configurable": {"thread_id": thread_id}}
    history: list[dict[str, str]] = []
    
    print("=" * 60)
    print("FITLIFT-LLM | LangGraph + SQL unificado + RAG + protección")
    print("Modelo:", MODEL, "\nSQLite:", ruta_db())
    print("Escribe 'salir' para terminar.\n")
    while True:
        try:
            user = input("TÚ: ").strip()
            if user.lower() in {"salir", "exit", "quit"}: break
            if not user: continue
            history.append({"role":"user", "content":user})
            
            state: FitLiftState = {
                "user_input": user, 
                "history": history[-MAX_HISTORY:], 
                "plan": {}, 
                "tool_results": [],
                "answer": "",
                "error": None,
                "pending_delete": None,
                "approval_decision": None, 
                "turn_date": date.today().isoformat()
            }
            
            result = graph.invoke(state, config=config)
            while result.get("__interrupt__"):
                interrupt_value = result["__interrupt__"][0].value
                print("IRON-AI:", _format_interrupt(interrupt_value))
                reply = input("CONFIRMACIÓN: ").strip()
                result = graph.invoke(Command(resume=reply), config=config)
            answer = str(result.get("answer") or "No se ha generado una respuesta.")
            print("IRON-AI:", answer)
            history.append({"role":"assistant", "content":answer})
        except KeyboardInterrupt:
            break
        except Exception as exc:
            print(f"ERROR CONTROLADO: {type(exc).__name__}: {exc}")

if __name__ == "__main__":
    main()