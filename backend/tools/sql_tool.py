from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text
from langchain_groq import ChatGroq
import os

# ✅ DB
engine = create_async_engine(os.getenv("POSTGRES_URL"))

# ✅ LLM (NON-deprecated)
llm = ChatGroq(model="llama-3.1-8b-instant")


# ✅ SQL VALIDATOR
def validate_sql(sql: str):
    sql_lower = sql.lower()

    if "select" not in sql_lower:
        return False, "Only SELECT queries are allowed."

    if "from" not in sql_lower:
        return False, "Query is incomplete (missing FROM clause)."

    if "employees" not in sql_lower:
        return False, "Only 'employees' table is allowed."

    if "user_id" in sql_lower:
        return False, "Column 'user_id' does not exist. Use 'id'."

    return True, ""


async def sql_node(state):
    try:
        q = state.get("question", "").lower()

        schema = """
        Table: employees(id, name, email, department, role)
        """

        prompt = f"""
        Convert to SQL.

        Schema:
        {schema}

        Question:
        {q}

        Rules:
        - ONLY SELECT
        - ALWAYS use FROM employees
        - id column = id
        - name column = name
        - NO explanation
        """

        # ===== 1. TRY LLM =====
        response = await llm.ainvoke(prompt)
        sql_query = response.content.strip()

        # clean
        sql_query = sql_query.replace("```sql", "").replace("```", "").strip()
        sql_query = sql_query.split("\n")[0].strip()

        print("LLM SQL:", sql_query)

        # ===== 2. EXECUTE =====
        try:
            async with engine.connect() as conn:
                result = await conn.execute(text(sql_query))
                rows = result.fetchall()

        except Exception as e:
            print("LLM SQL FAILED:", e)

            # ===== 3. SMART FALLBACK (THIS FIXES YOUR ISSUE) =====

            if "name" in q and "id" in q:
                sql_query = "SELECT id, name FROM employees;"

            elif "name" in q:
                sql_query = "SELECT name FROM employees;"

            elif "id" in q:
                sql_query = "SELECT id FROM employees;"

            else:
                return {"answer": "I couldn't understand that query."}

            print("FALLBACK SQL:", sql_query)

            async with engine.connect() as conn:
                result = await conn.execute(text(sql_query))
                rows = result.fetchall()

        # ===== 4. FORMAT OUTPUT =====

        if not rows:
            return {"answer": "No data found."}

        # id + name
        if len(rows[0]) == 2:
            return {
                "answer": "\n".join([f"{r[0]} - {r[1]}" for r in rows])
            }

        # single column
        if len(rows[0]) == 1:
            return {
                "answer": ", ".join([str(r[0]) for r in rows])
            }

        return {"answer": str(rows)}

    except Exception as e:
        print("SQL ERROR:", e)
        return {"answer": "Something went wrong while querying the database."}