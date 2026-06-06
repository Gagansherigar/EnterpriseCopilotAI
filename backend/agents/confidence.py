from backend.state import AgentState


async def confidence_node(
    state: AgentState
):

    score = 0.0

    sql_result = state.get(
        "sql_result"
    )

    rag_result = state.get(
        "rag_result"
    )

    # SQL confidence

    if (
        sql_result and
        sql_result.get("success")
    ):
        score += 0.5

    # RAG confidence

    if (
        rag_result and
        rag_result.get("success")
    ):
        score += 0.5

    confidence = round(
        score,
        2
    )

    state["confidence"] = (
        confidence
    )

    if confidence < 0.5:

        state[
            "requires_human"
        ] = True

    return state