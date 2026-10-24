
"""
Indexa PDFs de data/raw_papers en ChromaDB.

Uso desde la raíz del proyecto:
    .\venv\Scripts\python.exe src/rag/ingestor.py

Requisitos:
    pymupdf, langchain-text-splitters, langchain-chroma,
    langchain-huggingface, sentence-transformers
"""

import hashlib
import re
from pathlib import Path

import pymupdf
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma


# ============================================================
# RUTAS Y CONFIGURACIÓN
# ============================================================

# ingestor.py está en FitLift-LLM/src/rag/.
# parents[2] apunta a la raíz FitLift-LLM/.
ROOT = Path(__file__).resolve().parents[2]

RAW_DIR = ROOT / "data" / "raw_papers"
DB_DIR = ROOT / "data" / "vector_store"

COLLECTION = "fitlift_papers"
EMBEDDING_MODEL = (
    "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
)


# ============================================================
# UTILIDADES
# ============================================================

def sha256_file(path: Path) -> str:
    """Calcula el SHA-256 de un archivo para detectar cambios."""
    h = hashlib.sha256()

    with path.open("rb") as file:
        for block in iter(lambda: file.read(1024 * 1024), b""):
            h.update(block)

    return h.hexdigest()


def infer_metadata(text: str, filename: str) -> dict:
    """
    Extrae metadatos heurísticos.
    Los autores y otros datos bibliográficos deben verificarse
    manualmente contra el documento original.
    """
    title = Path(filename).stem.replace("_", " ").replace("-", " ")

    year_match = re.search(r"\b(?:19|20)\d{2}\b", text[:6000])

    doi_match = re.search(
        r"\b10\.\d{4,9}/[-._;()/:A-Z0-9]+\b",
        text,
        re.IGNORECASE,
    )

    return {
        "title": title,
        "year": year_match.group(0) if year_match else "no extraído",
        "doi": doi_match.group(0).rstrip(".,;") if doi_match else "",
        "authors": "no extraídos; verificar el PDF",
    }


# ============================================================
# INGESTIÓN
# ============================================================

def main() -> None:
    """Lee los PDF, los divide en fragmentos y los guarda en ChromaDB."""

    print(f"Raíz del proyecto: {ROOT}")
    print(f"Directorio de PDF: {RAW_DIR}")
    print(f"Directorio ChromaDB: {DB_DIR}")

    RAW_DIR.mkdir(parents=True, exist_ok=True)

    pdfs = sorted(
        path for path in RAW_DIR.iterdir()
        if path.is_file() and path.suffix.lower() == ".pdf"
    )

    if not pdfs:
        print(f"No se encontraron PDF en: {RAW_DIR}")
        print("Introduce los PDF científicos en esa carpeta y vuelve a ejecutar.")
        return

    print(f"PDF encontrados: {len(pdfs)}")

    embeddings = HuggingFaceEmbeddings(
        model_name=EMBEDDING_MODEL
    )

    store = Chroma(
        collection_name=COLLECTION,
        persist_directory=str(DB_DIR),
        embedding_function=embeddings,
    )

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1200,
        chunk_overlap=220,
        separators=["\n\n", "\n", ". ", " ", ""],
    )

    total_added = 0

    for pdf in pdfs:
        print(f"\nProcesando: {pdf.name}")

        digest = sha256_file(pdf)
        source_key = str(pdf.resolve())

        # Comprobar si ya existe una versión indexada de este archivo.
        existing = store.get(
            where={"source": source_key},
            include=["metadatas"],
        )

        existing_ids = existing.get("ids") or []
        existing_metadata = existing.get("metadatas") or []

        old_hashes = {
            metadata.get("file_hash")
            for metadata in existing_metadata
            if metadata
        }

        if existing_ids and old_hashes == {digest}:
            print(f"Sin cambios: {pdf.name}")
            continue

        if existing_ids:
            store.delete(ids=existing_ids)
            print("Versión anterior eliminada; se indexará la nueva.")

        documents = []

        try:
            with pymupdf.open(str(pdf)) as pdf_document:
                for page_index, page in enumerate(pdf_document):
                    text = page.get_text("text").strip()

                    if not text:
                        continue

                    base_metadata = infer_metadata(text, pdf.name)

                    documents.append(
                        Document(
                            page_content=text,
                            metadata={
                                "source": source_key,
                                "source_name": pdf.name,
                                "file_hash": digest,
                                "page": page_index + 1,
                                **base_metadata,
                            },
                        )
                    )

        except Exception as exc:
            print(f"ERROR leyendo {pdf.name}: {exc}")
            continue

        if not documents:
            print(
                f"AVISO: {pdf.name} no contiene texto extraíble. "
                "Si es un PDF escaneado, necesitarás aplicar OCR."
            )
            continue

        chunks = splitter.split_documents(documents)

        ids = [
            hashlib.sha1(
                f"{source_key}|{digest}|{index}".encode("utf-8")
            ).hexdigest()
            for index in range(len(chunks))
        ]

        try:
            store.add_documents(chunks, ids=ids)
        except Exception as exc:
            print(f"ERROR indexando {pdf.name}: {exc}")
            continue

        total_added += len(chunks)

        print(
            f"Indexado correctamente: {pdf.name} "
            f"-> {len(chunks)} fragmentos"
        )

    print("\n" + "=" * 55)
    print("INGESTIÓN FINALIZADA")
    print(f"Fragmentos añadidos en esta ejecución: {total_added}")
    print(f"Colección: {COLLECTION}")
    print(f"Almacenamiento: {DB_DIR}")
    print("=" * 55)


if __name__ == "__main__":
    main()
