from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from backend.db.models import Base, Employee
import os
from sqlalchemy import text
DATABASE_URL = os.getenv("POSTGRES_URL")

engine = create_async_engine(DATABASE_URL, echo=True)

AsyncSessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False
)


async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with AsyncSessionLocal() as session:


        result = await session.execute(
            text("SELECT COUNT(*) FROM employees")
        )
        count = result.scalar()

        if count == 0:
            employees = [
                Employee(name="Amit Sharma", email="amit@company.com", department="Engineering", role="Developer"),
                Employee(name="Priya Verma", email="priya@company.com", department="HR", role="Manager"),
                Employee(name="Rahul Singh", email="rahul@company.com", department="Sales", role="Executive"),
                Employee(name="Neha Gupta", email="neha@company.com", department="Marketing", role="Lead"),
                Employee(name="Arjun Mehta", email="arjun@company.com", department="Engineering", role="Backend Engineer"),
                Employee(name="Sneha Reddy", email="sneha@company.com", department="Finance", role="Analyst"),
                Employee(name="Karan Patel", email="karan@company.com", department="Support", role="Agent"),
                Employee(name="Anjali Nair", email="anjali@company.com", department="HR", role="Recruiter"),
            ]

            session.add_all(employees)
            await session.commit()

            print("✅ Seed data inserted")