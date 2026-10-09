from langchain_community.vectorstores import FAISS
from langchain_ollama import OllamaLLM, OllamaEmbeddings
from langchain.chains import RetrievalQA

MAX_EVENTS = 50

def data_incomplete(state):
    for event in state.get("pending_tasks", []):
        if not event.get("user") and not event.get("Source IP") and not event.get("Dst IP"):
            return True
    return False

def request_more_data(state):
    print("🟠 [Planner] Requesting more data for incomplete events...")
    # Here you could query other agents or external systems for info
    for event in state.get("pending_tasks", []):
        if not event.get("user") and not event.get("Source IP") and not event.get("Dst IP"):
            event["user"] = "unknown_user"
    return state

def generate_recovery_plan(event, qa):
    user = event.get("user") or event.get("Source IP") or event.get("Dst IP") or "unknown"
    query = f"Create a recovery plan for user={user} given abnormal activity: {event}"
    try:
        response = qa.invoke({"query": query})["result"]
    except Exception as e:
        print(f"⚠️ Planner error for event {user}: {e}")
        response = "Failed to generate plan"
    return response

def recovery_planner(state):
    if "pending_tasks" not in state:
        state["pending_tasks"] = []
    if "completed_tasks" not in state:
        state["completed_tasks"] = []
    if "plans" not in state:
        state["plans"] = []

    suspicious = state.get("suspicious", [])
    for event in suspicious:
        if event not in state["pending_tasks"] and event not in state["completed_tasks"]:
            state["pending_tasks"].append(event)

    while True:
        if not state["pending_tasks"]:
            print("🟢 [Planner] No pending tasks, planning complete.")
            break

        if data_incomplete(state):
            state = request_more_data(state)
            continue

        embeddings = OllamaEmbeddings(model="llama3")
        vectorstore = FAISS.load_local(
            "knowledge_base/faiss_index",
            embeddings,
            allow_dangerous_deserialization=True
        )
        retriever = vectorstore.as_retriever(search_kwargs={"k": 3})
        llm = OllamaLLM(model="llama3")
        qa = RetrievalQA.from_chain_type(llm=llm, retriever=retriever)

        plans_this_cycle = []

        for event in state["pending_tasks"][:MAX_EVENTS]:
            plan = generate_recovery_plan(event, qa)
            plans_this_cycle.append({"user": event.get("user", "unknown"), "plan": plan})
            state["completed_tasks"].append(event)

        state["pending_tasks"] = state["pending_tasks"][MAX_EVENTS:]
        state["plans"].extend(plans_this_cycle)
        print(f"🟢 [Planner] Generated {len(plans_this_cycle)} recovery plans this cycle.")

        if not state["pending_tasks"]:
            break

    return state
