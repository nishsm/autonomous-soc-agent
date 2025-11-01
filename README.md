# Autonomous SOC Agentic System

A modular, multi-agent Python system simulating Security Operations Center (SOC) workflows. Designed for educational and research scenarios, it integrates anomaly detection, Recovery Planning, and Retrieval-Augmented Generation (RAG) using local LLMs and knowledge bases.

---

## Features

- **Agent-based architecture** modeling workflow transitions in an SOC.
- **SIEM Observer agent**: Detects anomalous behaviors in logs using Isolation Forests (scikit-learn).
- **Recovery Planner agent**: Generates context-aware recovery plans with local LLM (Ollama) and FAISS-powered RAG.
- **Knowledge base integration**: Uses local documents, embedded via LangChain/Ollama, for fast semantic retrieval.
- **Modular codebase** for rapid extension, including real log integration and multi-agent communication.

---

## Project Structure

```
initial-langraph/
│
├── agents/
│   ├── recovery_planner.py         # Generates recovery plans using Ollama LLM and FAISS
│   └── siem_observer.py            # Collects logs and detects anomalies
│
├── knowledge_base/
│   ├── faiss_index/
│   │   ├── index.faiss
│   │   └── index.pkl
│   └── recovery_docs/
│       ├── account_recovery.txt
│       ├── network_threats.md
│       ├── build_index.py          # RAG vector store builder
│       └── create_vector_store.py  # Automates FAISS index creation with Ollama embeddings
│
├── models/
│   └── anomaly_detector.py
│
├── README.md
├── main.py                         # Coordinates the pipeline
└── state.py                        # Defines agent state and transitions
```

---

## Requirements

- Python 3.9+  
- [Ollama](https://ollama.com/) running locally (`ollama serve`), with your preferred model (e.g., llama3) installed.  
- Pip packages:
  ```bash
  pip install langgraph langchain langchain-ollama langchain-community pandas scikit-learn faiss-cpu
  ```

_Note: For LangChain v0.2+, use `langchain_community` for embeddings and vectorstores._

---

## Installation & Setup

### 1. Clone repository
```bash
git clone https://github.com/serenagomez1304/autonomous-soc-agentic-system.git
cd autonomous-soc-agentic-system
```

### 2. Install dependencies
```bash
pip install langgraph langchain langchain-ollama langchain-community pandas scikit-learn faiss-cpu
```

### 3. Start Ollama daemon and ensure model
```bash
ollama serve
ollama list   # Confirm your model (e.g., llama3) is available
```

### 4. Build and initialize the FAISS vector store
```bash
python3 knowledge_base/create_vector_store.py
```
- Embeds your knowledge base using Ollama and constructs the FAISS index locally.  
- Indices are saved at: `knowledge_base/faiss_index`  

### 5. Run the main pipeline
```bash
python3 main.py
```
- The SIEM Observer agent simulates log analysis and flags suspicious activity.  
- The Recovery Planner agent uses your local knowledge base and LLM to propose detailed recovery steps.  
- Final output prints structured recovery plans to the console.  

---

## Troubleshooting & Notes

- **Ollama connection errors**: Ensure `ollama serve` is running before script execution.  
- **FAISS deserialization issues**: Set `allow_dangerous_deserialization=True` when loading local indices.  
- **LangChain API updates**: Use `.invoke()` instead of `.run()`. Replace `OpenAIEmbeddings` with `OllamaEmbeddings`.  
- **SSL warnings on macOS**: LibreSSL/urllib3 warnings are ignorable unless connectivity fails.  

---

## Key Components

| Script | Purpose |
|--------|----------|
| `agents/siem_observer.py` | Log monitoring and anomaly detection with Isolation Forest |
| `agents/recovery_planner.py` | Generates recovery steps using FAISS+Ollama RAG pipeline |
| `main.py` | Manages end-to-end agent workflow, outputting structured plans |
| `knowledge_base/create_vector_store.py` | Indexes docs (txt/md) using Ollama embeddings for retrieval |
| `state.py` | Defines SOC state and agent transitions |
| `models/anomaly_detector.py` | Additional anomaly detection utilities (optional/expandable) |

---

## Example Run

```bash
python3 main.py
```

**Output Example:**  
```
SIEM Observer: Detected suspicious login (user: eve, login_attempts: 10, files_accessed: 9)
Recovery Planner: Generated plan for eve
Plan: [Step-by-step recovery actions based on local knowledge base...]
Final state: all suspicious events handled and recovery plans output.
```

---

## Extending & Roadmap

- Integrate real log ingestion for SIEM observer.  
- Improve RAG queries with multi-step reasoning and better context assembly.  
- Add multi-agent logging, dashboards, or notifications for production-style SOC simulation.  
- Expand recovery knowledge base with more threat/incident response scenarios.  

---

## Credits & References

- [Ollama Docs](https://ollama.com)  
- [LangChain Documentation](https://python.langchain.com)  
- [FAISS Documentation](https://github.com/facebookresearch/faiss)  
- Scikit-Learn & Pandas for data analysis.  

---

## Authors

Project by **Nishanth** and **Serena**
