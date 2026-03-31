from langgraph.graph import StateGraph, END
from backend.agents.router import router_node
from backend.tools.rag import rag_node
from backend.tools.sql_tool import sql_node


async def escalate_node(state):
    state["answer"] = "Escalating to human support."
    return state

async def direct_node(state):
    return state

builder = StateGraph(dict)

builder.add_node("router", router_node)
builder.add_node("rag", rag_node)
builder.add_node("sql", sql_node)   # ✅ now correct
builder.add_node("escalate", escalate_node)
builder.add_node("direct", direct_node)
builder.set_entry_point("router")


def route_decision(state):
    return state.get("route", "escalate")


builder.add_conditional_edges(
    "router",
    route_decision,
    {
        "rag": "rag",
        "sql": "sql",
        "escalate": "escalate",
        "direct": "direct",
    },
)

builder.add_edge("rag", END)
builder.add_edge("sql", END)
builder.add_edge("escalate", END)

graph = builder.compile()