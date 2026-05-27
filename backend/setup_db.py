import os
import json
import hashlib
from sqlalchemy import create_engine, Column, Integer, String, Float, ForeignKey, DateTime, Text, text
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
from datetime import datetime, timedelta
import random
import bcrypt

def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

Base = declarative_base()

# ==================== 1. SQL (TABULAR) LAYER ====================
class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    role = Column(String(20), nullable=False) 
    password_hash = Column(String(100), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    orders = relationship("Order", back_populates="user")

class Product(Base):
    __tablename__ = 'products'
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    category = Column(String(50), nullable=False)
    price = Column(Float, nullable=False)
    stock_quantity = Column(Integer, nullable=False)
    order_items = relationship("OrderItem", back_populates="product")

class Order(Base):
    __tablename__ = 'orders'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    total_amount = Column(Float, nullable=False)
    status = Column(String(20), nullable=False) 
    created_at = Column(DateTime, default=datetime.utcnow)
    user = relationship("User", back_populates="orders")
    items = relationship("OrderItem", back_populates="order")

class OrderItem(Base):
    __tablename__ = 'order_items'
    id = Column(Integer, primary_key=True)
    order_id = Column(Integer, ForeignKey('orders.id'), nullable=False)
    product_id = Column(Integer, ForeignKey('products.id'), nullable=False)
    quantity = Column(Integer, nullable=False)
    unit_price = Column(Float, nullable=False)
    order = relationship("Order", back_populates="items")
    product = relationship("Product", back_populates="order_items")


# ==================== 2. ALIVE GRAPH LAYER (WITH SKILL.MD) ====================
class GraphNode(Base):
    __tablename__ = 'graph_nodes'
    id = Column(Integer, primary_key=True)
    label = Column(String(50), nullable=False) # e.g., 'workflow', 'regulation'
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    skill_markdown = Column(Text, nullable=True) # The skill.md content
    properties = Column(Text, nullable=True) # JSON encoded metadata
    
    # Relationships
    vector_partitions = relationship("VectorPartition", back_populates="node", cascade="all, delete-orphan")

class GraphEdge(Base):
    __tablename__ = 'graph_edges'
    id = Column(Integer, primary_key=True)
    source_id = Column(Integer, ForeignKey('graph_nodes.id'), nullable=False)
    target_id = Column(Integer, ForeignKey('graph_nodes.id'), nullable=False)
    edge_type = Column(String(50), nullable=False) 
    properties = Column(Text, nullable=True) 


# ==================== 3. CONTEXTUAL VECTOR PARTITION LAYER ====================
class VectorPartition(Base):
    __tablename__ = 'vector_partitions'
    id = Column(Integer, primary_key=True)
    node_id = Column(Integer, ForeignKey('graph_nodes.id'), nullable=False)
    source_type = Column(String(50), nullable=False) # e.g., 'law', 'email', 'internal_doc'
    text_content = Column(Text, nullable=False)
    embedding = Column(Text, nullable=False) # JSON array of floats for cosine similarity
    
    node = relationship("GraphNode", back_populates="vector_partitions")


# ==================== 4. APPEND-ONLY AUDIT LEDGER LAYER ====================
class AuditLedger(Base):
    __tablename__ = 'audit_ledger'
    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    agent_name = Column(String(100), nullable=False)
    action_type = Column(String(50), nullable=False) # e.g., 'SCHEMA_EVOLUTION', 'TRANSACTION_MUTATION'
    action_details = Column(Text, nullable=False) # JSON-encoded parameters
    governing_node_id = Column(Integer, ForeignKey('graph_nodes.id'), nullable=True)
    prev_hash = Column(String(64), nullable=False)
    row_hash = Column(String(64), nullable=False)


# ==================== 5. BACKGROUND JOBS (TASKS) LAYER ====================
class Task(Base):
    __tablename__ = 'tasks'
    task_id = Column(String(36), primary_key=True)
    status = Column(String(20), nullable=False) # 'pending', 'processing', 'completed', 'failed'
    query = Column(Text, nullable=False)
    role = Column(String(20), nullable=True)
    email = Column(String(100), nullable=True)
    result_json = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    finished_at = Column(DateTime, nullable=True)



# ==================== INITIALIZATION & SEEDING ====================
def init_db(db_path="sqlite:///erp_database.db"):
    engine = create_engine(db_path)
    # Drop dynamic courier_shipments table if it exists
    with engine.connect() as conn:
        try:
            conn.execute(text("DROP TABLE IF EXISTS courier_shipments"))
            conn.commit()
        except Exception:
            pass
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

    # Clear external/fallback Neo4j and Qdrant graph and vector stores
    try:
        from middleware import ShieldGateway
        gateway = ShieldGateway()
        gateway.clear_graph_and_vector_stores()
    except Exception as e:
        print(f"Warning: Could not clear external graph and vector stores: {e}")



    # Seed Tabular SQL
    hashed_pwd = hash_password("password123")
    users = [
        User(name="Alice Smith", email="alice@example.com", role="admin", password_hash=hashed_pwd),
        User(name="Bob Jones", email="bob@example.com", role="employee", password_hash=hashed_pwd),
        User(name="Charlie Brown", email="charlie@example.com", role="customer", password_hash=hashed_pwd),
        User(name="Diana Prince", email="diana@example.com", role="customer", password_hash=hashed_pwd),
    ]
    session.add_all(users)
    
    products = [
        Product(name="Ergonomic Chair", category="Furniture", price=299.99, stock_quantity=50),
        Product(name="Standing Desk", category="Furniture", price=499.50, stock_quantity=30),
        Product(name="Laptop Stand", category="Accessories", price=45.00, stock_quantity=100),
        Product(name="Wireless Mouse", category="Electronics", price=29.99, stock_quantity=200),
        Product(name="Mechanical Keyboard", category="Electronics", price=120.00, stock_quantity=75),
    ]
    session.add_all(products)
    session.commit()

    # Create random orders
    customers = session.query(User).filter_by(role="customer").all()
    all_products = session.query(Product).all()
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
        properties=json.dumps({"version": "2.1.0", "active": True})
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
        properties=json.dumps({"limit": 500.0, "mfa_required": True})
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
        properties=json.dumps({"reorder_count": 50})
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
        embedding=json.dumps([0.9, 0.1, 0.05])
    )
    p2 = VectorPartition(
        node_id=node2.id,
        source_type="email",
        text_content="Email from CEO (2026-05-10): Re: Cashflow regulations. Keep the MFA limit strictly at $500. Do not lift this until audit is over.",
        embedding=json.dumps([0.85, 0.15, 0.08])
    )
    
    # Vector partitions linked to node 1 (Order Verification Workflow)
    p3 = VectorPartition(
        node_id=node1.id,
        source_type="internal_doc",
        text_content="Warehouse Logistics Manual: Ergonomic Chair shipments are restricted to maximum 5 units per customer during standard freight restrictions.",
        embedding=json.dumps([0.1, 0.9, 0.05])
    )
    p4 = VectorPartition(
        node_id=node1.id,
        source_type="email",
        text_content="Email from Logistics Manager: Re: Ergonomic chair backlogs. Make sure the order workflow blocks large bulk requests.",
        embedding=json.dumps([0.08, 0.88, 0.1])
    )

    session.add_all([p1, p2, p3, p4])
    session.commit()

    # --- Seeding Cryptographically Chained Audit Ledger ---
    print("Seeding Audit Ledger with Cryptographic SHA-256 chain...")
    genesis_details = json.dumps({"message": "Genesis Block of OmniGate ERP OS Ledger"})
    genesis_prev_hash = "0" * 64
    genesis_time = datetime(2026, 5, 20, 12, 0, 0)
    
    # Format: ISO_timestamp|agent_name|action_type|action_details|prev_hash
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
    
    # 2. Add DB Initialization Event
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

    print("Hybrid SQL + Graph (with skill.md) + Mapped Vector Partitions database seeded successfully.")

if __name__ == "__main__":
    db_engine = init_db()
    seed_data(db_engine)
