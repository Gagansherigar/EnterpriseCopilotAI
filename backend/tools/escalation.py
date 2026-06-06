from sqlalchemy import insert

from backend.db.session import AsyncSessionLocal
from backend.db.models import EscalationTicket

from backend.state import AgentState


async def escalate_node(
    state: AgentState
):

    try:

        question = state["question"]

        confidence = state.get(
            "confidence",
            0.0
        )

        reason = state.get(
            "error",
            "Low confidence response"
        )

        async with AsyncSessionLocal() as session:

            ticket = EscalationTicket(
                question=question,
                reason=reason,
                status="OPEN",
                assigned_to=None
            )

            session.add(ticket)

            await session.commit()

        state["requires_human"] = True

        state["answer"] = (
            "Your request has been escalated "
            "to a human reviewer."
        )

        return state

    except Exception as e:

        state["error"] = str(e)

        state["answer"] = (
            "Failed to create escalation ticket."
        )

        return state