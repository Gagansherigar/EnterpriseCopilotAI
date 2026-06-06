async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with AsyncSessionLocal() as session:

        result = await session.execute(
            text("SELECT COUNT(*) FROM employees")
        )

        if result.scalar() > 0:
            return

        employees = [
            Employee(
                name="Amit Sharma",
                email="amit@acmeelectronics.com",
                department="Engineering",
                role="Senior Backend Engineer"
            ),
            Employee(
                name="Priya Verma",
                email="priya@acmeelectronics.com",
                department="HR",
                role="HR Manager"
            ),
            Employee(
                name="Rahul Singh",
                email="rahul@acmeelectronics.com",
                department="Sales",
                role="Regional Sales Executive"
            ),
        ]

        customers = [
            Customer(
                name="RetailCorp",
                industry="Retail",
                region="APAC",
                contract_value=500000
            ),
            Customer(
                name="HealthPlus",
                industry="Healthcare",
                region="North America",
                contract_value=900000
            ),
        ]

        products = [
            Product(
                name="SmartSensor X",
                category="IoT"
            ),
            Product(
                name="EdgeGateway Pro",
                category="Networking"
            ),
        ]

        sales = [
            Sale(
                product_name="SmartSensor X",
                region="APAC",
                quarter="Q1-2026",
                revenue=420000,
                units_sold=1200
            ),
            Sale(
                product_name="SmartSensor X",
                region="APAC",
                quarter="Q2-2026",
                revenue=310000,
                units_sold=850
            ),
            Sale(
                product_name="EdgeGateway Pro",
                region="APAC",
                quarter="Q2-2026",
                revenue=190000,
                units_sold=420
            ),
        ]

        tickets = [
            SupportTicket(
                customer_name="RetailCorp",
                issue_type="Shipment Delay",
                priority="High",
                status="Open"
            ),
            SupportTicket(
                customer_name="RetailCorp",
                issue_type="Device Failure",
                priority="Medium",
                status="Closed"
            ),
        ]

        session.add_all(employees)
        session.add_all(customers)
        session.add_all(products)
        session.add_all(sales)
        session.add_all(tickets)

        await session.commit()

        print("✅ Enterprise seed data inserted")