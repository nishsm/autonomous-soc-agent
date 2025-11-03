# agents/recovery_planner.py

from langchain_community.vectorstores import FAISS
from langchain_ollama import OllamaLLM, OllamaEmbeddings
from langchain.chains import RetrievalQA

# Limit number of suspicious events to process at a time
MAX_EVENTS = 50

def recovery_planner(state):
    """
    Uses RAG with Ollama to plan recovery actions based on suspicious events
    detected by the SIEM observer.
    """
    suspicious = state.get("suspicious", [])
    if not suspicious:
        print("🟢 [Planner] No suspicious events to plan for.")
        return {"plans": []}

    # Load FAISS index
    embeddings = OllamaEmbeddings(model="llama3")
    vectorstore = FAISS.load_local(
        "knowledge_base/faiss_index",
        embeddings,
        allow_dangerous_deserialization=True
    )
    retriever = vectorstore.as_retriever(search_kwargs={"k": 3})

    # Initialize LLM for generation
    llm = OllamaLLM(model="llama3")
    qa = RetrievalQA.from_chain_type(llm=llm, retriever=retriever)

    plans = []
    for event in suspicious[:MAX_EVENTS]:
        # Safely get 'user', fallback to Source IP, Dest IP, or 'unknown'
        user = event.get("user") or event.get("Source IP") or event.get("Dst IP") or "unknown"

        query = f"Create a recovery plan for user={user} given abnormal activity: {event}"
        try:
            response = qa.invoke({"query": query})["result"]
        except Exception as e:
            print(f"⚠️ Planner error for event {user}: {e}")
            response = "Failed to generate plan"

        plans.append({"user": user, "plan": response})

    print(f"🟢 [Planner] Generated {len(plans)} recovery plans.")
    return {"plans": plans}
