from langgraph.graph import (
    StateGraph,
    END
)

from backend.state import AgentState

from backend.agents.planner import (
    planner_node
)

from backend.agents.synthesizer import (
    synthesizer_node
)

from backend.agents.confidence import (
    confidence_node
)

from backend.tools.rag import (
    rag_node
)

from backend.tools.sql_tool import (
    sql_node
)

from backend.tools.escalation import (
    escalate_node
)


builder = StateGraph(
    AgentState
)


# =====================================================
# NODES
# =====================================================

builder.add_node(
    "planner",
    planner_node
)

builder.add_node(
    "sql",
    sql_node
)

builder.add_node(
    "rag",
    rag_node
)

builder.add_node(
    "synthesizer",
    synthesizer_node
)

builder.add_node(
    "confidence",
    confidence_node
)

builder.add_node(
    "escalate",
    escalate_node
)


# =====================================================
# ENTRY
# =====================================================

builder.set_entry_point(
    "planner"
)


# =====================================================
# ROUTING
# =====================================================

def planner_router(
    state: AgentState
):

    plan = state.get(
        "plan",
        []
    )

    if "escalate" in plan:
        return "escalate"

    if "sql" in plan and "rag" in plan:
        return "both"

    if "sql" in plan:
        return "sql"

    if "rag" in plan:
        return "rag"

    return "escalate"


builder.add_conditional_edges(
    "planner",
    planner_router,
    {
        "sql": "sql",
        "rag": "rag",
        "both": "sql",
        "escalate": "escalate",
    },
)


# =====================================================
# SQL FLOW
# =====================================================

builder.add_edge(
    "sql",
    "synthesizer"
)


# =====================================================
# RAG FLOW
# =====================================================

builder.add_edge(
    "rag",
    "synthesizer"
)


# =====================================================
# SYNTHESIS
# =====================================================

builder.add_edge(
    "synthesizer",
    "confidence"
)


# =====================================================
# CONFIDENCE
# =====================================================

def confidence_router(
    state: AgentState
):

    if state.get(
        "requires_human",
        False
    ):
        return "escalate"

    return "end"


builder.add_conditional_edges(
    "confidence",
    confidence_router,
    {
        "escalate": "escalate",
        "end": END,
    },
)


# =====================================================
# ESCALATION
# =====================================================

builder.add_edge(
    "escalate",
    END
)


graph = builder.compile()