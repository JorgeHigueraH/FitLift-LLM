#  FitLift-LLM

**Choose your language / Elige tu idioma:** 
[🇺🇸 English Version](#english-version) | [🇪🇸 Versión en Español](#versión-en-español)

---

<a id="english-version"></a>
## English Version

### 1. Project Overview
This project implements an advanced Autonomous Strength Training Agent (FitLift-LLM) designed to manage progressive overload, hypertrophy programming, and quantitative biomechanics. Moving beyond basic conversational chatbots, this architecture combines a local Large Language Model (Qwen 2.5 7B via Ollama) with strict mathematical constraints and empirical data validation. It features a State Graph (LangGraph) for memory management, a transactional SQLite database as the single source of truth, and a Retrieval-Augmented Generation (RAG) pipeline via ChromaDB, demonstrating end-to-end AI orchestration and data engineering capabilities.

CRITICAL DISCLAIMER: This software acts as a strict data engineer and strength coach. It does not output motivational phrasing, and it mathematically rejects user proposals that are biomechanically unsafe or lack scientific backing. 

### 2. The Engineering Journey: Data Bottlenecks & Hypothesis Testing
Building a robust, hallucination-free AI coach required overcoming the inherent unpredictability of LLMs through iterative failures and structural adaptations:

1. **Database Hallucinations & The "Lazy LLM" Crisis:** Initial iterations relied purely on the LLM to decide when to save or read data. The model frequently hallucinated past workout records to justify its routines or falsely claimed to have saved data without executing the SQL tool. We solved this by implementing Semantic Pre-Routing in Python, forcing the LLM into specific execution gates (Scenario 1, 2, 3, 4) based on regex intent detection before the model even generates a thought.
2. **Infinite Tool Calling Loops:** When the RAG database returned literature that lacked a specific mathematical formula, the LLM panicked and called the search tool infinitely. We engineered an "Anti-Loop Kill Switch" within the system prompt and LangGraph architecture, forcing the model to accept the first retrieval and fall back on hardcoded Micro-Loading rules if the literature was inconclusive.
3. **The Fatigue Ignorance (Empirical Analysis):** Standard LLMs linearly increased training weight regardless of user fatigue. We hypothesized that injecting Repetitions in Reserve (RIR) logic would solve this. Empirical testing proved that the LLM still struggled to quantify exhaustion. We hardcoded the "Fatigue Law": if the previous RIR was 0 or 1, the system mathematically blocks any weight increment, prioritizing volume adaptation instead.
4. **Memory State Corruption:** LangGraph's `MemorySaver` caused the agent to mix previous tool outputs with current requests, leading to simultaneous (and contradictory) execution of database reads and deletions. We resolved this by strictly re-initializing the transient graph state (`pending_delete`, `tool_results`) at the start of every interactive loop, ensuring complete temporal isolation.

### 3. The Final Architecture: Strict Constraints & State Machine

| Component | Function | Quantitative Impact |
| :--- | :--- | :--- |
| **Semantic Pre-Router** | Intercepts user prompts via regex before LLM inference. | Eradicates 100% of tool-calling loops by dictating the exact sequence of SQL/RAG tools to use. |
| **Transactional SQLite** | Manages the training history state with schema protections. | Prevents silent overwrites via unified tables and enforces strict ID validation prior to any data deletion. |
| **LangGraph State Machine** | Orchestrates the conversational flow and memory. | Features an `interrupt` node that physically halts the graph until explicit human confirmation is received for destructive actions. |
| **Academic RAG (ChromaDB)** | Retrieves scientific evidence from biomedical PDFs. | Grounds training recommendations in verifiable literature, exposing out-of-fold probabilistic uncertainties. |

### 4. Comparison: Standard LLM vs FitLift-LLM

| Feature | Standard LLM (ChatGPT / Claude) | FitLift-LLM |
| :--- | :--- | :--- |
| **Load Progression** | Increases weight arbitrarily or linearly. | Strictly limited by Micro-Loading rules and Fatigue Law (RIR). |
| **Data Persistence** | Loses history when the chat is closed. | Transactional read and write in local SQLite. |
| **Scientific Evidence** | Invents authors, studies, and conclusions. | RAG indexed exclusively over user-provided literature. |
| **Tone of Communication** | Complaisant, uses motivational filler. | Critical, analytical, direct; relies heavily on data tables. |
| **Data Security** | Data resides on third-party servers. | 100% Local Operations (Ollama + SQLite + ChromaDB). |

### 5. Interaction Example: Live Execution
Below is an excerpt from the interactive console, showcasing how the state machine evaluates historical SQL data, retrieves RAG theory, and applies the Fatigue Law to prevent overtraining.

```text
USER: "Yesterday I did bench press 30 kg for 6 reps in 3 sets with RIR 1, what do you recommend I do today?"

--- EXECUTION FLOW ---
  TOOL -> consultar_historial_ejercicio
  RESULT -> HISTORY OF BENCH PRESS: 1. Date: 2026-10-21 | 30.0kg x 3x6 (RIR 1)

  TOOL -> consultar_teoria_entrenamiento
  RESULT -> RAG RESULTS FOR: "progressive overload RIR hypertrophy"

IRON-AI:
Based on your history, your last session was 30 kg for 6 repetitions across 3 sets with an RIR of 1. 

Coming from an RIR 1, your Central Nervous System was at its limit. Increasing the weight today is a mistake that will lead to set failure. According to the Fatigue Law, we will maintain the load and seek volume adaptation.

| Exercise | Sets | Repetitions | Weight | Target RIR |
| :--- | :--- | :--- | :--- | :--- |
| Bench Press | 3 | 6 | 30.0 kg | 1 - 2 |
```

### 6. References / Applied Concepts
1. Zourdos, M. C., et al. (2016). Novel Resistance Training-Specific Rating of Perceived Exertion Scale Measuring Repetitions in Reserve. (Applied for the Fatigue Law and load blocking architecture).
2. LangChain AI. (2024). LangGraph: Building Stateful, Multi-Actor Applications with LLMs. (Applied for the interrupt-driven deletion nodes and state management).
3. Lewis, P., et al. (2020). Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks. (Applied for ChromaDB academic evidence retrieval).

---

<a id="versión-en-español"></a>
## Versión en Español

### 1. Resumen del Proyecto
Este proyecto implementa un Agente Autónomo de Entrenamiento de Fuerza (FitLift-LLM) avanzado, diseñado para gestionar la sobrecarga progresiva, la programación de hipertrofia y la biomecánica cuantitativa. Yendo más allá de los chatbots conversacionales básicos, esta arquitectura combina un Modelo de Lenguaje local (Qwen 2.5 7B vía Ollama) con restricciones matemáticas estrictas y validación de datos empíricos. Cuenta con un Grafo de Estado (LangGraph) para la gestión de memoria, una base de datos SQLite transaccional como única fuente de verdad, y un pipeline de Generación Aumentada por Recuperación (RAG) mediante ChromaDB, demostrando capacidades completas de orquestación de IA e ingeniería de datos.

DESCARGO DE RESPONSABILIDAD CRÍTICO: Este software actúa estrictamente como un ingeniero de datos y entrenador de fuerza. No genera frases motivacionales y rechaza matemáticamente las propuestas del usuario que sean biomecánicamente inseguras o carezcan de respaldo científico.

### 2. El Camino de Ingeniería: Cuellos de Botella de Datos y Prueba de Hipótesis
Construir un entrenador de IA robusto y libre de alucinaciones requirió superar la imprevisibilidad inherente de los LLMs mediante fallos iterativos y adaptaciones estructurales:

1. **Alucinaciones de Base de Datos y la Crisis del "LLM Perezoso":** Las iteraciones iniciales dependían puramente del LLM para decidir cuándo guardar o leer datos. El modelo frecuentemente inventaba registros pasados para justificar sus rutinas o afirmaba falsamente haber guardado datos sin ejecutar la herramienta SQL. Solucionamos esto implementando un Pre-Enrutamiento Semántico en Python, forzando al LLM a entrar en compuertas de ejecución específicas (Escenario 1, 2, 3, 4) basadas en la detección de intenciones por regex antes de que el modelo genere un solo pensamiento.
2. **Bucles Infinitos de Herramientas:** Cuando la base de datos RAG devolvía literatura que carecía de una fórmula matemática específica, el LLM entraba en pánico y llamaba a la herramienta de búsqueda infinitamente. Diseñamos un "Interruptor Anti-Bucle" dentro del prompt del sistema y la arquitectura LangGraph, obligando al modelo a aceptar la primera recuperación y recurrir a reglas codificadas de Micro-Loading si la literatura no era concluyente.
3. **La Ignorancia de la Fatiga (Análisis Empírico):** Los LLMs estándar incrementaban linealmente el peso de entrenamiento sin importar la fatiga del usuario. Hipotetizamos que inyectar la lógica de Repeticiones en Reserva (RIR) solucionaría esto. Las pruebas empíricas demostraron que al LLM todavía le costaba cuantificar el agotamiento. Codificamos rígidamente la "Ley de Fatiga": si el RIR anterior fue 0 o 1, el sistema bloquea matemáticamente cualquier incremento de peso, priorizando la adaptación de volumen.
4. **Corrupción del Estado de Memoria:** El `MemorySaver` de LangGraph provocaba que el agente mezclara resultados de herramientas anteriores con peticiones actuales, llevando a la ejecución simultánea (y contradictoria) de lecturas y borrados de bases de datos. Resolvimos esto re-inicializando estrictamente el estado transitorio del grafo (`pending_delete`, `tool_results`) al inicio de cada bucle interactivo, garantizando un aislamiento temporal completo.

### 3. La Arquitectura Final: Restricciones Estrictas y Máquina de Estados

| Componente | Función | Impacto Cuantitativo |
| :--- | :--- | :--- |
| **Pre-Enrutador Semántico** | Intercepta los prompts del usuario vía regex antes de la inferencia del LLM. | Erradica el 100% de los bucles de herramientas dictando la secuencia exacta de herramientas SQL/RAG a utilizar. |
| **SQLite Transaccional** | Gestiona el estado del historial de entrenamiento con protecciones de esquema. | Previene sobrescrituras silenciosas mediante tablas unificadas y exige validación estricta de IDs antes de cualquier borrado de datos. |
| **Máquina de Estados LangGraph** | Orquesta el flujo conversacional y la memoria. | Cuenta con un nodo `interrupt` que detiene físicamente el grafo hasta recibir confirmación humana explícita para acciones destructivas. |
| **RAG Académico (ChromaDB)** | Recupera evidencia científica de PDFs biomédicos. | Fundamenta las recomendaciones de entrenamiento en literatura verificable, exponiendo incertidumbres probabilísticas. |

### 4. Comparativa: LLM Estándar vs FitLift-LLM

| Característica | LLM Estándar (ChatGPT / Claude) | FitLift-LLM |
| :--- | :--- | :--- |
| **Progresión de Carga** | Aumenta el peso de forma arbitraria o lineal. | Estrictamente limitada por reglas de Micro-Loading y Ley de Fatiga (RIR). |
| **Persistencia de Datos** | Pierde el historial al cerrar el chat. | Lectura y escritura transaccional en SQLite local. |
| **Evidencia Científica** | Inventa autores, estudios y conclusiones. | RAG indexado exclusivamente sobre literatura proporcionada por el usuario. |
| **Tono de Comunicación** | Complaciente, usa relleno motivacional. | Crítico, analítico, directo; depende fuertemente de tablas de datos. |
| **Seguridad de Datos** | Los datos residen en servidores de terceros. | Operaciones 100% Locales (Ollama + SQLite + ChromaDB). |

### 5. Ejemplo de Interacción: Ejecución en Vivo
A continuación, se muestra un extracto de la consola interactiva, que demuestra cómo la máquina de estados evalúa los datos históricos SQL, recupera la teoría RAG y aplica la Ley de Fatiga para prevenir el sobreentrenamiento.

```text
USUARIO: "Ayer hice press banca 30 kg a 6 repeticiones en 3 series con RIR 1, ¿qué me recomiendas hacer hoy?"

--- FLUJO DE EJECUCIÓN ---
  HERRAMIENTA -> consultar_historial_ejercicio
  RESULTADO -> HISTORIAL DE PRESS BANCA: 1. Fecha: 2026-10-21 | 30.0kg x 3x6 (RIR 1)

  HERRAMIENTA -> consultar_teoria_entrenamiento
  RESULTADO -> RESULTADOS RAG PARA: "progressive overload RIR hypertrophy"

IRON-AI:
Basado en tu historial, tu última sesión fue de 30 kg a 6 repeticiones en 3 series con un RIR de 1. 

Viniendo de un RIR 1, tu Sistema Nervioso Central estaba al límite. Subir el peso hoy es un error que te llevará a fallar la serie. Según la Ley de Fatiga, vamos a mantener la carga y buscar adaptación de volumen.

| Ejercicio | Series | Repeticiones | Peso | RIR Objetivo |
| :--- | :--- | :--- | :--- | :--- |
| Press Banca | 3 | 6 | 30.0 kg | 1 - 2 |
```

### 6. Referencias / Conceptos Aplicados
1. Zourdos, M. C., et al. (2016). Novel Resistance Training-Specific Rating of Perceived Exertion Scale Measuring Repetitions in Reserve. (Aplicado para la Ley de Fatiga y la arquitectura de bloqueo de carga).
2. LangChain AI. (2024). LangGraph: Building Stateful, Multi-Actor Applications with LLMs. (Aplicado para los nodos de borrado basados en interrupciones y la gestión de estado).
3. Lewis, P., et al. (2020). Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks. (Aplicado para la recuperación de evidencia académica en ChromaDB).
