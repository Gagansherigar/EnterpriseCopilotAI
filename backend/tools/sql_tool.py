from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text
from langchain_groq import ChatGroq
import os

from backend.state import AgentState

engine = create_async_engine(os.getenv("POSTGRES_URL"))

llm = ChatGroq(
    model=os.getenv(
        "GROQ_MODEL",
        "llama-3.1-8b-instant"
    )
)


def validate_sql(sql: str):

    sql_lower = sql.lower().strip()

    forbidden = [
        "drop",
        "delete",
        "update",
        "alter",
        "truncate",
        "insert",
    ]

    if any(word in sql_lower for word in forbidden):
        return False, "Dangerous SQL operation detected."

    if not sql_lower.startswith("select"):
        return False, "Only SELECT queries are allowed."

    return True, ""


async def sql_node(state: AgentState):

    try:

        question = state["question"]

        schema = """
        employees(
            id,
            name,
            email,
            department,
            role,
            manager,
            location,
            salary
        )

        customers(
            id,
            name,
            industry,
            region,
            contract_value,
            account_manager
        )

        products(
            id,
            name,
            category,
            status,
            launch_date
        )

        sales(
            id,
            product_id,
            region,
            quarter,
            revenue,
            units_sold
        )

        support_tickets(
            id,
            customer_id,
            issue_type,
            priority,
            status,
            created_at
        )
        """

        prompt = f"""
        Convert the user's question into PostgreSQL SQL.

        Schema:
        {schema}

        Rules:
        - Only generate SQL
        - Only SELECT statements
        - No markdown
        - No explanation
        - Add LIMIT 100 if not present

        Question:
        {question}
        """

        response = await llm.ainvoke(prompt)

        sql_query = response.content.strip()

        sql_query = (
            sql_query
            .replace("```sql", "")
            .replace("```", "")
            .strip()
        )

        valid, error = validate_sql(sql_query)

        if not valid:
            state["error"] = error
            state["requires_human"] = True

            state["sql_result"] = {
                "success": False,
                "error": error
            }

            return state

        if "limit" not in sql_query.lower():
            sql_query += " LIMIT 100"

        async with engine.connect() as conn:

            result = await conn.execute(
                text(sql_query)
            )

            rows = result.fetchall()

            columns = list(result.keys())

        state["sql_result"] = {
            "success": True,
            "query": sql_query,
            "columns": columns,
            "rows": [list(row) for row in rows]
        }

        return state

    except Exception as e:

        state["sql_result"] = {
            "success": False,
            "error": str(e)
        }

        state["error"] = str(e)

        return state