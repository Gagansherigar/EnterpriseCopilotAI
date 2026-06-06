from sqlalchemy.ext.asyncio import (
    create_async_engine,
    AsyncSession
)

from sqlalchemy.orm import sessionmaker

DATABASE_URL = (
    "postgresql+asyncpg://postgres:postgres@localhost:5432/enterprise_ai"
)

engine = create_async_engine(
    DATABASE_URL,
    echo=False
)

AsyncSessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False
)