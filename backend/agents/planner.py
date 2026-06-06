
import os

from dotenv import load_dotenv

from langchain_groq import ChatGroq

from backend.state import AgentState

load_dotenv()

llm = ChatGroq(
    model=os.getenv(
        "GROQ_MODEL",
        "llama-3.1-8b-instant"
    )
)


async def planner_node(
    state: AgentState
):

    question = state["question"]

    prompt = f"""
You are an enterprise AI planner.

Available Agents:

SQL Agent:
- employees
- customers
- products
- sales
- support tickets

RAG Agent:
- company policies
- reports
- manuals
- knowledge base

Decide which agents are required.

Return ONLY one of:

sql
rag
both
escalate

Examples:

What is the leave policy?
rag

Show all employees.
sql

Why did APAC revenue decrease?
both

Hack the company database.
escalate

Question:
{question}
"""

    response = await llm.ainvoke(
        prompt
    )

    decision = (
        response.content
        .strip()
        .lower()
    )

    if decision not in [
        "sql",
        "rag",
        "both",
        "escalate"
    ]:
        decision = "rag"

    state["route"] = decision

    # =====================================
    # BUILD EXECUTION PLAN
    # =====================================

    if decision == "sql":

        state["plan"] = [
            "sql"
        ]

    elif decision == "rag":

        state["plan"] = [
            "rag"
        ]

    elif decision == "both":

        state["plan"] = [
            "sql",
            "rag"
        ]

    else:

        state["plan"] = [
            "escalate"
        ]

    return state