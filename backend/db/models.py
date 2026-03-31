from sqlalchemy.orm import declarative_base, Mapped, mapped_column
from sqlalchemy import Integer, String

Base = declarative_base()


class Employee(Base):
    __tablename__ = "employees"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String)
    email: Mapped[str] = mapped_column(String)
    department: Mapped[str] = mapped_column(String)
    role: Mapped[str] = mapped_column(String)