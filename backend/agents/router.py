from langchain_groq import ChatGroq

llm = ChatGroq(model="llama-3.1-8b-instant")

import os
from langchain_groq import ChatGroq

llm = ChatGroq(model=os.getenv("GROQ_MODEL", "llama-3.1-8b-instant"))


async def router_node(state):
    try:
        MULTI_INTENT_KEYWORDS = [" and ", ",", " also ", " plus "]

        question = state["question"].lower()

        if any(k in question for k in MULTI_INTENT_KEYWORDS):
            state["route"] = "rag"
            state["answer"] = "Please ask one question at a time for better accuracy."
            return state

        question = state.get("question", "").lower()
        if any(word in question for word in [
            "human", "agent", "support", "talk to human", "representative"
        ]):
            state["route"] = "escalate"
            return state
        if any(word in question for word in [
            "order", "orders",
            "count", "total", "sum",
            "amount", "revenue",
            "data", "stats"
        ]):
            state["route"] = "sql"
            return state
        SMALL_TALK = ["ok", "okay", "thanks", "thank you", "cool", "nice"]

        if state["question"].lower().strip() in SMALL_TALK:
            return {
                "route": "direct",
                "answer": "Glad I could help! Let me know if you need anything else."
            }
        # ✅ RULE-BASED FIRST (fast + accurate)
        if any(word in question for word in [
            "policy", "refund", "delivery", "cancel", "order",
            "payment", "support", "company", "service"
        ]):
            state["route"] = "rag"
            return state

        if any(word in question for word in [
            "count", "total", "number", "users", "data", "stats"
        ]):
            state["route"] = "sql"
            return state

        # ✅ fallback to LLM
        prompt = f"""
        You are a router for an enterprise AI system.

        Chat History:
        {state.get("history", "")}

        User Question:
        {state['question']}

        Routes:
        - rag → documents, policies
        - sql → anything related to data, employees, ids, names, numbers
        - escalate → irrelevant or unsafe

        Rules:
        - If question mentions:
          employees, users, id, name, data, count → ALWAYS choose sql
        - Only choose escalate if completely unrelated

        Answer ONLY one word: rag / sql / escalate
        """

        response = await llm.ainvoke(prompt)
        route = response.content.strip().lower()

        if route not in ["rag", "sql"]:
            route = "rag"   # ✅ default to RAG (important)

        state["route"] = route
        return state

    except Exception as e:
        state["route"] = "rag"  # ✅ always fallback safe
        state["error"] = str(e)
        return state

