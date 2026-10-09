from langgraph.graph import StateGraph, START, END
from state import SOCState
from agents.siem_observer import siem_observer
from agents.recovery_planner import recovery_planner
from time import sleep

# Build LangGraph Pipeline
builder = StateGraph(SOCState)
builder.add_node("Observer", siem_observer)
builder.add_node("Planner", recovery_planner)
builder.add_edge(START, "Observer")
builder.add_edge("Observer", "Planner")
builder.add_edge("Planner", END)
graph = builder.compile()

# Run workflow for multiple cycles to enable agentic looping
state = SOCState()
for cycle in range(5):
    print(f"\nCycle {cycle+1} running")
    state = graph.invoke(state)
    sleep(1)  # Simulate delay or external data acquisition

print("\n✅ FINAL STATE:")
print(state)
