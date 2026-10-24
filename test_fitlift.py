"""Pruebas unitarias automatizadas para FitLift-LLM reparado."""
import unittest
from unittest.mock import MagicMock
import sqlite3
import os
from pathlib import Path

import src.tools.sql_tools as sql_tools
TEST_DB_PATH = Path(__file__).resolve().parent / "data" / "test_fitlift.db"
sql_tools.DB_PATH = TEST_DB_PATH  # Parcheamos la ruta a nivel de módulo

from main import build_graph

class MockLLM:
    """Doble de prueba para simular Qwen sin requerir Ollama local."""
    def __init__(self, forced_response=None):
        self.forced_response = forced_response or '{"steps":[], "need_clarification":null, "answer_without_tools":true}'
    def invoke(self, prompt):
        mock_response = MagicMock()
        mock_response.content = self.forced_response
        return mock_response

class TestFitLiftReparado(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Asegurar entorno aislado
        if TEST_DB_PATH.exists(): 
            try:
                os.remove(TEST_DB_PATH)
            except PermissionError:
                pass # Si el sistema operativo lo bloquea, se limpiará en setUp
        sql_tools.inicializar_db()
        
    def setUp(self):
        # Limpiar tabla antes de cada prueba de forma segura
        c = sql_tools._connect()
        try:
            with c: 
                c.execute("DELETE FROM historial")
        finally:
            c.close()

    def test_1_historial_vacio(self):
        res = sql_tools.consultar_historial_ejercicio("Sentadilla")
        self.assertEqual(res["count"], 0)
        self.assertEqual(res["sessions"], [])

    def test_2_registrar_y_consultar_independiente(self):
        res = sql_tools.registrar_entrenamiento("2026-10-24", "Press Banca", 100, 3, 5, 2)
        self.assertTrue(res["ok"], f"Fallo al registrar: {res.get('error')}")
        db_res = sql_tools.consultar_historial_ejercicio("Press Banca")
        self.assertEqual(db_res["count"], 1)
        self.assertEqual(db_res["sessions"][0]["peso"], 100.0)

    def test_3_sesiones_multiples_mismo_dia(self):
        sql_tools.registrar_entrenamiento("2026-10-24", "Remo", 50, 3, 10, 1)
        sql_tools.registrar_entrenamiento("2026-10-24", "Remo", 55, 2, 8, 0)
        db_res = sql_tools.consultar_historial_ejercicio("Remo")
        self.assertEqual(db_res["count"], 2, "La base de datos debe permitir dobles sesiones y no sobrescribir.")

    def test_5_insercion_fallida_sin_exito(self):
        res = sql_tools.registrar_entrenamiento("fecha-invalida", "Remo", 50, 3, 10, 1)
        self.assertFalse(res["ok"])
        self.assertIn("error", res)

    def test_6_borrado_cancelado_no_modifica_filas(self):
        sql_tools.registrar_entrenamiento("2026-10-24", "Remo", 50, 3, 10, 1)
        pre = sql_tools.previsualizar_borrado(ejercicios=["Remo"])
        # Simulamos flujo LangGraph con cancelación manual
        graph = build_graph(MockLLM())
        state = {"user_input": "borra remo", "pending_delete": {"ids": [pre["records"][0]["id"]], "records": pre["records"]}, "approval_decision": "cancel"}
        res = graph.invoke(state, config={"configurable": {"thread_id": "t1"}})
        self.assertIn("cancelada", res["answer"].lower())
        db_res = sql_tools.consultar_historial_ejercicio("Remo")
        self.assertEqual(db_res["count"], 1)

    def test_7_borrado_confirmado(self):
        sql_tools.registrar_entrenamiento("2026-10-24", "Remo", 50, 3, 10, 1)
        pre = sql_tools.previsualizar_borrado(ejercicios=["Remo"])
        borrado = sql_tools.borrar_registros_por_ids([pre["records"][0]["id"]])
        self.assertTrue(borrado["ok"])
        self.assertEqual(borrado["deleted_count"], 1)
        db_res = sql_tools.consultar_historial_ejercicio("Remo")
        self.assertEqual(db_res["count"], 0)

    def test_8_confirmacion_ambigua(self):
        graph = build_graph(MockLLM())
        state = {"user_input": "borralo", "pending_delete": {"ids": [1]}, "approval_decision": "other"}
        res = graph.invoke(state, config={"configurable": {"thread_id": "t1"}})
        self.assertIn("cancelado", res["answer"].lower())

if __name__ == '__main__':
    unittest.main()