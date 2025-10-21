# Autonomous SOC Agentic System

A modular, multi-agent system that simulates a Security Operations Center (SOC) workflow.  
This system uses:

- **LangGraph** to manage state transitions between agents
- **Ollama** for local embeddings and LLM generation
- **FAISS** for RAG-style retrieval from a local knowledge base
- **Pandas & Scikit-Learn** for anomaly detection

---

## Project Structure

autonomous-soc-agentic-system/
│
├─ agents/
│ ├─ siem_observer.py # Collects logs & detects anomalies
│ └─ recovery_planner.py # Generates recovery plans using Ollama + FAISS
│
├─ knowledge_base/
│ └─ create_vector_store.py # Builds FAISS index with Ollama embeddings
│
├─ state.py # Defines SOCState
├─ main.py # Runs the full agent pipeline
└─ README.md


---

## Requirements

- Python 3.9+
- [Ollama](https://ollama.com/download) installed and running
- Python packages:

```bash
pip install langgraph langchain langchain-ollama langchain-community pandas scikit-learn faiss-cpu
```

⚠️ Note: langchain imports have changed in v0.2+, so we now use langchain_community for FAISS and embeddings.

Setup & Running

1. Start Ollama Daemon
    ```
    ollama serve
    ```
    Ensure your local model is installed (llama3 in this project). You can check with:
    ```
    ollama list
    ```

2. Create FAISS Vector Store
    ```
    python3 knowledge_base/create_vector_store.py
    ```

    * Stores local FAISS index at knowledge_base/faiss_index

    * Uses Ollama embeddings for document vectors

    * Debugging notes:

        - If you previously used OpenAI embeddings, switch to Ollama.

        - Avoid pickling errors by saving FAISS locally using save_local().

        - If you see AttributeError: 'function' object has no attribute 'embed_documents', ensure you’re using OllamaEmbeddings and not a function.

3. Run Main Pipeline
    ```
    python3 main.py
    ```
    Steps performed:

    * SIEM Observer: detects suspicious logs with an Isolation Forest

    * Recovery Planner: generates recovery plans using RAG (FAISS + Ollama LLM)

    * Final State: prints plans in a structured format

    ```
    🟡 [Observer] Suspicious logs: [{'user': 'eve', 'login_attempts': 10, 'files_accessed': 9, 'is_suspicious': True}]
    🟢 [Planner] Recovery plans: [{'user': 'eve', 'plan': '...plan text...'}]

    ✅ FINAL STATE:
    {'plans': [{'user': 'eve', 'plan': '...plan text...'}]}
    ```

## Key Code Updates

1. Recovery Planner (agents/recovery_planner.py)

    * Switched to Ollama LLM and OllamaEmbeddings

    * Loads FAISS index safely with:
        ```
        vectorstore = FAISS.load_local(
            "knowledge_base/faiss_index",
            embeddings,
            allow_dangerous_deserialization=True
        )
        ```
    * RAG QA replaced .run() with .invoke() to avoid deprecation warnings:
        ```
        response = qa.invoke(query)
        ```
    
2. SIEM Observer (agents/siem_observer.py)

    * Detects suspicious logins with IsolationForest
    * Returns suspicious events for the planner

3. FAISS Vector Store (knowledge_base/create_vector_store.py)

    * Creates FAISS index locally

    * Uses OllamaEmbeddings to embed sample documents

    * Avoids pickling _thread.RLock errors by saving FAISS via save_local() instead of pickling

## Debugging Notes

1. SSL warning (LibreSSL vs OpenSSL):
    ```
    NotOpenSSLWarning: urllib3 v2 only supports OpenSSL 1.1.1+, currently the 'ssl' module is compiled with 'LibreSSL 2.8.3'
    ```
    * Can be ignored; it doesn’t prevent the code from running on macOS

2. Ollama connection error:
    ```
    ConnectionError: Failed to connect to Ollama.
    ```
    * Ensure ollama serve is running
    * Verify your model exists with ollama list

3. FAISS deserialization error:
    ```
    allow_dangerous_deserialization=True
    ```
    * Must be set for locally created FAISS indices

4. LangChain deprecation warnings:
    * .run() → .invoke()
    * langchain.vectorstores → langchain_community.vectorstores
    * OpenAIEmbeddings → OllamaEmbeddings


## Next Steps / Improvements:

* Auto-create FAISS vector store if missing in main.py

* Expand SIEM observer to handle real log ingestion

* Improve RAG queries with additional context or multi-step reasoning

* Add multi-agent logging & monitoring for production SOC simulation


## Authors

Nishanth, Serena

## References

* [Ollama Docs](https://ollama.com/docs)
* [LangChain Docs](https://python.langchain.com/en/latest/)
* [FAISS Documentation](https://github.com/facebookresearch/faiss)
