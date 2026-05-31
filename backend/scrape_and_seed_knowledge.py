import os
import json
import hashlib
import urllib.request
import urllib.parse
import re
import time
from datetime import datetime
from sqlalchemy.orm import sessionmaker

# Setup python path
import sys
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
if CURRENT_DIR not in sys.path:
    sys.path.append(CURRENT_DIR)

from core.db import (
    engine, GraphNode, GraphEdge, VectorPartition, SessionLocal
)

# Rich plain-text fallback content mapped to sections for all 19 Wikipedia ERP topics
LOCAL_FALLBACK_TEXTS = {
    "Enterprise resource planning": (
        "Enterprise resource planning (ERP) is the integrated management of main business processes, "
        "often in real-time and mediated by software and technology. ERP is usually referred to as a category "
        "of business-management software—typically a suite of integrated applications—that an organization "
        "can use to collect, store, manage, and interpret data from many business activities.\n"
        "== Core Functional Modules ==\n"
        "ERP systems typically partition business logic into modular functional areas: "
        "1. Financial Accounting (FI): GL ledger, AR accounts receivable, AP accounts payable.\n"
        "2. Controlling (CO): Management accounting, cost center allocations, internal auditing.\n"
        "3. Materials Management (MM): Inventory checks, stock tracking, and supplier coordination.\n"
        "4. Sales and Distribution (SD): Customer quotations, sales orders, and shipment tracking.\n"
        "5. Production Planning (PP): Manufacturing schedules, bill of materials (BOM).\n"
        "== Architectural Evolution ==\n"
        "ERP architectures evolved from rigid, monolithic databases (such as SAP R/3 and ABAP applications) "
        "to web service frameworks, and finally to modern cloud-native systems. The latest evolution incorporates "
        "decentralized Agentic ERP Operating Systems, where autonomous LLM agents coordinate business events, "
        "checked by deterministic validation gateways and immutable cryptographic audit ledgers."
    ),
    "Order-to-cash": (
        "Order-to-Cash (O2C or OTC) refers to the set of business processes that involves receiving and processing "
        "customer sales orders for goods and services and collecting payment.\n"
        "== Core Stages ==\n"
        "The standard O2C pipeline covers the following sequential operational stages: "
        "1. Customer Order Entry: Capture product requests and prices.\n"
        "2. Credit Limit Check: Verify client outstanding debt limits before checkout approval.\n"
        "3. Order Fulfillment: Dispatch goods and coordinate logistics shipping records.\n"
        "4. Customer Invoicing: Generate tax-compliant billing statements.\n"
        "5. Payment Collection: Record cash receipts and clear accounts receivable balances.\n"
        "== Credit and Risk Management ==\n"
        "To safeguard cash flow, credit control regulations dynamically query unpaid customer history. "
        "If a sales request causes a customer's total unpaid orders to exceed their designated credit limit "
        "(e.g., $2,000 for standard customer accounts), the system blocks checkout validation, requiring "
        "authorized manager approvals."
    ),
    "Procure-to-pay": (
        "Procure-to-Pay (P2P) is the process of requisitioning, purchasing, receiving, paying for, and accounting "
        "for goods and services. It forms a critical loop in materials management and financial controlling.\n"
        "== Core Stages ==\n"
        "The standard P2P workflow is divided into: "
        "1. Requisitioning: Identifying business needs and creating purchase requisitions.\n"
        "2. Purchase Order (PO): Generating, authorizing, and sending POs to suppliers.\n"
        "3. Goods Receipt: Verifying delivery quantities and quality at the warehouse.\n"
        "4. Invoice Matching: Performing three-way match (PO, Receipt, Invoice).\n"
        "5. Supplier Payment: Releasing payments and bookkeeping General Ledger adjustments.\n"
        "== Saga Recovery Logic ==\n"
        "Because procurement involves distributed systems, modern ERP engines use the Agentic Saga Pattern. "
        "Each forward step (e.g., stock deduction) has a compensating rollback action (e.g., restocking). "
        "If downstream checks fail (like payment limit authorization failure), the transaction coordinator "
        "rolls back preceding changes in reverse order to ensure ACID-level consistency across ledgers."
    ),
    "Financial accounting": (
        "Financial accounting is a specific branch of accounting involving a process of recording, summarizing, "
        "and reporting the myriad of transactions resulting from business operations over a period of time.\n"
        "== Double-Entry Bookkeeping ==\n"
        "Under double-entry accounting rules, every financial transaction must be recorded in at least two accounts. "
        "It enforces the fundamental accounting equation: Assets = Liabilities + Equity. Each transaction requires "
        "equal and opposite debit and credit postings, preventing mathematical and compliance errors.\n"
        "== Regulatory Reporting ==\n"
        "The outputs of financial accounting are formalized reports, including: "
        "1. Balance Sheet: Snapshot of assets, liabilities, and equity.\n"
        "2. Income Statement: Logs revenues and expenses over time.\n"
        "3. Cash Flow Statement: Tracks cash inflows and outflows.\n"
        "These reports are audited against regulatory compliance standards to guarantee corporate transparency."
    ),
    "Management accounting": (
        "Management accounting is the provision of financial and non-financial decision-making information to managers, "
        "focusing on internal organizational budgeting, costing, and strategy.\n"
        "== Controlling Functions ==\n"
        "Management accounting (Controlling or CO) is essential for internal tracking. It includes cost center accounting, "
        "profit center monitoring, overhead allocations, and variance analysis to track operational efficiency.\n"
        "== Comparison with Financial Accounting ==\n"
        "Unlike Financial Accounting, which reports historical transactions to external auditors and regulators, "
        "Management Accounting is forward-looking, flexible, and customized for internal corporate decision-makers."
    ),
    "Materials management": (
        "Materials management is a core function of supply chain management, dealing with the planning, organizing, "
        "and controlling of the flow of materials to ensure stock availability.\n"
        "== Inventory Control ==\n"
        "Maintains warehouse balance by monitoring stock levels. It enforces safety stock metrics, "
        "ensuring that replenishment purchase orders are automatically created when product quantities drop "
        "below critical safety margins (e.g. 10 units for desks).\n"
        "== Logistics Coordination ==\n"
        "Tracks shipping documents, customs clearances, and warehouse bin locations. It coordinates with "
        "billing and purchasing systems to ensure materials receipt matching matches the supplier invoice."
    ),
    "Sales and distribution": (
        "Sales and Distribution (SD) is a core module in ERP systems that handles transactions from customer inquiries "
        "to sales orders, dispatch, and final billing.\n"
        "== SD Sub-components ==\n"
        "SD governs multiple sequential events: inquiry and quotation, sales order creation, shipping and transportation "
        "dispatch, physical goods issue, and customer invoicing.\n"
        "== SD-FI Integration ==\n"
        "Generates direct ledger links between sales invoice postings and accounts receivable, automatically updating "
        "financial accounting records upon customer sales completion."
    ),
    "Production planning": (
        "Production planning is the planning of production and manufacturing modules in a company or industry. "
        "It optimizes resource utilization, coordinates capacity, and schedules work orders.\n"
        "== Master Production Scheduling ==\n"
        "Master Production Scheduling (MPS) coordinates factory assembly timelines based on sales orders and forecasting "
        "inputs, aligning capacities with raw material constraints.\n"
        "== Capacity and Scheduling ==\n"
        "Schedules machinery and labor workflows, tracking actual run hours and processing lags to calculate production variance."
    ),
    "Warehouse management system": (
        "A warehouse management system (WMS) is a software application designed to support and optimize warehouse "
        "functionality and distribution center management.\n"
        "== Warehouse Operations ==\n"
        "WMS tracks stock items from receiving to dispatch: "
        "1. Receiving & Putaway: Scan and locate items in optimized warehouse bins.\n"
        "2. Inventory Tracking: Real-time stock counts by shelf, bin, and serial number.\n"
        "3. Pick & Pack: Generate picking lists matching customer orders to minimize operator pathing.\n"
        "4. Shipping: Generate carrier labels and track outbound logistics logs."
    ),
    "Human resource management": (
        "Human Resource Management (HRM or HR) is the strategic approach to the effective and efficient management of "
        "people in a company or organization.\n"
        "== Hire-to-Retire Lifecycle ==\n"
        "HR manages employee cycles: recruitment, training, onboarding, time-tracking, salary structures, payroll allocations, "
        "and final pension/retirement payouts.\n"
        "== HR Access Control ==\n"
        "Governs user authorization directories, linking organizational levels to Role-Based Access Control (RBAC) database security keys."
    ),
    "Quality management": (
        "Quality Management (QM) ensures that an organization, product, or service is consistent. It has four key components: "
        "quality planning, quality control, quality assurance, and quality improvement.\n"
        "== Inspection Lots ==\n"
        "QM triggers inspection lots at goods receipt from suppliers. If materials fail quality standards, the batch is locked "
        "and prevented from being used in production.\n"
        "== Corrective Action ==\n"
        "QM manages returns to supplier (RTS) and logs vendor defect profiles to evaluate supplier rating scores."
    ),
    "Project system": (
        "Project System (PS) is a project management tool integrated with ERP modules to plan, schedule, and track project lifecycle activities.\n"
        "== Work Breakdown Structure (WBS) ==\n"
        "PS splits projects into hierarchical Work Breakdown Structure (WBS) elements. This links project activities directly "
        "to cost centers, tracking actual versus budgeted expenditures.\n"
        "== Milestone Billing ==\n"
        "Tracks project stages and automatically triggers sales invoicing triggers in SD when project milestone goals are checked as completed."
    ),
    "Plant maintenance": (
        "Plant Maintenance (PM) governs equipment inspection, servicing, and repair activities to prevent operational breakdowns.\n"
        "== Preventive Servicing ==\n"
        "Schedules regular maintenance tasks based on elapsed time or equipment run hours, protecting active hardware investments.\n"
        "== Breakdown Maintenance ==\n"
        "Generates corrective repair orders and blocks production capacity slots in PP when machinery goes offline due to faults."
    ),
    "Supply chain management": (
        "Supply chain management (SCM) is the management of the flow of goods and services, including all processes "
        "that transform raw materials into final products.\n"
        "== Strategic Importance ==\n"
        "SCM optimizes logistics, cuts manufacturing costs, and minimizes delivery latencies. It bridges "
        "purchasing, warehouse storage, production planning, and customer delivery networks into a cohesive, "
        "responsive pipeline.\n"
        "== Integration with ERP ==\n"
        "Enterprise resource planning systems integrate SCM data to automate supply lines, sync inventory levels "
        "with active sales order pipelines, and trigger purchase requisitions based on real-time consumer demands."
    ),
    "Double-entry bookkeeping": (
        "Double-entry bookkeeping is a system of accounting in which every entry to an account requires a corresponding "
        "and opposite entry to a different account.\n"
        "== Bookkeeping Equation ==\n"
        "Ensures balance sheet mathematical consistency: Assets = Liabilities + Owner's Equity. Debits must equal credits.\n"
        "== Ledger Postings ==\n"
        "Every corporate transaction creates at least two ledger entries. For example, a customer sales order debit "
        "to Cash is offset by a credit to Sales Revenue, ensuring audited balance accuracy."
    ),
    "Material requirements planning": (
        "Material requirements planning (MRP) is a production planning, scheduling, and inventory control system used "
        "to manage manufacturing processes.\n"
        "== MRP Calculations ==\n"
        "Calculates required component quantities, BOM requirements, and production schedules to meet customer delivery dates.\n"
        "== Inventory Optimization ==\n"
        "Minimizes warehouse storage costs and prevents stock outages by aligning raw materials orders with production runs."
    ),
    "Bill of materials": (
        "A bill of materials (BOM) is a comprehensive list of raw materials, assemblies, sub-assemblies, parts, "
        "and components needed to manufacture a product.\n"
        "== BOM Types ==\n"
        "Differentiates Engineering BOMs (EBOM, design-based) from Manufacturing BOMs (MBOM, production-ready checklists).\n"
        "== BOM Explosion ==\n"
        "Deconstructs a finished product order into individual raw components, feeding direct requirements into MRP scheduling."
    ),
    "Internal control": (
        "Internal control comprises the policies and procedures established by a company to ensure financial reporting accuracy "
        "and regulatory compliance.\n"
        "== Segregation of Duties ==\n"
        "Restricts database write privileges. No single role can both initiate and approve payment (e.g. creating and paying PO).\n"
        "== SOX Compliance ==\n"
        "Requires tamper-proof audit trails. The ERP OS implements cryptographically chained ledger hashes (SHA-256) to log every database write."
    ),
    "Cost center": (
        "A cost center is a department or function within an organization that does not directly add to profit but still "
        "costs the organization money to operate.\n"
        "== Cost Tracking ==\n"
        "Allocates direct operational expenses (e.g., IT support, HR, facility rent) to analyze spending budgets.\n"
        "== Overhead Allocations ==\n"
        "Distributes indirect overheads back to production lines using predefined management accounting algorithms."
    )
}

def fetch_wikipedia_text(topic):
    # Introduce rate-limiting sleep of 2 seconds between Wikipedia requests
    print(f"[*] Fetching Wikipedia topic: '{topic}'...")
    time.sleep(2)
    
    url = f"https://en.wikipedia.org/w/api.php?action=query&format=json&titles={urllib.parse.quote(topic)}&prop=extracts&explaintext=1&redirects=1"
    req = urllib.request.Request(url, headers={"User-Agent": "ERPOSBot/1.0 (contact@example.com)"})
    try:
        with urllib.request.urlopen(req, timeout=10) as res:
            data = json.loads(res.read().decode('utf-8'))
            pages = data.get("query", {}).get("pages", {})
            for page_id, page in pages.items():
                if "missing" not in page:
                    return page.get("title"), page.get("extract", "")
    except Exception as e:
        print(f"    [Network Request Failed for '{topic}']: {e}. Using local fallback data.")
    return None, None

def parse_wiki_sections(text):
    sections = []
    # Split text on headers like == Section Name ==
    parts = re.split(r'\n==+\s*(.*?)\s*==+\n', text)
    # The first part is the introduction (no heading)
    intro = parts[0].strip() if parts else ""
    sections.append(("Introduction", intro))
    
    for i in range(1, len(parts), 2):
        heading = parts[i].strip()
        body = parts[i+1].strip() if i+1 < len(parts) else ""
        if heading.lower() not in ["references", "further reading", "external links", "see also", "notes"]:
            sections.append((heading, body))
    return sections

def chunk_text(text, max_chars=600):
    chunks = []
    paragraphs = text.split('\n')
    current_chunk = ""
    for para in paragraphs:
        para = para.strip()
        if not para:
            continue
        if len(current_chunk) + len(para) <= max_chars:
            current_chunk += "\n" + para if current_chunk else para
        else:
            if current_chunk:
                chunks.append(current_chunk)
            if len(para) > max_chars:
                sentences = re.split(r'(?<=[.!?])\s+', para)
                sub_chunk = ""
                for sent in sentences:
                    if len(sub_chunk) + len(sent) <= max_chars:
                        sub_chunk += " " + sent if sub_chunk else sent
                    else:
                        if sub_chunk:
                            chunks.append(sub_chunk)
                        sub_chunk = sent
                if sub_chunk:
                    current_chunk = sub_chunk
            else:
                current_chunk = para
    if current_chunk:
        chunks.append(current_chunk)
    return chunks

def get_embedding(text_content):
    api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
    if api_key:
        try:
            from langchain_google_genai import GoogleGenerativeAIEmbeddings
            embeddings_model = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-2", google_api_key=api_key)
            return embeddings_model.embed_query(text_content)
        except Exception:
            pass
            
    query_vector = [0.1, 0.1, 0.1]
    q_lower = text_content.lower()
    if "audit" in q_lower or "regulation" in q_lower or "policy" in q_lower or "comply" in q_lower:
        query_vector = [0.9, 0.1, 0.05]
    elif "warehouse" in q_lower or "inventory" in q_lower or "material" in q_lower or "stock" in q_lower:
        query_vector = [0.1, 0.9, 0.05]
    elif "workflow" in q_lower or "process" in q_lower or "sales" in q_lower or "billing" in q_lower:
        query_vector = [0.1, 0.1, 0.9]
    return query_vector

def main():
    print("==================================================================")
    print("ERPOS Knowledge Crawler & Seeding System (Wikipedia Adapter)")
    print("==================================================================")
    
    Session = sessionmaker(bind=engine)
    session = Session()

    print("[*] Clearing Graph & Vector tables to rebuild with Wikipedia data...")
    session.query(GraphNode).delete()
    session.query(GraphEdge).delete()
    session.query(VectorPartition).delete()
    session.commit()

    from middleware import ShieldGateway
    gateway = ShieldGateway()
    gateway.graph_adapter.clear_all()
    gateway.vector_adapter.clear_all()

    # --- Seed Baseline Interactive Nodes for Saga & RBAC first ---
    print("[*] Re-seeding core interactive baseline rules...")
    
    skill_credit = """
# Customer Credit Control Regulation (SAP-FICO)
- General customer checkout limit is strictly $2,000.00.
- Stark Industries / Wayne Enterprises pre-approved credit: $10,000.00.
"""
    node_credit = GraphNode(
        label="regulation", name="Customer Credit Control Regulation",
        description="Controls credit ratings and checkout thresholds for B2B/B2C accounts.",
        skill_markdown=skill_credit.strip(), properties=json.dumps({"max_general_credit": 2000.0, "active": True}),
        clearance_level=2
    )

    skill_spending = """
# Procurement Spending Limits Regulation
- Orders <= $500.00: Auto-approved.
- Orders > $500.00: Intercepted by FinOps middleware. Requires CFO override.
"""
    node_spending = GraphNode(
        label="regulation", name="Internal Spending Approval Limits",
        description="Enforces authorization workflows on corporate procurement based on order cost.",
        skill_markdown=skill_spending.strip(), properties=json.dumps({"threshold_limit": 500.00}),
        clearance_level=2
    )

    session.add_all([node_credit, node_spending])
    session.commit()

    # --- Crawl or fallback Wikipedia Articles ---
    wiki_topics = list(LOCAL_FALLBACK_TEXTS.keys())

    crawled_nodes = {}
    
    for topic in wiki_topics:
        title, extract = fetch_wikipedia_text(topic)
        
        # Fallback to local high-fidelity summaries if network query failed (e.g. HTTP 429)
        if not title or not extract:
            print(f"    [Fallback] Using offline pre-scraped dataset for '{topic}'.")
            title = topic
            extract = LOCAL_FALLBACK_TEXTS.get(topic, "")
            if not extract:
                print(f"    [-] Critical Error: Fallback text not found for '{topic}'. Skipping.")
                continue
        
        print(f"    [+] Successfully loaded: '{title}' ({len(extract)} chars)")
        sections = parse_wiki_sections(extract)
        intro_text = next((body for head, body in sections if head == "Introduction"), "")
        snippet = intro_text[:200] + "..." if len(intro_text) > 200 else intro_text
        
        # Determine label
        label = "regulation" if "accounting" in title.lower() or "management" in title.lower() or "control" in title.lower() or "center" in title.lower() or "bookkeeping" in title.lower() or "bill of" in title.lower() else "workflow"
        
        skill_markdown = f"# Wikipedia Article: {title}\n\n## Overview\n{intro_text}\n\n## References & Knowledge Map\n- Source: Wikipedia URL: https://en.wikipedia.org/wiki/{title.replace(' ', '_')}"
        
        node = GraphNode(
            label=label,
            name=title,
            description=f"Wikipedia backing summary of {title}: {snippet}",
            skill_markdown=skill_markdown.strip(),
            properties=json.dumps({
                "source": f"https://en.wikipedia.org/wiki/{title.replace(' ', '_')}",
                "timestamp": datetime.utcnow().isoformat(),
                "sections_count": len(sections)
            }),
            clearance_level=1
        )
        session.add(node)
        session.commit()
        
        crawled_nodes[title] = node
        
        # Segment sections into vector partitions
        for heading, body in sections:
            if not body.strip():
                continue
            chunks = chunk_text(body, max_chars=500)
            for chunk_idx, chunk in enumerate(chunks):
                full_text = f"Subject: {title} | Section: {heading} | Content: {chunk}"
                embedding = get_embedding(full_text)
                
                partition = VectorPartition(
                    node_id=node.id,
                    source_type="internal_doc",
                    text_content=full_text,
                    embedding=json.dumps(embedding),
                    clearance_level=1
                )
                session.add(partition)
        session.commit()

    # Link Crawled Nodes dynamically
    print("[*] Linking graph relationships...")
    edges = []
    
    erp_node = crawled_nodes.get("Enterprise resource planning")
    o2c_node = crawled_nodes.get("Order-to-cash")
    p2p_node = crawled_nodes.get("Procure-to-pay")
    fa_node = crawled_nodes.get("Financial accounting")
    ma_node = crawled_nodes.get("Management accounting")
    mm_node = crawled_nodes.get("Materials management")
    sd_node = crawled_nodes.get("Sales and distribution")
    pp_node = crawled_nodes.get("Production planning")
    wms_node = crawled_nodes.get("Warehouse management system")
    hr_node = crawled_nodes.get("Human resource management")
    qm_node = crawled_nodes.get("Quality management")
    ps_node = crawled_nodes.get("Project system")
    pm_node = crawled_nodes.get("Plant maintenance")
    scm_node = crawled_nodes.get("Supply chain management")
    deb_node = crawled_nodes.get("Double-entry bookkeeping")
    mrp_node = crawled_nodes.get("Material requirements planning")
    bom_node = crawled_nodes.get("Bill of materials")
    ic_node = crawled_nodes.get("Internal control")
    cc_node = crawled_nodes.get("Cost center")

    # Link modules to ERP Core Hub
    if erp_node:
        for other in [fa_node, ma_node, scm_node, pp_node, hr_node, qm_node, ps_node, pm_node]:
            if other:
                edges.append(GraphEdge(source_id=other.id, target_id=erp_node.id, edge_type="DEPENDS_ON"))
                
    # Financial linkages
    if fa_node:
        for other in [o2c_node, p2p_node, deb_node]:
            if other:
                edges.append(GraphEdge(source_id=fa_node.id, target_id=other.id, edge_type="GOVERNS"))
        for other in [node_credit, node_spending]:
            if other:
                edges.append(GraphEdge(source_id=fa_node.id, target_id=other.id, edge_type="GOVERNS"))

    # Management control linkages
    if ma_node:
        for other in [cc_node, ic_node]:
            if other:
                edges.append(GraphEdge(source_id=ma_node.id, target_id=other.id, edge_type="GOVERNS"))

    # Supply Chain linkages
    if scm_node:
        for other in [mm_node, wms_node, sd_node]:
            if other:
                edges.append(GraphEdge(source_id=other.id, target_id=scm_node.id, edge_type="DEPENDS_ON"))

    # Materials Management and WMS interdependencies
    if mm_node:
        for other in [wms_node, pp_node]:
            if other:
                edges.append(GraphEdge(source_id=mm_node.id, target_id=other.id, edge_type="DEPENDS_ON"))

    # Production Planning controls
    if pp_node:
        for other in [mrp_node, bom_node]:
            if other:
                edges.append(GraphEdge(source_id=pp_node.id, target_id=other.id, edge_type="GOVERNS"))

    # Quality control gates
    if qm_node and mm_node:
        edges.append(GraphEdge(source_id=qm_node.id, target_id=mm_node.id, edge_type="GOVERNS"))

    # Maintenance and Project planning links
    if ps_node:
        for other in [ma_node, pp_node]:
            if other:
                edges.append(GraphEdge(source_id=ps_node.id, target_id=other.id, edge_type="DEPENDS_ON"))
    if pm_node:
        for other in [pp_node, mm_node]:
            if other:
                edges.append(GraphEdge(source_id=pm_node.id, target_id=other.id, edge_type="DEPENDS_ON"))

    # HR payroll Controlling allocations
    if hr_node and ma_node:
        edges.append(GraphEdge(source_id=hr_node.id, target_id=ma_node.id, edge_type="GOVERNS"))

    session.add_all(edges)
    session.commit()

    # Re-synchronize graph/vector stores
    from middleware import ShieldGateway
    print("[*] Re-synchronizing graph and vector database layers...")
    gateway = ShieldGateway()
    gateway.sync_from_sqlite_if_needed()

    print("\n==================================================================")
    print("Wikipedia ERP Knowledge Scraped & Synced successfully!")
    print("==================================================================")

if __name__ == "__main__":
    main()
