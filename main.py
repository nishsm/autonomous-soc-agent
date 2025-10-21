from langgraph.graph import StateGraph, START, END
from state import SOCState
from agents.siem_observer import siem_observer
from agents.recovery_planner import recovery_planner

# Build the graph
builder = StateGraph(SOCState)
builder.add_node("Observer", siem_observer)
builder.add_node("Planner", recovery_planner)

# ✅ Add entrypoint from START
builder.add_edge(START, "Observer")
builder.add_edge("Observer", "Planner")
builder.add_edge("Planner", END)

# Compile and execute
graph = builder.compile()
final_state = graph.invoke({})

print("\n✅ FINAL STATE:")
print(final_state)
