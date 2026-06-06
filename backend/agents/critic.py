import os

from langchain_groq import ChatGroq

from backend.state import AgentState


llm = ChatGroq(
    model=os.getenv(
        "GROQ_MODEL",
        "llama-3.1-8b-instant"
    )
)


async def critic_agent(
    state: AgentState
):

    sql_result = state.get(
        "sql_result"
    )

    rag_result = state.get(
        "rag_result"
    )

    memory_result = state.get(
        "memory_result"
    )

    prompt = f"""
You are a critic agent.

Review outputs from multiple agents.

SQL Agent Output:
{sql_result}

RAG Agent Output:
{rag_result}

Memory Agent Output:
{memory_result}

Tasks:

1. Detect contradictions
2. Detect missing evidence
3. Detect weak answers

Return concise feedback.
"""

    response = await llm.ainvoke(
        prompt
    )

    state["critic_feedback"] = {
        "feedback":
        response.content
    }

    return state