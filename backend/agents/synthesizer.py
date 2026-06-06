import os

from langchain_groq import ChatGroq

from backend.state import AgentState


llm = ChatGroq(
    model=os.getenv(
        "GROQ_MODEL",
        "llama-3.1-8b-instant"
    )
)


async def synthesizer_node(
    state: AgentState
):

    question = state["question"]

    sql_result = state.get(
        "sql_result"
    )

    rag_result = state.get(
        "rag_result"
    )

    memory_result = state.get(
        "memory_result"
    )

    critic_feedback = state.get(
        "critic_feedback"
    )

    prompt = f"""
You are the Synthesis Agent in a multi-agent enterprise copilot.

Your job is to create the final answer by combining outputs from specialized agents.

==================================================
USER QUESTION
==================================================

{question}

==================================================
SQL AGENT OUTPUT
==================================================

{sql_result}

==================================================
RAG AGENT OUTPUT
==================================================

{rag_result}

==================================================
MEMORY AGENT OUTPUT
==================================================

{memory_result}

==================================================
CRITIC AGENT FEEDBACK
==================================================

{critic_feedback}

==================================================
INSTRUCTIONS
==================================================

1. Combine information from all agents.
2. Prefer factual evidence from SQL results.
3. Use RAG results for explanations and context.
4. Use Memory results for conversation continuity.
5. Consider Critic feedback before answering.
6. Do not hallucinate.
7. If evidence is weak, explicitly state uncertainty.
8. If information is missing, say so.
9. Produce a professional enterprise response.

Generate the final answer only.
"""

    response = await llm.ainvoke(
        prompt
    )

    state["answer"] = (
        response.content.strip()
    )

    return state