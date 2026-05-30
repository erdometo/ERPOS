import os
import json
import hashlib
from datetime import datetime, timedelta
import random
import bcrypt
from sqlalchemy import text
from sqlalchemy.orm import sessionmaker

# Set python path if needed to find core package
import sys
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
if CURRENT_DIR not in sys.path:
    sys.path.append(CURRENT_DIR)

from core.db import (
    engine, User, Product, Order, OrderItem, GraphNode, GraphEdge, 
    VectorPartition, AuditLedger, Task, Base
)

def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def seed_enterprise():
    print("==================================================================")
    # Reinitialize session
    Session = sessionmaker(bind=engine)
    session = Session()

    print("[*] Wiping old tables...")
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

    print("[*] Clearing external Graph and Vector databases...")
    try:
        from middleware import ShieldGateway
        gateway = ShieldGateway()
        gateway.clear_graph_and_vector_stores()
    except Exception as e:
        print(f"Warning: Could not clear external stores: {e}")

    # 1. Seed Users (Corporate Roles + Diverse Customers)
    print("[*] Seeding enterprise-grade users and employees...")
    hashed_pwd = hash_password("password123")
    
    users = [
        User(name="Alice Smith", email="alice@example.com", role="admin", password_hash=hashed_pwd),
        User(name="Bob Jones", email="bob@example.com", role="employee", password_hash=hashed_pwd),
        User(name="Dave Finance", email="finance@example.com", role="employee", password_hash=hashed_pwd),
        User(name="Sarah Logistics", email="logistics@example.com", role="employee", password_hash=hashed_pwd),
        
        # Customers (B2C & Large B2B accounts)
        User(name="Charlie Brown", email="charlie@example.com", role="customer", password_hash=hashed_pwd),
        User(name="Diana Prince", email="diana@example.com", role="customer", password_hash=hashed_pwd),
        User(name="Stark Industries", email="stark@example.com", role="customer", password_hash=hashed_pwd),
        User(name="Wayne Enterprises", email="wayne@example.com", role="customer", password_hash=hashed_pwd),
        User(name="Acme Corporation", email="acme@example.com", role="customer", password_hash=hashed_pwd),
        User(name="LexCorp Global", email="lex@example.com", role="customer", password_hash=hashed_pwd)
    ]
    session.add_all(users)
    session.commit()

    # 2. Seed Products (Varying Prices, Stocks, and Clearance Levels)
    print("[*] Seeding SAP-like product master data...")
    products = [
        # Public Furniture / Office Equipment (Clearance: 1)
        Product(name="Ergonomic Office Chair v2", category="Furniture", price=299.99, stock_quantity=150, clearance_level=1),
        Product(name="Standing Desk v3 (Dual Motor)", category="Furniture", price=499.50, stock_quantity=85, clearance_level=1),
        Product(name="4K Ultra-Wide Monitor", category="Electronics", price=649.99, stock_quantity=60, clearance_level=1),
        Product(name="Mechanical Keyboard (Quiet Edition)", category="Electronics", price=120.00, stock_quantity=120, clearance_level=1),
        Product(name="Wireless Mouse Pro", category="Electronics", price=59.99, stock_quantity=200, clearance_level=1),
        Product(name="USB-C Multi-Port Hub", category="Accessories", price=29.99, stock_quantity=300, clearance_level=1),
        Product(name="Aluminum Laptop Stand", category="Accessories", price=45.00, stock_quantity=150, clearance_level=1),
        
        # Internal / Restricted Components (Clearance: 2)
        Product(name="Quantum Processing Chipset v1", category="Hardware", price=1250.00, stock_quantity=20, clearance_level=2),
        Product(name="High-Performance AI Inference Node", category="Hardware", price=3500.00, stock_quantity=12, clearance_level=2),
        Product(name="Enterprise Rack Server (2U)", category="Infrastructure", price=5500.00, stock_quantity=8, clearance_level=2),
        
        # Restricted / High-Value Software Subscriptions (Clearance: 3)
        Product(name="ERP Platform Cloud Licence (Annual)", category="Software", price=15000.00, stock_quantity=99, clearance_level=3),
        Product(name="Autonomous Agent LLM API Tokens (100M)", category="Software", price=1200.00, stock_quantity=500, clearance_level=3)
    ]
    session.add_all(products)
    session.commit()

    # 3. Seed Graph Workflow Nodes (Credit checks, taxation, asset control)
    print("[*] Seeding Graph Governance workflow nodes...")
    
    skill_o2c = """
# SAP-like Order-to-Cash (O2C) Workflow

## Purpose
Validates customer sales orders, maps inventory reservations, checks client credit limits, applies taxation, and queues items for shipping log tasks.

## Steps
1. **Sales Order Ingestion**: Receive item request and verify pricing.
2. **Credit Limit Check**: Reference Credit Control Regulation to check customer clearance.
3. **Tax Assessment**: Calculate local tax / VAT details.
4. **Goods Issue**: Reserve inventory stock balance and log transaction.
"""

    node_o2c = GraphNode(
        label="workflow",
        name="Order-to-Cash (O2C) Pipeline",
        description="Standard customer order checkout and delivery dispatch process.",
        skill_markdown=skill_o2c.strip(),
        properties=json.dumps({"version": "3.0.0", "active": True}),
        clearance_level=1
    )

    skill_p2p = """
# SAP-like Procure-to-Pay (P2P) Saga Workflow

## Purpose
Governs corporate procurement. Triggers compensating rollbacks for stock/payments if compliance validations fail.

## Transaction Steps
1. **Deduct Stock (Inventory)**: Subtract item quantity from warehouse.
2. **Authorize Payment (Finance)**: Verify transaction total against $500 compliance threshold.
3. **Verify Compliance (Auditor)**: Check supplier records and country-specific tax rules.

## Compensating Routines (Rollback)
- **Step 1 Fail**: No compensation needed.
- **Step 2 Fail**: Reverse stock allocation (restock).
- **Step 3 Fail**: Void payment authorization + restock.
"""

    node_p2p = GraphNode(
        label="workflow",
        name="Procure-to-Pay (P2P) Saga Workflow",
        description="Transactional purchasing flow with Saga-based recovery triggers.",
        skill_markdown=skill_p2p.strip(),
        properties=json.dumps({"version": "1.2.0", "active": True}),
        clearance_level=1
    )

    skill_credit_regulation = """
# Credit Control Regulation (SAP-FICO)

## Purpose
Protects corporate accounts receivable by restricting client credit bounds.

## Rules
- Standard unpaid customer limit: $2,000.00.
- B2B account limits (Stark Industries / Wayne Enterprises): Pre-approved up to $10,000.00.
- Blocks new Sales Orders if current order total + outstanding debt exceeds limit.
"""

    node_credit = GraphNode(
        label="regulation",
        name="Customer Credit Control Regulation",
        description="Controls credit ratings and checkout thresholds for B2B/B2C accounts.",
        skill_markdown=skill_credit_regulation.strip(),
        properties=json.dumps({"max_general_credit": 2000.0, "net_30_active": True}),
        clearance_level=2
    )

    skill_spending_regulation = """
# Procurement Spending Limits Regulation

## Purpose
Restricts employee purchase requisition bounds.

## Approval Policy
- Orders <= $500.00: Auto-approved.
- Orders > $500.00: Intercepted by FinOps middleware. Requires CFO override or dual signatures.
"""

    node_spending = GraphNode(
        label="regulation",
        name="Internal Spending Approval Limits",
        description="Enforces authorization workflows on corporate procurement based on order cost.",
        skill_markdown=skill_spending_regulation.strip(),
        properties=json.dumps({"threshold_limit": 500.00}),
        clearance_level=2
    )

    skill_taxation = """
# Global Tax & VAT Compliance Policy

## Purpose
Applies dynamic local and international taxation models to invoice calculations.

## Standard Inclusions
- UK VAT rate: 20%.
- US Sales Tax: 8.25% (state-based variable).
- Rest of World: flat 10% import duties.
"""

    node_tax = GraphNode(
        label="regulation",
        name="Dynamic Sales Tax & VAT Compliance",
        description="Applies state-specific and country-specific tax rules to invoice creation.",
        skill_markdown=skill_taxation.strip(),
        properties=json.dumps({"uk_vat": 0.20, "us_sales_tax": 0.0825, "default_duty": 0.10}),
        clearance_level=1
    )

    skill_materials = """
# Materials Management & Reorder Limits (SAP-MM)

## Purpose
Triggers procurement flows when active stock drop below critical thresholds.

## Safety Stock Rates
- Furniture categories: Safety stock = 10 units. Reorder = 50 units.
- Hardware categories: Safety stock = 2 units. Reorder = 10 units.
"""

    node_materials = GraphNode(
        label="regulation",
        name="Materials Management & Reorder Thresholds",
        description="Establishes minimum inventory balances and reorder parameters.",
        skill_markdown=skill_materials.strip(),
        properties=json.dumps({"safety_stock_furniture": 10, "safety_stock_hardware": 2}),
        clearance_level=1
    )

    session.add_all([node_o2c, node_p2p, node_credit, node_spending, node_tax, node_materials])
    session.commit()

    # 4. Connect Graph Nodes (Edges)
    print("[*] Linking graph governance connections...")
    edges = [
        GraphEdge(source_id=node_credit.id, target_id=node_o2c.id, edge_type="GOVERNS"),
        GraphEdge(source_id=node_tax.id, target_id=node_o2c.id, edge_type="GOVERNS"),
        GraphEdge(source_id=node_tax.id, target_id=node_p2p.id, edge_type="GOVERNS"),
        GraphEdge(source_id=node_spending.id, target_id=node_p2p.id, edge_type="GOVERNS"),
        GraphEdge(source_id=node_materials.id, target_id=node_p2p.id, edge_type="DEPENDS_ON")
    ]
    session.add_all(edges)
    session.commit()

    # 5. Seed Vector Partitions (Audit texts, guidelines, CEO memos, emails)
    print("[*] Seeding Vector Database payload rules...")
    partitions = [
        # Tax Policy vector
        VectorPartition(
            node_id=node_tax.id,
            source_type="law",
            text_content="International Tax Regulation Act §102: Cross-border digital software purchases are subject to destination-based VAT compliance tracking.",
            embedding=json.dumps([0.1, 0.1, 0.9]),
            clearance_level=1
        ),
        
        # Credit Policy vectors
        VectorPartition(
            node_id=node_credit.id,
            source_type="internal_doc",
            text_content="Standard Credit Policy Document: Standard customer accounts are strictly capped at $2,000.00 in outstanding net-30 orders. Any extension requires Dave Finance approval.",
            embedding=json.dumps([0.9, 0.1, 0.05]),
            clearance_level=2
        ),
        VectorPartition(
            node_id=node_credit.id,
            source_type="email",
            text_content="Email from CFO (2026-05-18) Subject: Outstanding Accounts. Stark Industries is cleared for a custom B2B credit limit of $10,000.00 due to their ongoing contract.",
            embedding=json.dumps([0.88, 0.12, 0.04]),
            clearance_level=2
        ),
        VectorPartition(
            node_id=node_credit.id,
            source_type="email",
            text_content="Email from CEO Subject: Cashflow Safeguards. Tighten B2C checkouts. Ensure any user account that has had a prior transaction failure is immediately blocked from net credit terms.",
            embedding=json.dumps([0.92, 0.08, 0.06]),
            clearance_level=2
        ),
        
        # Spending Policy vectors
        VectorPartition(
            node_id=node_spending.id,
            source_type="policy",
            text_content="Corporate Spending Act §22: All purchasing requisitions exceeding $500.00 must require dual approvals (Purchasing Manager Bob Jones + CFO Dave Finance).",
            embedding=json.dumps([0.9, 0.05, 0.1]),
            clearance_level=2
        ),
        VectorPartition(
            node_id=node_spending.id,
            source_type="email",
            text_content="Email from CFO Dave Subject: Procurement Waivers. Do not approve standing desk orders that bypass the Saga workflow controls during this quarter's fiscal audit.",
            embedding=json.dumps([0.85, 0.07, 0.12]),
            clearance_level=2
        ),

        # Materials Policy vectors
        VectorPartition(
            node_id=node_materials.id,
            source_type="internal_doc",
            text_content="Warehouse Safety Operations: Maintain safety stock of 10 units for standing desks to cover supply line latency during customs processing.",
            embedding=json.dumps([0.1, 0.9, 0.05]),
            clearance_level=1
        ),
        VectorPartition(
            node_id=node_materials.id,
            source_type="email",
            text_content="Email from Sarah Logistics Subject: Standing Desk Backlogs. Reorder triggers should restock 50 units at a time to optimize container shipping rates.",
            embedding=json.dumps([0.08, 0.88, 0.1]),
            clearance_level=1
        )
    ]
    session.add_all(partitions)
    session.commit()

    # 6. Seed Operational Sales Orders (30+ diverse orders over the past month)
    print("[*] Generating mock Sales Orders history...")
    customers = session.query(User).filter_by(role="customer").all()
    all_products = session.query(Product).filter(Product.clearance_level <= 1).all()
    
    order_statuses = ["pending", "approved", "shipped", "delivered", "flagged", "cancelled"]
    
    for i in range(35):
        cust = random.choice(customers)
        status = random.choice(order_statuses)
        # Weight statuses for realistic distributions (more delivered/shipped, fewer flagged/cancelled)
        status = random.choices(order_statuses, weights=[15, 20, 25, 30, 5, 5])[0]
        
        days_ago = random.randint(1, 30)
        created_dt = datetime.utcnow() - timedelta(days=days_ago, hours=random.randint(0, 23))
        
        order = Order(
            user_id=cust.id,
            total_amount=0,
            status=status,
            created_at=created_dt
        )
        session.add(order)
        session.commit()
        
        # Choose 1 to 4 unique products for this order
        num_items = random.randint(1, 4)
        selected_prods = random.sample(all_products, num_items)
        
        total = 0.0
        for prod in selected_prods:
            qty = random.randint(1, 3)
            item = OrderItem(
                order_id=order.id,
                product_id=prod.id,
                quantity=qty,
                unit_price=prod.price
            )
            session.add(item)
            total += qty * prod.price
            
        order.total_amount = round(total, 2)
        session.commit()

    # 7. Seed Cryptographically Chained Audit Ledger
    print("[*] Seeding cryptographic audit ledger timeline...")
    genesis_details = json.dumps({"message": "Genesis Block of OmniGate ERP OS Ledger"})
    genesis_prev_hash = "0" * 64
    genesis_time = datetime(2026, 5, 1, 9, 0, 0)
    
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

    # Generate a series of chained ledger events mapping back to the past 30 days of operations
    current_hash = genesis_hash
    current_time = genesis_time
    
    ledger_actions = [
        ("System Seeder", "DB_INITIALIZATION", {"action": "Seed relational tables and initial governance workflows"}),
        ("Security Module", "RBAC_RECONCILIATION", {"action": "Verify database drivers and configure user security clearance tags"}),
        ("materials_agent", "RESTOCK_TRIGGER", {"product": "Ergonomic Office Chair v2", "refill": 50}),
        ("CFO Auditor Agent", "COMPLIANCE_REVIEW", {"action": "Audit net-30 credit control boundaries. Flagged Wayne Enterprises waiver expansion"}),
        ("Kernel Supervisor", "COMPLIANCE_SIGN", {"action": "Approved credit waiver for Stark Industries under rule Node #3"}),
        ("compliance_auditor", "LEDGER_INTEGRITY_CHECK", {"status": "verified", "compromised_rows": []}),
        ("dba_agent", "SCHEMA_EVOLUTION", {"ddl_query": "ALTER TABLE orders ADD COLUMN shipping_tracking_code TEXT"})
    ]

    for agent, action_type, details in ledger_actions:
        current_time += timedelta(days=3, hours=random.randint(1, 5))
        details_json = json.dumps(details)
        
        ts_str = current_time.isoformat()
        if " " in ts_str:
            ts_str = ts_str.replace(" ", "T")
        if "." in ts_str:
            ts_str = ts_str.split(".")[0]
            
        data_str = f"{ts_str}|{agent}|{action_type}|{details_json}|{current_hash}"
        new_hash = hashlib.sha256(data_str.encode("utf-8")).hexdigest()
        
        block = AuditLedger(
            timestamp=current_time,
            agent_name=agent,
            action_type=action_type,
            action_details=details_json,
            prev_hash=current_hash,
            row_hash=new_hash
        )
        session.add(block)
        session.commit()
        current_hash = new_hash

    # Sync graph nodes and vector partitions to the active adapters
    try:
        from middleware import ShieldGateway
        print("[*] Re-synchronizing graph and vector database layers...")
        gateway = ShieldGateway()
        gateway.sync_from_sqlite_if_needed()
    except Exception as e:
        print(f"Warning: Synchronization failed: {e}")

    print("\n==================================================================")
    print("Enterprise-grade SAP-like database seed completed successfully!")
    print("==================================================================")

if __name__ == "__main__":
    seed_enterprise()
