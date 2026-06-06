from datetime import datetime

from sqlalchemy import (
    Integer,
    String,
    Float,
    DateTime,
    Text,
    ForeignKey
)

from sqlalchemy.orm import (
    declarative_base,
    Mapped,
    mapped_column
)

Base = declarative_base()


# -------------------------
# Employees
# -------------------------

class Employee(Base):
    __tablename__ = "employees"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    name: Mapped[str] = mapped_column(String(100))
    email: Mapped[str] = mapped_column(String(100), unique=True)

    department: Mapped[str] = mapped_column(String(50))
    role: Mapped[str] = mapped_column(String(50))

    manager: Mapped[str] = mapped_column(String(100))
    location: Mapped[str] = mapped_column(String(50))

    salary: Mapped[int] = mapped_column(Integer)




class Customer(Base):
    __tablename__ = "customers"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    name: Mapped[str] = mapped_column(String(100))

    industry: Mapped[str] = mapped_column(String(50))

    region: Mapped[str] = mapped_column(String(50))

    contract_value: Mapped[float] = mapped_column(Float)

    account_manager: Mapped[str] = mapped_column(String(100))




class Product(Base):
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    name: Mapped[str] = mapped_column(String(100))

    category: Mapped[str] = mapped_column(String(50))

    status: Mapped[str] = mapped_column(String(30))

    launch_date: Mapped[datetime] = mapped_column(DateTime)



class Sale(Base):
    __tablename__ = "sales"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    product_id: Mapped[int] = mapped_column(
        ForeignKey("products.id")
    )

    region: Mapped[str] = mapped_column(String(50))

    quarter: Mapped[str] = mapped_column(String(20))

    revenue: Mapped[float] = mapped_column(Float)

    units_sold: Mapped[int] = mapped_column(Integer)


class SupportTicket(Base):
    __tablename__ = "support_tickets"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    customer_id: Mapped[int] = mapped_column(
        ForeignKey("customers.id")
    )

    issue_type: Mapped[str] = mapped_column(String(100))

    priority: Mapped[str] = mapped_column(String(20))

    status: Mapped[str] = mapped_column(String(20))

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow
    )




class EscalationTicket(Base):
    __tablename__ = "escalation_tickets"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    question: Mapped[str] = mapped_column(Text)

    reason: Mapped[str] = mapped_column(String(200))

    status: Mapped[str] = mapped_column(
        String(20),
        default="OPEN"
    )

    assigned_to: Mapped[str] = mapped_column(
        String(100),
        nullable=True
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow
    )




class AgentExecutionLog(Base):
    __tablename__ = "agent_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    question: Mapped[str] = mapped_column(Text)

    chosen_route: Mapped[str] = mapped_column(
        String(50)
    )

    generated_sql: Mapped[str] = mapped_column(
        Text,
        nullable=True
    )

    confidence: Mapped[float] = mapped_column(Float)

    latency_ms: Mapped[int] = mapped_column(Integer)

    final_answer: Mapped[str] = mapped_column(Text)

    timestamp: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow
    )