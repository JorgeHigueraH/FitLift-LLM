[Español](#español) | [English](#english)

---

<a name="español"></a>
# Español

## FitLift-LLM: Agente Autónomo de Entrenamiento de Fuerza
FitLift-LLM es un sistema conversacional avanzado diseñado para el entrenamiento de fuerza, hipertrofia y biomecánica cuantitativa. A diferencia de los asistentes estándar basados en modelos de lenguaje grandes (LLMs), este sistema opera bajo un paradigma de "Cerebro Dividido", actuando como un ingeniero de datos estricto. Basa sus decisiones de sobrecarga progresiva en cálculos matemáticos, control de fatiga (RIR/RPE) y literatura científica verificable.

El sistema orquesta un modelo de lenguaje local (Qwen 2.5 7B vía Ollama) con un grafo de estado (LangGraph), memoria persistente (SQLite) y recuperación de documentos (ChromaDB) para erradicar las alucinaciones y proporcionar planificaciones atléticas de grado profesional.

### Problemas Solucionados
Durante el desarrollo de asistentes de IA convencionales orientados al fitness, surgen fallos estructurales que este proyecto resuelve de raíz:
1. **Alucinaciones de Base de Datos:** Los LLMs estándar inventan registros pasados para justificar rutinas. FitLift-LLM tiene su acceso de escritura/lectura restringido a consultas reales de SQLite.
2. **Bucles de Herramientas (Infinite Tool Calling):** Los modelos suelen entrar en pánico si una consulta a una base de datos no devuelve exactamente lo que esperan. FitLift-LLM utiliza un sistema de pre-enrutamiento estricto que limita los pasos de ejecución.
3. **Progresiones Lesivas:** Un LLM estándar ignora la implicación de la fatiga. Si el usuario indica un esfuerzo máximo (RIR 0), el LLM a menudo recomienda subir el peso. Este proyecto integra compuertas lógicas ("Leyes de Fatiga") que bloquean incrementos de carga bajo alta fatiga central.
4. **Falta de Trazabilidad:** Las afirmaciones científicas inventadas se eliminan obligando al modelo a justificar sus respuestas citando exclusivamente los metadatos devueltos por el sistema RAG.

### Estrategias y Arquitectura
* **Pre-Enrutamiento Semántico:** El sistema evalúa la entrada del usuario mediante expresiones regulares y lógica condicional antes de invocar al LLM. Esto prioriza las intenciones (Registrar, Progresar, Borrar, Consultar Teoría).
* **LangGraph y MemorySaver:** Implementación de un grafo de estado (`StateGraph`) que gestiona el contexto de la conversación. Las interrupciones (`interrupt`) permiten confirmar borrados de forma segura, pausando el grafo hasta recibir autorización explícita del usuario.
* **SQL Seguro (SQLite):** Esquema relacional con protección contra sobrescritura no deseada. Inserciones transaccionales que verifican la lectura posterior antes de reportar éxito al usuario.
* **RAG Académico:** Indexación de documentos científicos mediante `pymupdf` y `sentence-transformers`, con partición semántica y persistencia vectorial en ChromaDB.

### Comparativa: LLM Estándar vs FitLift-LLM

| Característica | LLM Estándar (ChatGPT / Claude) | FitLift-LLM |
| :--- | :--- | :--- |
| **Progresión de Carga** | Sube el peso de forma arbitraria o lineal. | Limitada por reglas de Micro-Loading y Ley de Fatiga (RIR). |
| **Persistencia de Datos** | Pierde el historial al cerrar el chat. | Lectura y escritura transaccional en SQLite local. |
| **Evidencia Científica** | Inventa autores, estudios y conclusiones. | RAG indexado sobre literatura proporcionada por el usuario. |
| **Tono de Comunicación** | Complaciente, usa frases motivacionales. | Crítico, analítico, directo; basado en tablas de datos. |
| **Seguridad de Datos** | Los datos residen en servidores de terceros. | 100% Local (Ollama + SQLite + ChromaDB). |

### Ejemplo de Interacción

**Usuario:** "Ayer hice press banca 30 kg a 6 repeticiones en 3 series con RIR 1, ¿qué me recomiendas hacer hoy?"

**Procesamiento Interno (Oculto):**
1. *Pre-Enrutamiento:* Intención de progresión detectada.
2. *Herramienta SQL:* Busca historial de "Press Banca" -> Recupera último E1RM y volumen.
3. *Herramienta RAG:* Busca "progressive overload RIR hypertrophy".
4. *Motor Lógico:* Evalúa RIR 1 (Alta fatiga). Aplica la Ley de Fatiga: Bloquear incremento de peso.

**Respuesta de FitLift-LLM:**
"Viniendo de un RIR 1 con 30 kg, tu Sistema Nervioso Central estaba al límite. Subir el peso hoy es un error que te llevará a fallar la serie. Vamos a mantener la carga y buscar adaptación de volumen.

| Ejercicio | Series | Repeticiones | Peso | RIR Objetivo |
| :--- | :--- | :--- | :--- | :--- |
| Press Banca | 3 | 6 | 30.0 kg | 1 - 2 |"

### Instalación y Ejecución
1. Instalar dependencias requeridas (solo paquetes de primer nivel):
   `pip install -r requirements.txt`
2. Depositar documentos científicos (PDFs) en `data/raw_papers/`.
3. Ingerir documentos en la base de datos vectorial:
   `python src/rag/ingestor.py`
4. Ejecutar el orquestador principal:
   `python main.py`

---

<a name="english"></a>
# English

## FitLift-LLM: Autonomous Strength Training Agent
FitLift-LLM is an advanced conversational system designed for strength training, hypertrophy, and quantitative biomechanics. Unlike standard assistants based on large language models (LLMs), this system operates under a "Split-Brain" paradigm, acting as a strict data engineer. It bases its progressive overload decisions on mathematical calculations, fatigue management (RIR/RPE), and verifiable scientific literature.

The system orchestrates a local language model (Qwen 2.5 7B via Ollama) with a state graph (LangGraph), persistent memory (SQLite), and document retrieval (ChromaDB) to eradicate hallucinations and provide professional-grade athletic planning.

### Problems Solved
During the development of conventional AI fitness assistants, structural flaws arise that this project solves at the root:
1. **Database Hallucinations:** Standard LLMs invent past workout records to justify routines. FitLift-LLM has its read/write access strictly constrained to actual SQLite queries.
2. **Infinite Tool Calling Loops:** Models often panic if a database query does not return exactly what they expect. FitLift-LLM uses a strict pre-routing system that limits execution steps.
3. **Harmful Progressions:** A standard LLM ignores the implications of fatigue. If the user indicates maximum effort (RIR 0), the LLM often recommends increasing the weight. This project integrates logic gates ("Fatigue Laws") that block load increments under high central nervous system fatigue.
4. **Lack of Traceability:** Invented scientific claims are eliminated by forcing the model to justify its answers citing exclusively the metadata returned by the RAG system.

### Strategies and Architecture
* **Semantic Pre-Routing:** The system evaluates user input using regular expressions and conditional logic before invoking the LLM. This prioritizes intents (Log, Progress, Delete, Query Theory).
* **LangGraph and MemorySaver:** Implementation of a state graph (`StateGraph`) that manages conversation context. Interruptions (`interrupt`) allow for safe deletion confirmations, pausing the graph until explicit user authorization is received.
* **Safe SQL (SQLite):** Relational schema with protection against unwanted overwriting. Transactional insertions that verify subsequent reading before reporting success to the user.
* **Strict Academic RAG:** Indexing of scientific documents using `pymupdf` and `sentence-transformers`, with semantic chunking and vector persistence in ChromaDB.

### Comparison: Standard LLM vs FitLift-LLM

| Feature | Standard LLM (ChatGPT / Claude) | FitLift-LLM |
| :--- | :--- | :--- |
| **Load Progression** | Increases weight arbitrarily or linearly. | Limited by Micro-Loading rules and Fatigue Law (RIR). |
| **Data Persistence** | Loses history when the chat is closed. | Transactional read and write in local SQLite. |
| **Scientific Evidence** | Invents authors, studies, and conclusions. | RAG indexed over user-provided literature. |
| **Tone of Communication** | Complaisant, uses motivational phrases. | Critical, analytical, direct; relies on data tables. |
| **Data Security** | Data resides on third-party servers. | 100% Local (Ollama + SQLite + ChromaDB). |

### Interaction Example

**User:** "Yesterday I did bench press 30 kg for 6 reps in 3 sets with RIR 1, what do you recommend I do today?"

**Internal Processing (Hidden):**
1. *Pre-Routing:* Progression intent detected.
2. *SQL Tool:* Searches history for "Bench Press" -> Retrieves last E1RM and volume.
3. *RAG Tool:* Searches for "progressive overload RIR hypertrophy".
4. *Logic Engine:* Evaluates RIR 1 (High fatigue). Applies Fatigue Law: Block weight increment.

**FitLift-LLM Response:**
"Coming from an RIR 1 with 30 kg, your Central Nervous System was at its limit. Increasing the weight today is a mistake that will lead to set failure. We will maintain the load and seek volume adaptation.

| Exercise | Sets | Repetitions | Weight | Target RIR |
| :--- | :--- | :--- | :--- | :--- |
| Bench Press | 3 | 6 | 30.0 kg | 1 - 2 |"

### Installation and Execution
1. Install required dependencies (top-level packages only):
   `pip install -r requirements.txt`
2. Place scientific documents (PDFs) in `data/raw_papers/`.
3. Ingest documents into the vector database:
   `python src/rag/ingestor.py`
4. Run the main orchestrator:
   `python main.py`[Español](#español) | [English](#english)

---

<a name="español"></a>
# Español

## FitLift-LLM: Agente Autónomo de Entrenamiento de Fuerza
FitLift-LLM es un sistema conversacional avanzado diseñado para el entrenamiento de fuerza, hipertrofia y biomecánica cuantitativa. A diferencia de los asistentes estándar basados en modelos de lenguaje grandes (LLMs), este sistema opera bajo un paradigma de "Cerebro Dividido", actuando como un ingeniero de datos estricto. Basa sus decisiones de sobrecarga progresiva en cálculos matemáticos, control de fatiga (RIR/RPE) y literatura científica verificable.

El sistema orquesta un modelo de lenguaje local (Qwen 2.5 7B vía Ollama) con un grafo de estado (LangGraph), memoria persistente (SQLite) y recuperación de documentos (ChromaDB) para erradicar las alucinaciones y proporcionar planificaciones atléticas de grado profesional.

### Problemas Solucionados
Durante el desarrollo de asistentes de IA convencionales orientados al fitness, surgen fallos estructurales que este proyecto resuelve de raíz:
1. **Alucinaciones de Base de Datos:** Los LLMs estándar inventan registros pasados para justificar rutinas. FitLift-LLM tiene su acceso de escritura/lectura restringido a consultas reales de SQLite.
2. **Bucles de Herramientas (Infinite Tool Calling):** Los modelos suelen entrar en pánico si una consulta a una base de datos no devuelve exactamente lo que esperan. FitLift-LLM utiliza un sistema de pre-enrutamiento estricto que limita los pasos de ejecución.
3. **Progresiones Lesivas:** Un LLM estándar ignora la implicación de la fatiga. Si el usuario indica un esfuerzo máximo (RIR 0), el LLM a menudo recomienda subir el peso. Este proyecto integra compuertas lógicas ("Leyes de Fatiga") que bloquean incrementos de carga bajo alta fatiga central.
4. **Falta de Trazabilidad:** Las afirmaciones científicas inventadas se eliminan obligando al modelo a justificar sus respuestas citando exclusivamente los metadatos devueltos por el sistema RAG.

### Estrategias y Arquitectura
* **Pre-Enrutamiento Semántico:** El sistema evalúa la entrada del usuario mediante expresiones regulares y lógica condicional antes de invocar al LLM. Esto prioriza las intenciones (Registrar, Progresar, Borrar, Consultar Teoría).
* **LangGraph y MemorySaver:** Implementación de un grafo de estado (`StateGraph`) que gestiona el contexto de la conversación. Las interrupciones (`interrupt`) permiten confirmar borrados de forma segura, pausando el grafo hasta recibir autorización explícita del usuario.
* **SQL Seguro (SQLite):** Esquema relacional con protección contra sobrescritura no deseada. Inserciones transaccionales que verifican la lectura posterior antes de reportar éxito al usuario.
* **RAG Académico:** Indexación de documentos científicos mediante `pymupdf` y `sentence-transformers`, con partición semántica y persistencia vectorial en ChromaDB.

### Comparativa: LLM Estándar vs FitLift-LLM

| Característica | LLM Estándar (ChatGPT / Claude) | FitLift-LLM |
| :--- | :--- | :--- |
| **Progresión de Carga** | Sube el peso de forma arbitraria o lineal. | Limitada por reglas de Micro-Loading y Ley de Fatiga (RIR). |
| **Persistencia de Datos** | Pierde el historial al cerrar el chat. | Lectura y escritura transaccional en SQLite local. |
| **Evidencia Científica** | Inventa autores, estudios y conclusiones. | RAG indexado sobre literatura proporcionada por el usuario. |
| **Tono de Comunicación** | Complaciente, usa frases motivacionales. | Crítico, analítico, directo; basado en tablas de datos. |
| **Seguridad de Datos** | Los datos residen en servidores de terceros. | 100% Local (Ollama + SQLite + ChromaDB). |

### Ejemplo de Interacción

**Usuario:** "Ayer hice press banca 30 kg a 6 repeticiones en 3 series con RIR 1, ¿qué me recomiendas hacer hoy?"

**Procesamiento Interno (Oculto):**
1. *Pre-Enrutamiento:* Intención de progresión detectada.
2. *Herramienta SQL:* Busca historial de "Press Banca" -> Recupera último E1RM y volumen.
3. *Herramienta RAG:* Busca "progressive overload RIR hypertrophy".
4. *Motor Lógico:* Evalúa RIR 1 (Alta fatiga). Aplica la Ley de Fatiga: Bloquear incremento de peso.

**Respuesta de FitLift-LLM:**
"Viniendo de un RIR 1 con 30 kg, tu Sistema Nervioso Central estaba al límite. Subir el peso hoy es un error que te llevará a fallar la serie. Vamos a mantener la carga y buscar adaptación de volumen.

| Ejercicio | Series | Repeticiones | Peso | RIR Objetivo |
| :--- | :--- | :--- | :--- | :--- |
| Press Banca | 3 | 6 | 30.0 kg | 1 - 2 |"

### Instalación y Ejecución
1. Instalar dependencias requeridas (solo paquetes de primer nivel):
   `pip install -r requirements.txt`
2. Depositar documentos científicos (PDFs) en `data/raw_papers/`.
3. Ingerir documentos en la base de datos vectorial:
   `python src/rag/ingestor.py`
4. Ejecutar el orquestador principal:
   `python main.py`

---

<a name="english"></a>
# English

## FitLift-LLM: Autonomous Strength Training Agent
FitLift-LLM is an advanced conversational system designed for strength training, hypertrophy, and quantitative biomechanics. Unlike standard assistants based on large language models (LLMs), this system operates under a "Split-Brain" paradigm, acting as a strict data engineer. It bases its progressive overload decisions on mathematical calculations, fatigue management (RIR/RPE), and verifiable scientific literature.

The system orchestrates a local language model (Qwen 2.5 7B via Ollama) with a state graph (LangGraph), persistent memory (SQLite), and document retrieval (ChromaDB) to eradicate hallucinations and provide professional-grade athletic planning.

### Problems Solved
During the development of conventional AI fitness assistants, structural flaws arise that this project solves at the root:
1. **Database Hallucinations:** Standard LLMs invent past workout records to justify routines. FitLift-LLM has its read/write access strictly constrained to actual SQLite queries.
2. **Infinite Tool Calling Loops:** Models often panic if a database query does not return exactly what they expect. FitLift-LLM uses a strict pre-routing system that limits execution steps.
3. **Harmful Progressions:** A standard LLM ignores the implications of fatigue. If the user indicates maximum effort (RIR 0), the LLM often recommends increasing the weight. This project integrates logic gates ("Fatigue Laws") that block load increments under high central nervous system fatigue.
4. **Lack of Traceability:** Invented scientific claims are eliminated by forcing the model to justify its answers citing exclusively the metadata returned by the RAG system.

### Strategies and Architecture
* **Semantic Pre-Routing:** The system evaluates user input using regular expressions and conditional logic before invoking the LLM. This prioritizes intents (Log, Progress, Delete, Query Theory).
* **LangGraph and MemorySaver:** Implementation of a state graph (`StateGraph`) that manages conversation context. Interruptions (`interrupt`) allow for safe deletion confirmations, pausing the graph until explicit user authorization is received.
* **Safe SQL (SQLite):** Relational schema with protection against unwanted overwriting. Transactional insertions that verify subsequent reading before reporting success to the user.
* **Strict Academic RAG:** Indexing of scientific documents using `pymupdf` and `sentence-transformers`, with semantic chunking and vector persistence in ChromaDB.

### Comparison: Standard LLM vs FitLift-LLM

| Feature | Standard LLM (ChatGPT / Claude) | FitLift-LLM |
| :--- | :--- | :--- |
| **Load Progression** | Increases weight arbitrarily or linearly. | Limited by Micro-Loading rules and Fatigue Law (RIR). |
| **Data Persistence** | Loses history when the chat is closed. | Transactional read and write in local SQLite. |
| **Scientific Evidence** | Invents authors, studies, and conclusions. | RAG indexed over user-provided literature. |
| **Tone of Communication** | Complaisant, uses motivational phrases. | Critical, analytical, direct; relies on data tables. |
| **Data Security** | Data resides on third-party servers. | 100% Local (Ollama + SQLite + ChromaDB). |

### Interaction Example

**User:** "Yesterday I did bench press 30 kg for 6 reps in 3 sets with RIR 1, what do you recommend I do today?"

**Internal Processing (Hidden):**
1. *Pre-Routing:* Progression intent detected.
2. *SQL Tool:* Searches history for "Bench Press" -> Retrieves last E1RM and volume.
3. *RAG Tool:* Searches for "progressive overload RIR hypertrophy".
4. *Logic Engine:* Evaluates RIR 1 (High fatigue). Applies Fatigue Law: Block weight increment.

**FitLift-LLM Response:**
"Coming from an RIR 1 with 30 kg, your Central Nervous System was at its limit. Increasing the weight today is a mistake that will lead to set failure. We will maintain the load and seek volume adaptation.

| Exercise | Sets | Repetitions | Weight | Target RIR |
| :--- | :--- | :--- | :--- | :--- |
| Bench Press | 3 | 6 | 30.0 kg | 1 - 2 |"

### Installation and Execution
1. Install required dependencies (top-level packages only):
   `pip install -r requirements.txt`
2. Place scientific documents (PDFs) in `data/raw_papers/`.
3. Ingest documents into the vector database:
   `python src/rag/ingestor.py`
4. Run the main orchestrator:
   `python main.py`
