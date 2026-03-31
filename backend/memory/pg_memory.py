from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text
import os

engine = create_async_engine(os.getenv("POSTGRES_URL"))

async def get_user_facts(user_id):
    async with engine.connect() as conn:
        res = await conn.execute(
            text("SELECT fact FROM memory WHERE user_id=:u"),
            {"u": user_id}
        )
        return [r[0] for r in res]