# agents/recovery_planner.py
from langchain_community.vectorstores import FAISS
from langchain_ollama import OllamaLLM, OllamaEmbeddings
from langchain.chains import RetrievalQA

def recovery_planner(state):
    """Uses RAG with Ollama to plan recovery actions."""
    suspicious = state.get("suspicious", [])
    if not suspicious:
        return {"plans": []}

    # Load FAISS index
    embeddings = OllamaEmbeddings(model="llama3")
    # Load FAISS index safely (your own trusted index)
    vectorstore = FAISS.load_local(
        "knowledge_base/faiss_index",
        embeddings,
        allow_dangerous_deserialization=True  # <-- add this
    )
    retriever = vectorstore.as_retriever(search_kwargs={"k": 3})


    # Initialize LLM for generation
    llm = OllamaLLM(model="llama3")  # replace with your model name
    qa = RetrievalQA.from_chain_type(llm=llm, retriever=retriever)

    plans = []
    for event in suspicious:
        query = f"Create a recovery plan for user={event['user']} given abnormal activity: {event}"
        response = qa.run(query)
        plans.append({"user": event["user"], "plan": response})

    print("🟢 [Planner] Recovery plans:", plans)
    return {"plans": plans}
