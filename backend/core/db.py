import os
import json
import hashlib
import re
from datetime import datetime
from dotenv import load_dotenv
from sqlalchemy import create_engine, Column, Integer, String, Float, ForeignKey, DateTime, Text, text
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
from auth import current_user_role, current_user_email

# Determine paths
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
BACKEND_DIR = os.path.dirname(CURRENT_DIR)
DB_FILE_PATH = os.path.join(BACKEND_DIR, "erp_database.db")

Base = declarative_base()

# ==================== SQL TABLES DEFINITION ====================

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    role = Column(String(20), nullable=False)  # admin, employee, customer
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
    clearance_level = Column(Integer, default=1, nullable=False)  # 1: customer, 2: employee, 3: admin
    order_items = relationship("OrderItem", back_populates="product")

class Order(Base):
    __tablename__ = 'orders'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    total_amount = Column(Float, nullable=False)
    status = Column(String(20), nullable=False)  # pending, approved, shipped, delivered, flagged, cancelled
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

class GraphNode(Base):
    __tablename__ = 'graph_nodes'
    id = Column(Integer, primary_key=True)
    label = Column(String(50), nullable=False)  # workflow, regulation, agent
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    skill_markdown = Column(Text, nullable=True)
    properties = Column(Text, nullable=True)  # JSON encoded metadata
    clearance_level = Column(Integer, default=1, nullable=False)
    vector_partitions = relationship("VectorPartition", back_populates="node", cascade="all, delete-orphan")

class GraphEdge(Base):
    __tablename__ = 'graph_edges'
    id = Column(Integer, primary_key=True)
    source_id = Column(Integer, ForeignKey('graph_nodes.id'), nullable=False)
    target_id = Column(Integer, ForeignKey('graph_nodes.id'), nullable=False)
    edge_type = Column(String(50), nullable=False)  # GOVERNS, DEPENDS_ON
    properties = Column(Text, nullable=True)

class VectorPartition(Base):
    __tablename__ = 'vector_partitions'
    id = Column(Integer, primary_key=True)
    node_id = Column(Integer, ForeignKey('graph_nodes.id'), nullable=False)
    source_type = Column(String(50), nullable=False)  # law, email, internal_doc, policy
    text_content = Column(Text, nullable=False)
    embedding = Column(Text, nullable=False)  # JSON array of floats
    clearance_level = Column(Integer, default=1, nullable=False)
    node = relationship("GraphNode", back_populates="vector_partitions")

class AuditLedger(Base):
    __tablename__ = 'audit_ledger'
    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    agent_name = Column(String(100), nullable=False)
    action_type = Column(String(50), nullable=False)  # SCHEMA_EVOLUTION, TRANSACTION_MUTATION, etc.
    action_details = Column(Text, nullable=False)
    governing_node_id = Column(Integer, ForeignKey('graph_nodes.id'), nullable=True)
    prev_hash = Column(String(64), nullable=False)
    row_hash = Column(String(64), nullable=False)

class Task(Base):
    __tablename__ = 'tasks'
    task_id = Column(String(36), primary_key=True)
    status = Column(String(20), nullable=False)  # pending, processing, completed, failed
    query = Column(Text, nullable=False)
    role = Column(String(20), nullable=True)
    email = Column(String(100), nullable=True)
    result_json = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    finished_at = Column(DateTime, nullable=True)
class EvaluationRun(Base):
    __tablename__ = 'evaluation_runs'
    id = Column(Integer, primary_key=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    status = Column(String(20), default="running")  # running, completed, failed
    pass_count = Column(Integer, default=0)
    fail_count = Column(Integer, default=0)
    total_count = Column(Integer, default=0)

class EvaluationScenarioResult(Base):
    __tablename__ = 'evaluation_scenario_results'
    id = Column(Integer, primary_key=True)
    run_id = Column(Integer, ForeignKey('evaluation_runs.id', ondelete="CASCADE"), nullable=False)
    scenario_id = Column(String(50), nullable=False)
    name = Column(String(100), nullable=False)
    category = Column(String(50), nullable=False)
    query = Column(Text, nullable=False)
    role = Column(String(20), nullable=False)
    email = Column(String(100), nullable=False)
    task_id = Column(String(36), nullable=False)
    expected_status = Column(String(20), nullable=False)
    expected_contains = Column(Text, nullable=False)  # JSON string of expected output keywords
    predefined_pass = Column(Integer, default=0)  # 0: fail, 1: pass
    llm_pass = Column(Integer, default=0)  # 0: fail, 1: pass
    llm_score = Column(Integer, nullable=True)  # 1-5
    llm_feedback = Column(Text, nullable=True)
    human_pass = Column(Integer, nullable=True)  # 0: fail, 1: pass, None: unrated
    human_score = Column(Integer, nullable=True)  # 1-5
    human_feedback = Column(Text, nullable=True)
    status = Column(String(20), default="pending")  # pending, running, completed, failed


# ==================== DATABASE INITIALIZATION ====================

engine = create_engine(f"sqlite:///{DB_FILE_PATH}")
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ==================== DATABASE SECURITY (RBAC MIDDLEWARE) ====================

def secure_sql_query(query: str, role: str, email: str) -> str:
    """
    Appends dynamic security and visibility constraints to SQL SELECT queries
    depending on the current authenticated user's role and email context.
    """
    role_clearances = {
        "admin": 3,
        "employee": 2,
        "customer": 1
    }
    clearance = role_clearances.get(role, 0)
    
    # 1. Enforce Product clearance levels
    if "products" in query.lower() and role != "admin":
        alias_match = re.search(r"products\s+(?:as\s+)?(\w+)", query, re.IGNORECASE)
        alias = alias_match.group(1) if alias_match else "products"
        constraint = f"{alias}.clearance_level <= {clearance}"
        
        query = _append_where_constraint(query, constraint)

    # 2. Enforce Customer Order isolation (Customers can only query their own orders)
    if "orders" in query.lower() and role == "customer":
        alias_match = re.search(r"orders\s+(?:as\s+)?(\w+)", query, re.IGNORECASE)
        alias = alias_match.group(1) if alias_match else "orders"
        constraint = f"{alias}.user_id = (SELECT id FROM users WHERE email = '{email}')"
        
        query = _append_where_constraint(query, constraint)
        
    return query

def _append_where_constraint(query: str, constraint: str) -> str:
    """
    Helper to cleanly append a constraint to an existing WHERE clause or construct a new one.
    """
    # Find WHERE clause location
    where_match = re.search(r"\bWHERE\b", query, re.IGNORECASE)
    
    if where_match:
        # Append as and-clause before ORDER BY / GROUP BY if they exist
        order_match = re.search(r"\b(ORDER BY|GROUP BY|LIMIT)\b", query, re.IGNORECASE)
        if order_match:
            insert_idx = order_match.start()
            before = query[:insert_idx].rstrip()
            after = query[insert_idx:]
            return f"{before} AND {constraint} {after}"
        else:
            return f"{query.rstrip()} AND {constraint}"
    else:
        # Inject WHERE clause before ORDER BY / GROUP BY
        order_match = re.search(r"\b(ORDER BY|GROUP BY|LIMIT)\b", query, re.IGNORECASE)
        if order_match:
            insert_idx = order_match.start()
            before = query[:insert_idx].rstrip()
            after = query[insert_idx:]
            return f"{before} WHERE {constraint} {after}"
        else:
            return f"{query.rstrip()} WHERE {constraint}"

# ==================== LEDGER & AUDITING CONTROLS ====================

def log_audit_event(agent_name: str, action_type: str, action_details: str, governing_node_id: int = None) -> dict:
    try:
        timestamp = datetime.utcnow().replace(microsecond=0)
        db = SessionLocal()
        
        # Calculate prev_hash
        last_block = db.query(AuditLedger).order_by(AuditLedger.id.desc()).first()
        prev_hash = last_block.row_hash if last_block else "0" * 64
        
        # Build block string to hash
        ts_str = timestamp.isoformat()
        if " " in ts_str:
            ts_str = ts_str.replace(" ", "T")
        if "." in ts_str:
            ts_str = ts_str.split(".")[0]
            
        data_str = f"{ts_str}|{agent_name}|{action_type}|{action_details}|{prev_hash}"
        row_hash = hashlib.sha256(data_str.encode("utf-8")).hexdigest()
        
        new_block = AuditLedger(
            timestamp=timestamp,
            agent_name=agent_name,
            action_type=action_type,
            action_details=action_details,
            governing_node_id=governing_node_id,
            prev_hash=prev_hash,
            row_hash=row_hash
        )
        db.add(new_block)
        db.commit()
        db.close()
        return {"status": "success", "row_hash": row_hash}
    except Exception as e:
        print(f"Failed to log audit event: {e}")
        return {"error": str(e)}

def verify_ledger_integrity() -> list:
    tampered_indices = []
    try:
        db = SessionLocal()
        blocks = db.query(AuditLedger).order_by(AuditLedger.id.asc()).all()
        db.close()
        
        expected_prev_hash = "0" * 64
        for block in blocks:
            # Format timestamp string exactly as generated
            ts_str = str(block.timestamp)
            if " " in ts_str:
                ts_str = ts_str.replace(" ", "T")
            if "." in ts_str:
                ts_str = ts_str.split(".")[0]
                
            # Recompute hash
            data_str = f"{ts_str}|{block.agent_name}|{block.action_type}|{block.action_details}|{block.prev_hash}"
            computed_hash = hashlib.sha256(data_str.encode("utf-8")).hexdigest()
            
            # Verify chain links
            if block.prev_hash != expected_prev_hash:
                tampered_indices.append(block.id)
            # Verify payload hash
            elif block.row_hash != computed_hash:
                tampered_indices.append(block.id)
                
            expected_prev_hash = block.row_hash
    except Exception as e:
        print(f"Ledger verification error: {e}")
    return tampered_indices

# Automatically create evaluation tables if not present
Base.metadata.create_all(engine)

