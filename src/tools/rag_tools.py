"""Recuperación de evidencia: nunca crea referencias; devuelve metadatos reales."""
from functools import lru_cache
from pathlib import Path
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma

ROOT = Path(__file__).resolve().parents[2]
VECTOR_DIR = ROOT / "data" / "vector_store"
COLLECTION = "fitlift_papers"

@lru_cache(maxsize=1)
def _embeddings():
    return HuggingFaceEmbeddings(model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2")
@lru_cache(maxsize=1)
def _store():
    return Chroma(collection_name=COLLECTION, persist_directory=str(VECTOR_DIR), embedding_function=_embeddings())
def estado_coleccion():
    try: return {"available": True, "collection": COLLECTION, "chunks": _store()._collection.count(), "path": str(VECTOR_DIR)}
    except Exception as e: return {"available": False, "error": f"{type(e).__name__}: {e}", "path": str(VECTOR_DIR)}
def buscar_evidencia(query, k=6):
    q = str(query or "").strip()
    if len(q) < 4: return {"ok": False, "error": "La consulta necesita más contexto."}
    try:
        docs = _store().similarity_search_with_score(q, k=max(1, min(int(k), 10)))
        chunks = []
        for rank, (doc, score) in enumerate(docs, 1):
            md = doc.metadata or {}
            source = md.get("source_name") or md.get("source") or md.get("file_path")
            title = md.get("title") or md.get("document_title") or (Path(str(source)).name if source else "Documento sin título en metadatos")
            chunks.append({"rank": rank, "title": str(title), "source": str(source) if source else None,
                           "page": md.get("page", md.get("page_number")), "score_distance": round(float(score), 4),
                           "text": " ".join(str(doc.page_content).split())[:2200]})
        return {"ok": True, "query": q, "collection": COLLECTION, "count": len(chunks), "chunks": chunks,
                "note": "La distancia de similitud no es una probabilidad de verdad; verifica que los fragmentos respondan realmente a la pregunta."}
    except Exception as e:
        return {"ok": False, "error": f"{type(e).__name__}: {e}"}
