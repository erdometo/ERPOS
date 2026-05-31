import os
import json
import hashlib
from datetime import datetime, timedelta
import random
import bcrypt
from sqlalchemy import text
from sqlalchemy.orm import sessionmaker

# Import from our central core.db module
from core.db import (
    engine, User, Product, Order, OrderItem, GraphNode, GraphEdge, 
    VectorPartition, AuditLedger, Task, Base
)

def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def init_db():
    # Drop dynamic courier_shipments table if it exists
    with engine.connect() as conn:
        conn.execute(text("DROP TABLE IF EXISTS courier_shipments"))
        conn.commit()
    # Drop all tables and recreate them using unified metadata
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    return engine

def seed_data(engine):
    Session = sessionmaker(bind=engine)
    session = Session()

    session.query(User).delete()
    session.query(Product).delete()
    session.query(Order).delete()
    session.query(OrderItem).delete()
    session.query(GraphNode).delete()
    session.query(GraphEdge).delete()
    session.query(VectorPartition).delete()
    session.query(AuditLedger).delete()
    session.query(Task).delete()
    session.commit()

    # Clear external Neo4j and Qdrant graph and vector stores
    from middleware import ShieldGateway
    gateway = ShieldGateway()
    gateway.graph_adapter.clear_all()
    gateway.vector_adapter.clear_all()

    # Seed Users
    hashed_pwd = hash_password("password123")
    users = [
        User(name="Alice Smith", email="alice@example.com", role="admin", password_hash=hashed_pwd),
        User(name="Bob Jones", email="bob@example.com", role="employee", password_hash=hashed_pwd),
        User(name="Charlie Brown", email="charlie@example.com", role="customer", password_hash=hashed_pwd),
        User(name="Diana Prince", email="diana@example.com", role="customer", password_hash=hashed_pwd),
    ]
    session.add_all(users)
    
    # Seed Products with different clearance levels
    # 1: Customer (public), 2: Employee (internal), 3: Admin (secret/restricted)
    products = [
        Product(name="Ergonomic Chair", category="Furniture", price=299.99, stock_quantity=50, clearance_level=1),
        Product(name="Standing Desk", category="Furniture", price=499.50, stock_quantity=30, clearance_level=1),
        Product(name="Laptop Stand", category="Accessories", price=45.00, stock_quantity=100, clearance_level=1),
        Product(name="Wireless Mouse", category="Electronics", price=29.99, stock_quantity=200, clearance_level=1),
        Product(name="Mechanical Keyboard", category="Electronics", price=120.00, stock_quantity=75, clearance_level=1),
        # Internal employee-only stock
        Product(name="Quantum Processor v1", category="Hardware", price=1250.00, stock_quantity=10, clearance_level=2),
        # Admin restricted cluster node
        Product(name="Mainframe Core Server Cluster", category="Infrastructure", price=8999.00, stock_quantity=3, clearance_level=3),
    ]
    session.add_all(products)
    session.commit()

    # Create random orders
    customers = session.query(User).filter_by(role="customer").all()
    all_products = session.query(Product).filter(Product.clearance_level <= 1).all()
    for _ in range(10):
        customer = random.choice(customers)
        order = Order(
            user_id=customer.id,
            total_amount=0,
            status=random.choice(["pending", "shipped", "delivered"]),
            created_at=datetime.utcnow() - timedelta(days=random.randint(0, 10))
        )
        session.add(order)
        session.commit()

        total_amount = 0
        selected_products = random.sample(all_products, random.randint(1, 3))
        for p in selected_products:
            qty = random.randint(1, 2)
            order_item = OrderItem(order_id=order.id, product_id=p.id, quantity=qty, unit_price=p.price)
            session.add(order_item)
            total_amount += (qty * p.price)
        order.total_amount = round(total_amount, 2)
        session.commit()

    # --- Seeding Graph Nodes with Embedded skill.md files ---
    
    skill_order_validation = """
# Skill: Order Validation & Risk Inspection

## Purpose
Enforces internal regulations, laws, and warehouse limits on incoming customer transactions.

## Execution Rules
1. **Inventory Verification**: Extract requested product counts. If stock_quantity < quantity, trigger WAITING_REORDER state.
2. **High-Value Auditing**: Compare transaction total to current threshold limits. If total > threshold, flag transaction as ANOMALOUS.
3. **Discount Enforcement**: Ensure standard maximum discount values are preserved.

## Constraints
- Max Allowed General Transaction Threshold is set dynamically by High Value Transaction Policy.
- Restrict bulk item purchases if warehouse log limits are active.
"""

    node1 = GraphNode(
        label="workflow",
        name="Order Verification Workflow",
        description="Core workflow sequence that runs upon incoming customer orders.",
        skill_markdown=skill_order_validation.strip(),
        properties=json.dumps({"version": "2.1.0", "active": True}),
        clearance_level=1
    )

    skill_high_value = """
# Skill: High Value Transaction Policy

## Purpose
Defines constraints, MFA requirements, and override approvals for large corporate orders.

## Regulatory Settings
- **Threshold Limit**: $500.00
- **Requirement**: Any transaction above this threshold must require dual-officer signature or manual waive override.
- **Enforcement Scope**: Worldwide corporate transactions.
"""

    node2 = GraphNode(
        label="regulation",
        name="High Value Transaction Policy",
        description="Regulatory boundaries for high cost transaction accounting.",
        skill_markdown=skill_high_value.strip(),
        properties=json.dumps({"limit": 500.0, "mfa_required": True}),
        clearance_level=2  # Employee/Admin only
    )

    skill_replenishment = """
# Skill: Automated Inventory Replenishment

## Purpose
Fulfills stock restocking parameters when product inventories fall below thresholds.

## Operation Rules
- Default restock amount is 50 units.
- Send Purchase Order notification to designated distributor.
"""

    node3 = GraphNode(
        label="workflow",
        name="Automated Inventory Replenishment",
        description="Fulfills product stock levels dynamically.",
        skill_markdown=skill_replenishment.strip(),
        properties=json.dumps({"reorder_count": 50}),
        clearance_level=1
    )
    
    session.add_all([node1, node2, node3])
    session.commit()

    # Connect nodes in the Graph
    edge1 = GraphEdge(source_id=node2.id, target_id=node1.id, edge_type="GOVERNS")
    edge2 = GraphEdge(source_id=node3.id, target_id=node1.id, edge_type="DEPENDS_ON")
    session.add_all([edge1, edge2])
    session.commit()

    # --- Seeding Vector Partitions directly mapped to Graph Nodes ---
    
    # Vector partitions linked to node 2 (High Value Transaction Policy)
    p1 = VectorPartition(
        node_id=node2.id,
        source_type="law",
        text_content="Corporate Compliance Act §4.2: Transactions exceeding $500 require visual audit trail and supervisor waiver validation.",
        embedding=json.dumps([0.9, 0.1, 0.05]),
        clearance_level=2
    )
    p2 = VectorPartition(
        node_id=node2.id,
        source_type="email",
        text_content="Email from CEO (2026-05-10): Re: Cashflow regulations. Keep the MFA limit strictly at $500. Do not lift this until audit is over.",
        embedding=json.dumps([0.85, 0.15, 0.08]),
        clearance_level=2
    )
    
    # Vector partitions linked to node 1 (Order Verification Workflow)
    p3 = VectorPartition(
        node_id=node1.id,
        source_type="internal_doc",
        text_content="Warehouse Logistics Manual: Ergonomic Chair shipments are restricted to maximum 5 units per customer during standard freight restrictions.",
        embedding=json.dumps([0.1, 0.9, 0.05]),
        clearance_level=1
    )
    p4 = VectorPartition(
        node_id=node1.id,
        source_type="email",
        text_content="Email from Logistics Manager: Re: Ergonomic chair backlogs. Make sure the order workflow blocks large bulk requests.",
        embedding=json.dumps([0.08, 0.88, 0.1]),
        clearance_level=1
    )

    session.add_all([p1, p2, p3, p4])
    session.commit()

    # --- Seeding Cryptographically Chained Audit Ledger ---
    print("Seeding Audit Ledger with Cryptographic SHA-256 chain...")
    genesis_details = json.dumps({"message": "Genesis Block of OmniGate ERP OS Ledger"})
    genesis_prev_hash = "0" * 64
    genesis_time = datetime(2026, 5, 20, 12, 0, 0)
    
    genesis_data = f"{genesis_time.isoformat()}|System Kernel|GENESIS|{genesis_details}|{genesis_prev_hash}"
    genesis_hash = hashlib.sha256(genesis_data.encode("utf-8")).hexdigest()
    
    g_block = AuditLedger(
        timestamp=genesis_time,
        agent_name="System Kernel",
        action_type="GENESIS",
        action_details=genesis_details,
        prev_hash=genesis_prev_hash,
        row_hash=genesis_hash
    )
    session.add(g_block)
    session.commit()
    
    rec1_time = genesis_time + timedelta(minutes=2)
    rec1_details = json.dumps({"action": "Seed relational tables and initial governance workflows"})
    rec1_data = f"{rec1_time.isoformat()}|System Seeder|DB_INITIALIZATION|{rec1_details}|{genesis_hash}"
    rec1_hash = hashlib.sha256(rec1_data.encode("utf-8")).hexdigest()
    
    row1 = AuditLedger(
        timestamp=rec1_time,
        agent_name="System Seeder",
        action_type="DB_INITIALIZATION",
        action_details=rec1_details,
        prev_hash=genesis_hash,
        row_hash=rec1_hash
    )
    session.add(row1)
    session.commit()

    print("Hybrid SQL + Graph + Mapped Vector database seeded successfully with clearance controls.")

if __name__ == "__main__":
    db_engine = init_db()
    seed_data(db_engine)
