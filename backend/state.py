from typing import TypedDict, Optional


class AgentState(TypedDict):

    # =====================
    # USER INPUT
    # =====================

    question: str

    # =====================
    # SESSION
    # =====================

    session_id: Optional[str]
    user_id: Optional[str]
    company_id: Optional[str]

    history: str
    facts: list[str]

    # =====================
    # PLANNER
    # =====================

    route: Optional[str]
    plan: list

    # =====================
    # AGENT OUTPUTS
    # =====================

    sql_result: Optional[dict]
    rag_result: Optional[dict]
    memory_result: Optional[dict]

    critic_feedback: Optional[dict]
    generated_sql: Optional[str]

    # =====================
    # FINAL OUTPUT
    # =====================

    answer: Optional[str]

    confidence: Optional[float]

    requires_human: bool

    # =====================
    # OBSERVABILITY
    # =====================

    start_time: Optional[float]

    # =====================
    # ERRORS
    # =====================

    error: Optional[str]

