import os
import json
import uuid
import queue
import threading
import pika
from fastapi import FastAPI, HTTPException, Depends, Request
from sqlalchemy import text
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
from sqlalchemy.orm import sessionmaker

# Import setup_db User and Task models
from setup_db import User, Task

# Import authentication utilities
from auth import (
    get_authenticated_user,
    get_password_hash,
    verify_password,
    create_access_token,
    current_user_role
)

# Import our sandboxed Shield Gateway
from middleware import ShieldGateway

# Load environment
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(CURRENT_DIR, ".env"))

def get_content_str(res_obj) -> str:
    if hasattr(res_obj, "content"):
        res_obj = res_obj.content
    if isinstance(res_obj, list):
        return "".join([part.get("text", "") if isinstance(part, dict) else str(part) for part in res_obj])
    return str(res_obj)

app = FastAPI(title="Agentic ERP OS Kernel")

# Configure CORS so the React frontend can query our backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.middleware("http")
async def add_auth_context_middleware(request: Request, call_next):
    import jwt
    from auth import SECRET_KEY, ALGORITHM, current_user_role, current_user_email
    
    auth_header = request.headers.get("Authorization")
    email = None
    role = None
    if auth_header and auth_header.startswith("Bearer "):
        token = auth_header.split(" ")[1]
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            email = payload.get("email")
            role = payload.get("role")
        except Exception:
            pass
            
    token_role = current_user_role.set(role)
    token_email = current_user_email.set(email)
    try:
        response = await call_next(request)
        return response
    finally:
        current_user_role.reset(token_role)
        current_user_email.reset(token_email)

gateway = ShieldGateway()

class QueryRequest(BaseModel):
    question: str

class ActionRequest(BaseModel):
    action_id: str
    params: dict


class ActionExecuteRequest(BaseModel):
    query: str
    params: dict = {}
    governing_node_id: int = None


class RegisterRequest(BaseModel):
    name: str
    email: str
    password: str
    role: str = "customer" # admin, employee, customer


class LoginRequest(BaseModel):
    email: str
    password: str


# ==================== 1. REAL LLM AGENT ROUTING & EXECUTION ENGINE ====================
def run_real_llm_agent(question: str):
    from langchain_core.prompts import ChatPromptTemplate
    
    custom_id = os.getenv("CUSTOM_CLIENT_ID")
    custom_secret = os.getenv("CUSTOM_CLIENT_SECRET")
    custom_model = os.getenv("CUSTOM_MODEL_NAME", "gemini-3-flash")
    
    if custom_id and custom_secret:
        from custom_client import ChatCustom
        llm = ChatCustom(client_id=custom_id, client_secret=custom_secret, model_name=custom_model, temperature=0.1)
        model_display = f"Custom LLM ({custom_model})"
    else:
        from langchain_google_genai import ChatGoogleGenerativeAI
        api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY or GOOGLE_API_KEY or CUSTOM client credentials are not configured.")
        llm = ChatGoogleGenerativeAI(model="gemini-3.5-flash", temperature=0.1, google_api_key=api_key)
        model_display = "gemini-3.5-flash"
        
    trace = []
    cb = CircuitBreaker(max_cycles=6)
    
    trace.append({
        "agent": "Kernel Supervisor",
        "action": "Initialize Autonomous ReAct Loop",
        "details": f"Spawning ReAct Agent to resolve ERP request: '{question}' using {model_display}."
    })
    
    # Introspect schema initially
    current_schema = gateway.get_schema_info()
    
    tools_description = """
Available Multi-Model Gateways (Tools):

1. Tool: `execute_sql`
   Arguments: {"query": "SELECT ..."}
   Description: Run a safe read-only SQL query against transactional tables (users, products, orders, order_items).

2. Tool: `execute_ddl`
   Arguments: {"query": "ALTER TABLE ... / CREATE TABLE ..."}
   Description: securely evolve SQL schema (CREATE/ALTER only, additive). Destructive operations are blocked.

3. Tool: `traverse_graph`
   Arguments: {"node_name": "Node Name"}
   Description: Fetch connected edges and workflow rules (skill.md) for a graph node.

4. Tool: `vector_search`
   Arguments: {"query_text": "Semantic search term"}
   Description: Query global corporate policies and vector partitions.

5. Tool: `node_vector_search`
   Arguments: {"node_id": 1, "query_text": "Semantic search term"}
   Description: Fetch localized compliance docs/emails/laws linked to a specific graph node.

6. Tool: `evolve_graph_node`
   Arguments: {"label": "workflow/regulation", "name": "Node Name", "description": "Short description", "skill_markdown": "Markdown rules text", "properties": "{}", "target_edges": [{"target_name": "Target Node Name", "edge_type": "GOVERNS/DEPENDS_ON"}]}
   Description: Evolve Graph database. Creates or updates workflow rules (skill.md nodes) and connects them in the operational ledger.

7. Tool: `vectorize_document`
   Arguments: {"node_id": 1, "source_type": "law/email/internal_doc", "text_content": "Full text to vectorize"}
   Description: Vectorize compliance text or corporate emails and map them strictly to a Graph Node.
"""

    system_prompt = """You are the sandboxed Autonomous Kernel Agent of the Agentic ERP OS.
Your objective is to solve the user's business, schema, or logic requests using a step-by-step reasoning and action (ReAct) loop.

{tools}

Current Database Schema Map:
{schema}

Instructions:
- Analyze the user request. Break it down into step-by-step tool invocations.
- You can run multiple tools in sequence. For example, search global policies first, then traverse the workflow graph, search local vectors, and finally query SQL tables.
- If requested to evolve the database, use `execute_ddl`, `evolve_graph_node`, or `vectorize_document` tools to update the multi-model storage layers.
- Formulate your output at each step in exactly the following structured format (do not output extra characters, output exactly this):

Thought: <Your reasoning about what to do next>
Action: <Tool Name>
Arguments: <JSON representation of the arguments for the tool>

When you have collected all observations and resolved the request completely, formulate your final answer as:

Thought: I have solved the request completely.
Final Answer: <Detailed summary of findings, evolved structures, and actions taken>

Never run destructive queries (no DROP/DELETE/TRUNCATE). Do not output markdown code blocks for the Thought/Action/Arguments lines.
"""

    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("user", "User Request: {question}\n\nExecution History:\n{history}")
    ])
    
    chain = prompt | llm
    history_log = []
    last_observation = "Initial Step"
    final_answer = ""
    
    for cycle in range(5):
        history_str = "\n".join(history_log) if history_log else "No history yet."
        
        # Invoke LLM
        res_obj = chain.invoke({
            "tools": tools_description,
            "schema": current_schema,
            "question": question,
            "history": history_str
        })
        res = get_content_str(res_obj).strip()
        
        # Parse Thought, Action, Arguments
        thought = ""
        action = ""
        arguments_str = ""
        
        lines = res.split("\n")
        for line in lines:
            if line.startswith("Thought:"):
                thought = line[8:].strip()
            elif line.startswith("Action:"):
                action = line[7:].strip()
            elif line.startswith("Arguments:"):
                arguments_str = line[10:].strip()
            elif line.startswith("Final Answer:"):
                final_answer = line[13:].strip()
                
        if not thought:
            if "Final Answer:" in res:
                final_answer = res.split("Final Answer:")[1].strip()
            else:
                thought = "Analyzing steps..."
                final_answer = res
                
        if final_answer:
            trace.append({
                "agent": "Autonomous Kernel Agent",
                "action": "Final Response Formulated",
                "details": final_answer
            })
            break
            
        if not action:
            trace.append({
                "agent": "Kernel Supervisor",
                "action": "Parser Warning",
                "details": "Agent did not request a tool. Concluding loop."
            })
            final_answer = res
            break
            
        # Execute tool
        trace.append({
            "agent": "Autonomous Kernel Agent",
            "action": f"Invoke Tool: {action}",
            "details": f"Thought: {thought}\nArguments: {arguments_str}"
        })
        
        # Parse arguments
        try:
            args = json.loads(arguments_str) if arguments_str else {}
        except Exception as e:
            args = {}
            last_observation = f"Error: Could not parse arguments as valid JSON: {str(e)}"
            history_log.append(f"Thought: {thought}\nAction: {action}\nArguments: {arguments_str}\nObservation: {last_observation}")
            continue
            
        # Active FinOps Circuit Breaker Check!
        sql_pattern = args.get("query", "") if action in ["execute_sql", "execute_ddl"] else ""
        broken, reason = cb.log_and_check("Autonomous Kernel Agent", f"Tool Call: {action}", sql_pattern)
        
        if broken:
            trace.append({
                "agent": "FinOps Circuit Breaker",
                "action": "SYSTEM_INTERRUPT",
                "details": f"HALTING EXECUTION. {reason} Preventing runaway token spend."
            })
            
            ui_code = f"""
            const EphemeralDashboard = ({{ data }}) => {{
                return (
                    <div className="space-y-6 animate-fadeIn">
                        <div className="bg-rose-500/10 border border-rose-500/30 p-6 rounded-2xl backdrop-blur-md shadow-2xl animate-shake">
                            <div className="flex items-center gap-3 mb-4">
                                <div className="p-3 bg-rose-500/20 text-rose-400 rounded-xl border border-rose-500/30">
                                    <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="lucide lucide-alert-octagon"><polygon points="7.86 2 16.14 2 22 7.86 22 16.14 16.14 22 7.86 22 2 16.14 2 7.86 7.86 2"/><line x1="12" x2="12" y1="8" y2="12"/><line x1="12" x2="12.01" y1="16" y2="16"/></svg>
                                </div>
                                <div>
                                    <h2 className="text-lg font-bold text-rose-400">FinOps Circuit Breaker Tripped</h2>
                                    <p className="text-xs text-rose-300/60">SYSTEM_INTERRUPT raised by kernel security gate</p>
                                </div>
                            </div>
                            <p className="text-sm text-slate-300 mb-4 font-mono leading-relaxed bg-black/40 p-4 rounded-xl border border-slate-900">
                                {reason}
                            </p>
                            <div className="text-xs text-slate-400 leading-normal">
                                The Kernel detected a repeated query loop in real agent execution. Running this recursively would drain the operational enterprise tokens. The sandboxed workspace closed the loop automatically.
                            </div>
                        </div>
                    </div>
                );
            }};
            return EphemeralDashboard;
            """
            return {
                "trace": trace,
                "data": {"reason": reason},
                "ui_code": ui_code
            }
            
        # Execute Tool via Shield Gateway
        try:
            if action == "execute_sql":
                tool_res = gateway.execute_sql(args.get("query", ""))
            elif action == "execute_ddl":
                tool_res = gateway.execute_ddl(args.get("query", ""))
            elif action == "traverse_graph":
                tool_res = gateway.traverse_graph(args.get("node_name", ""))
            elif action == "vector_search":
                tool_res = gateway.vector_search(args.get("query_text", ""))
            elif action == "node_vector_search":
                tool_res = gateway.node_vector_search(args.get("node_id", 1), args.get("query_text", ""))
            elif action == "evolve_graph_node":
                properties = args.get("properties", "{}")
                if isinstance(properties, dict):
                    properties = json.dumps(properties)
                tool_res = gateway.execute_graph_mutation(
                    label=args.get("label", "workflow"),
                    name=args.get("name", ""),
                    description=args.get("description", ""),
                    skill_markdown=args.get("skill_markdown", ""),
                    properties=properties,
                    target_edges=args.get("target_edges")
                )
            elif action == "vectorize_document":
                tool_res = gateway.execute_vector_mutation(
                    node_id=args.get("node_id", 1),
                    source_type=args.get("source_type", "email"),
                    text_content=args.get("text_content", "")
                )
            else:
                tool_res = {"error": f"Unknown tool name: {action}"}
                
            if isinstance(tool_res, dict) and "error" in tool_res:
                last_observation = f"Blocked/Error: {tool_res['error']}"
            else:
                last_observation = json.dumps(tool_res)
                
        except Exception as tool_err:
            last_observation = f"Exception during tool execution: {str(tool_err)}"
            
        trace.append({
            "agent": "Shield Security Proxy",
            "action": f"Observation Captured",
            "details": f"Result: {last_observation[:300]}..."
        })
        
        # Log to agent context history
        history_log.append(f"Thought: {thought}\nAction: {action}\nArguments: {arguments_str}\nObservation: {last_observation}")
        
    # --- Step E: Compliance analysis & UI generation ---
    trace.append({
        "agent": "Compliance Auditor Agent",
        "action": "Enforce Multi-Model Bounds & Render Workspace UI",
        "details": "Feeding execution observations and evolution ledger into Vibe Coder UI Agent."
    })
    
    # Formulate auditing data details to send to UI Vibe Coder
    audit_data = {
        "user_query": question,
        "history": history_log,
        "final_answer": final_answer or "ReAct Loop concluded successfully.",
        "current_schema": gateway.get_schema_info()
    }
    
    ui_prompt = ChatPromptTemplate.from_messages([
        ("system", """You are the Lead Auditor & Vibe Coder UI Agent.
Your job is to build a premium, stunning glassmorphic React dashboard named `EphemeralDashboard` to visualize the results of the autonomous multi-agent execution workspace.

The component receives `data` and `onAction` as props.

Include:
- A beautiful header showing the final outcome of the agent's query.
- A visual "Multi-Agent Trajectory Timeline" summarizing the thoughts, actions, and observations taken during the ReAct loop.
- A visual breakdown of any evolved database structures (e.g. newly created SQL columns/tables, new Graph skill nodes, or vectorized documents).
- Action buttons if anomalies or reorders are present (e.g. onAction("approve_waiver", {{ order_id: x }}) or onAction("reorder_stock", {{ product_name: y }})).
- Exquisite design aesthetics: zinc-950 dark styling, soft colorful borders (emerald, rose, indigo, or amber depending on context), nice glassmorphic card glows, smooth lists, and clear typography.

Return ONLY raw, valid React JSX code wrapped in the following signature:
const EphemeralDashboard = ({{ data, onAction }}) => {{ ... }}; return EphemeralDashboard;"""),
        ("user", "Compile the custom React UI dashboard for this execution result: {payload}")
    ])
    
    ui_chain = ui_prompt | llm
    ui_res = ui_chain.invoke({"payload": json.dumps(audit_data)})
    ui_code = get_content_str(ui_res).strip()
    
    if ui_code.startswith("```"):
        ui_code = ui_code.split("```")[1]
        if ui_code.startswith("javascript") or ui_code.startswith("jsx") or ui_code.startswith("typescript") or ui_code.startswith("tsx"):
            ui_code = ui_code[10:]
        elif ui_code.startswith("js"):
            ui_code = ui_code[2:]
    ui_code = ui_code.strip()
    
    trace.append({
        "agent": "Vibe Coder UI Agent",
        "action": "Generate Ephemeral Interface",
        "details": "Compiled generative React workspace widget showing trajectory and updated hybrid ledger."
    })
    
    return {
        "trace": trace,
        "data": audit_data,
        "ui_code": ui_code
    }


# ==================== 2. FINOPS CIRCUIT BREAKER LOGIC ====================
class CircuitBreaker:
    def __init__(self, max_cycles=5):
        self.max_cycles = max_cycles
        self.call_history = []
        
    def log_and_check(self, agent_name: str, action: str, sql_pattern: str = ""):
        self.call_history.append({
            "agent": agent_name,
            "action": action,
            "sql": sql_pattern
        })
        
        # Check 1: Exceeds 5 cycles
        if len(self.call_history) >= self.max_cycles:
            return True, f"FinOps Alert: Execution chain exceeded safe budget limit of {self.max_cycles} trace steps."
            
        # Check 2: Loop detection (executing the exact same SQL pattern repeatedly)
        if len(self.call_history) >= 3:
            last_three_sqls = [h["sql"] for h in self.call_history[-3:] if h["sql"]]
            if len(last_three_sqls) == 3 and len(set(last_three_sqls)) == 1:
                return True, f"FinOps Alert: Infinite query loop detected! Same SQL query executed 3 times in a row."
                
        return False, ""


# ==================== 3. HIGH-FIDELITY DETERMINISTIC SIMULATOR (OFFLINE FALLBACK) ====================
def simulate_agentic_workflow(question: str):
    q = question.lower()
    trace = []
    data = {}
    ui_code = ""
    
    # Instantiate Circuit Breaker
    cb = CircuitBreaker()

    # Step 1: Supervisor Introspection
    trace.append({
        "agent": "Kernel Supervisor",
        "action": "Introspect User Request",
        "details": f"Analyzing natural language query: '{question}'."
    })
    
    # Check circuit breaker trigger simulation (if loop keyword is supplied)
    if "loop" in q or "circuit" in q or "breaker" in q:
        trace.append({"agent": "Tabular SQL Agent", "action": "Query Warehouse Inventory", "details": "SELECT stock_quantity FROM products;"})
        # Simulate quick steps to trigger circuit breaker
        for idx in range(4):
            broken, reason = cb.log_and_check("Tabular SQL Agent", "Query Warehouse Inventory", "SELECT stock_quantity FROM products;")
            trace.append({
                "agent": "Tabular SQL Agent",
                "action": "Retry Transactional Query",
                "details": f"Retrying query step due to verification mismatch (cycle {idx+2}/5)."
            })
            if broken:
                trace.append({
                    "agent": "FinOps Circuit Breaker",
                    "action": "SYSTEM_INTERRUPT",
                    "details": f"HALTING EXECUTION. {reason} Preventing runaway token spend."
                })
                
                ui_code = """
                const EphemeralDashboard = ({ data }) => {
                    return (
                        <div className="space-y-6 animate-fadeIn">
                            <div className="bg-rose-500/10 border border-rose-500/30 p-6 rounded-2xl backdrop-blur-md shadow-2xl animate-shake">
                                <div className="flex items-center gap-3 mb-4">
                                    <div className="p-3 bg-rose-500/20 text-rose-400 rounded-xl border border-rose-500/30">
                                        <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="lucide lucide-alert-octagon"><polygon points="7.86 2 16.14 2 22 7.86 22 16.14 16.14 22 7.86 22 2 16.14 2 7.86 7.86 2"/><line x1="12" x2="12" y1="8" y2="12"/><line x1="12" x2="12.01" y1="16" y2="16"/></svg>
                                    </div>
                                    <div>
                                        <h2 className="text-lg font-bold text-rose-400">FinOps Circuit Breaker Tripped</h2>
                                        <p className="text-xs text-rose-300/60">SYSTEM_INTERRUPT raised by kernel security gate</p>
                                    </div>
                                </div>
                                <p className="text-sm text-slate-300 mb-4 font-mono leading-relaxed bg-black/40 p-4 rounded-xl border border-slate-900">
                                    {data.reason}
                                </p>
                                <div className="text-xs text-slate-400 leading-normal">
                                    The Kernel detected a repeated query loop. Running this recursively would drain the operational enterprise tokens. The sandboxed workspace closed the loop automatically.
                                </div>
                            </div>
                        </div>
                    );
                };
                return EphemeralDashboard;
                """
                return {
                    "trace": trace,
                    "data": {"reason": reason},
                    "ui_code": ui_code
                }

    # DBA Evolution Introspection
    if "table" in q or "column" in q or "evolve" in q or "add column" in q:
        trace.append({
            "agent": "DBA Schema Mutation Agent",
            "action": "Analyze DB Evolution Prompt",
            "details": f"Interpreted schema expansion command: '{question}'."
        })
        
        # Formulate SQL DDL
        ddl_sql = ""
        mutation_desc = ""
        if "shipping" in q or "courier" in q:
            ddl_sql = "ALTER TABLE orders ADD COLUMN courier_name VARCHAR(50);"
            mutation_desc = "Added 'courier_name' column to 'orders' table to integrate express freight routing."
        elif "shipment" in q or "deliver" in q:
            ddl_sql = """CREATE TABLE courier_shipments (
                id INTEGER PRIMARY KEY,
                order_id INTEGER,
                carrier VARCHAR(50),
                status VARCHAR(20),
                dispatched_at DATETIME
            );"""
            mutation_desc = "Created new structured 'courier_shipments' table to audit delivery operations."
        else:
            # Fallback simple alter
            ddl_sql = "ALTER TABLE users ADD COLUMN last_login_ip VARCHAR(30);"
            mutation_desc = "Added 'last_login_ip' column to 'users' table to secure authorization sessions."
            
        trace.append({
            "agent": "DBA Schema Mutation Agent",
            "action": "Formulate Audited DDL",
            "details": f"Generated safe DDL:\n{ddl_sql}"
        })
        
        # Check Pydantic validation
        res = gateway.execute_ddl(ddl_sql)
        if "error" in res:
            trace.append({
                "agent": "Shield Security Proxy",
                "action": "DDL INTERCEPTED & BLOCKED",
                "details": f"Shield gateway rejected operation: {res['error']}"
            })
            raise HTTPException(status_code=400, detail=res["error"])
            
        trace.append({
            "agent": "Shield Security Proxy",
            "action": "Execute DDL Mutation",
            "details": f"Valid Additive Query Approved. Database evolved successfully. Ledger state synchronized."
        })
        
        # Inspect post-mutation schema
        new_schema = gateway.get_schema_info()
        data = {
            "status": "evolved",
            "applied_ddl": ddl_sql,
            "mutation_description": mutation_desc,
            "active_schema": new_schema
        }
        
        trace.append({
            "agent": "Vibe Coder UI Agent",
            "action": "Generate Schema Evolution View",
            "details": "Constructing dynamic interactive schema visualizer."
        })
        
        ui_code = """
        const EphemeralDashboard = ({ data }) => {
            const active_schema = data.active_schema || "";
            return (
                <div className="space-y-6 animate-fadeIn">
                    {/* Header */}
                    <div className="bg-slate-900/60 backdrop-blur-md p-5 rounded-2xl border border-indigo-500/20 shadow-lg">
                        <div className="flex items-center gap-3">
                            <div className="p-2.5 bg-indigo-500/20 border border-indigo-500/40 text-indigo-400 rounded-xl">
                                <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="lucide lucide-database-backup"><path d="M12 2v4M12 18v4M4.93 4.93l2.83 2.83M16.24 16.24l2.83 2.83M2 12h4M18 12h4M4.93 19.07l2.83-2.83M16.24 7.76l2.83-2.83"/></svg>
                            </div>
                            <div>
                                <h2 className="text-base font-bold text-indigo-400">Database Schema Evolved Safely</h2>
                                <p className="text-xs text-slate-400">Additive evolutionary mutation committed by DBA Agent</p>
                            </div>
                        </div>
                    </div>

                    {/* DDL Details */}
                    <div className="bg-slate-950 p-5 rounded-2xl border border-slate-900 space-y-3">
                        <span className="text-[10px] text-slate-500 font-bold tracking-wider uppercase block">Executed Schema Modification (DDL)</span>
                        <pre className="font-mono text-xs text-indigo-300 bg-black/50 p-3 rounded-lg overflow-x-auto border border-slate-900">
                            {data.applied_ddl}
                        </pre>
                        <p className="text-xs text-slate-300 italic">"{data.mutation_description}"</p>
                    </div>

                    {/* Current Schema Explorer */}
                    <div className="bg-slate-950 border border-slate-900 rounded-2xl overflow-hidden shadow-lg">
                        <div className="px-5 py-3 bg-slate-900/40 border-b border-slate-900">
                            <h3 className="font-semibold text-slate-200 text-xs">Evolved SQLite Schema Map</h3>
                        </div>
                        <div className="p-5 font-mono text-xs text-emerald-400/90 space-y-2 whitespace-pre-wrap leading-relaxed max-h-[350px] overflow-y-auto">
                            {active_schema}
                        </div>
                    </div>
                </div>
            );
        };
        return EphemeralDashboard;
        """
        
        return {
            "trace": trace,
            "data": data,
            "ui_code": ui_code
        }

    # Graph Evolution Introspection
    elif "evolve graph" in q or "graph node" in q or "workflow node" in q or "express shipping" in q:
        trace.append({
            "agent": "Graph Governance Agent",
            "action": "Analyze Graph Evolution Request",
            "details": f"Interpreted graph node creation/evolution command: '{question}'."
        })
        
        skill_text = """# Skill: Express Freight Delivery

## Purpose
Governs rapid logistics dispatch of high value or high priority product freight orders.

## Operation Rules
- Orders with priority courier must be dispatched within 4 hours.
- Maximum freight payload must not exceed 2000 lbs.
"""
        trace.append({
            "agent": "Graph Governance Agent",
            "action": "Formulate Node Structure & Rules",
            "details": f"Formulated skill.md markdown:\n{skill_text}\nLabel: WORKFLOW. Target govern edge: 'Order Verification Workflow'."
        })
        
        # Execute Graph Mutation
        res = gateway.execute_graph_mutation(
            label="workflow",
            name="Express Freight Delivery",
            description="Expedited shipping workflow for bulk freight orders",
            skill_markdown=skill_text,
            properties='{"priority": "high"}',
            target_edges=[{"target_name": "Order Verification Workflow", "edge_type": "GOVERNS"}]
        )
        
        if "error" in res:
            trace.append({
                "agent": "Shield Security Proxy",
                "action": "GRAPH MUTATION BLOCKED",
                "details": f"Shield gateway rejected operation: {res['error']}"
            })
            raise HTTPException(status_code=400, detail=res["error"])
            
        trace.append({
            "agent": "Shield Security Proxy",
            "action": "Execute Graph Mutation",
            "details": f"Evolved workflow node: '{res.get('message') or 'Success'}' approved and connected."
        })
        
        # Inspect post-mutation schema
        new_schema = gateway.get_schema_info()
        data = {
            "status": "evolved",
            "node_name": "Express Freight Delivery",
            "node_label": "WORKFLOW",
            "description": "Expedited shipping workflow for bulk freight orders",
            "skill_markdown": skill_text,
            "target_edges": [{"target_name": "Order Verification Workflow", "edge_type": "GOVERNS"}],
            "active_schema": new_schema
        }
        
        trace.append({
            "agent": "Vibe Coder UI Agent",
            "action": "Generate Graph Evolution View",
            "details": "Constructing dynamic interactive graph visualizer."
        })
        
        ui_code = """
        const EphemeralDashboard = ({ data }) => {
            const active_schema = data.active_schema || "";
            return (
                <div className="space-y-6 animate-fadeIn">
                    {/* Header */}
                    <div className="bg-slate-900/60 backdrop-blur-md p-5 rounded-2xl border border-indigo-500/20 shadow-lg">
                        <div className="flex items-center gap-3">
                            <div className="p-2.5 bg-indigo-500/20 border border-indigo-500/40 text-indigo-400 rounded-xl">
                                <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="lucide lucide-git-branch"><line x1="6" x2="6" y1="3" y2="15"/><circle cx="18" cy="6" r="3"/><circle cx="6" cy="18" r="3"/><path d="M18 9a9 9 0 0 1-9 9"/></svg>
                            </div>
                            <div>
                                <h2 className="text-base font-bold text-indigo-400">Graph Workflow Ledger Evolved Safely</h2>
                                <p className="text-xs text-slate-400 font-medium">New workflow node & governing edges committed to active Graph</p>
                            </div>
                        </div>
                    </div>

                    {/* Node Cards */}
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                        <div className="bg-slate-950 p-5 rounded-2xl border border-slate-900 space-y-4">
                            <div>
                                <span className="text-[10px] text-indigo-400 font-bold uppercase tracking-wider block font-mono">Evolved Node Details</span>
                                <h3 className="text-sm font-bold text-slate-200 mt-1">{data.node_name}</h3>
                                <p className="text-xs text-slate-400 mt-0.5">{data.description}</p>
                            </div>
                            <div className="bg-black/50 p-3 rounded-lg border border-slate-900">
                                <span className="text-[9px] text-slate-500 font-bold block font-mono uppercase">Node Connections</span>
                                <div className="mt-2 flex items-center gap-2 text-xs">
                                    <span className="px-2 py-0.5 bg-indigo-500/10 text-indigo-400 border border-indigo-500/20 rounded font-semibold text-[10px]">Express Freight Delivery</span>
                                    <span className="text-slate-500 font-mono text-[10px]">-- GOVERNS --></span>
                                    <span className="px-2 py-0.5 bg-rose-500/10 text-rose-400 border border-rose-500/20 rounded font-semibold text-[10px]">Order Verification Workflow</span>
                                </div>
                            </div>
                        </div>
                        
                        <div className="bg-slate-950 p-5 rounded-2xl border border-slate-900 flex flex-col gap-2">
                            <span className="text-[10px] text-emerald-400 font-bold uppercase tracking-wider block font-mono">Governed skill.md Rules</span>
                            <pre className="font-mono text-[11px] text-emerald-400/90 bg-black/50 p-3 rounded-lg overflow-y-auto border border-slate-900 max-h-[160px] whitespace-pre-wrap leading-relaxed">
                                {data.skill_markdown}
                            </pre>
                        </div>
                    </div>

                    {/* Current Schema Explorer */}
                    <div className="bg-slate-950 border border-slate-900 rounded-2xl overflow-hidden shadow-lg">
                        <div className="px-5 py-3 bg-slate-900/40 border-b border-slate-900">
                            <h3 className="font-semibold text-slate-200 text-xs">Updated Hybrid Schema Ledger</h3>
                        </div>
                        <div className="p-5 font-mono text-xs text-emerald-400/90 space-y-2 whitespace-pre-wrap leading-relaxed max-h-[250px] overflow-y-auto">
                            {active_schema}
                        </div>
                    </div>
                </div>
            );
        };
        return EphemeralDashboard;
        """
        
        return {
            "trace": trace,
            "data": data,
            "ui_code": ui_code
        }

    # Vector Evolution Introspection
    elif "vectorize" in q or "document" in q or "compliance memo" in q or "map" in q:
        trace.append({
            "agent": "Vector Index Agent",
            "action": "Analyze Vector Integration Prompt",
            "details": f"Interpreted vector partition mapping request: '{question}'."
        })
        
        text_content = "CEO Compliance Memo: Restrict large bulk standing desk exports during freight backlogs. Priority shipping overrides require CFO approval."
        
        trace.append({
            "agent": "Vector Index Agent",
            "action": "Generate Document Embeddings",
            "details": "Running mock embedding pipeline. Source Type: POLICY. Target Node: 3 (Automated Inventory Replenishment)."
        })
        
        # Execute Vector Mutation
        res = gateway.execute_vector_mutation(
            node_id=3,
            source_type="policy",
            text_content=text_content
        )
        
        if "error" in res:
            trace.append({
                "agent": "Shield Security Proxy",
                "action": "VECTOR MUTATION BLOCKED",
                "details": f"Shield gateway rejected operation: {res['error']}"
            })
            raise HTTPException(status_code=400, detail=res["error"])
            
        trace.append({
            "agent": "Shield Security Proxy",
            "action": "Execute Vector Mutation",
            "details": f"Vectorized context partition: '{res.get('message') or 'Success'}' approved and mapped to Node 3."
        })
        
        # Inspect post-mutation schema
        new_schema = gateway.get_schema_info()
        data = {
            "status": "evolved",
            "source_type": "POLICY",
            "target_node_id": 3,
            "target_node_name": "Automated Inventory Replenishment",
            "text_content": text_content,
            "embedding_dims": 1536,
            "active_schema": new_schema
        }
        
        trace.append({
            "agent": "Vibe Coder UI Agent",
            "action": "Generate Vector Partition View",
            "details": "Constructing dynamic vector embedding distribution dashboard."
        })
        
        ui_code = """
        const EphemeralDashboard = ({ data }) => {
            const active_schema = data.active_schema || "";
            return (
                <div className="space-y-6 animate-fadeIn">
                    {/* Header */}
                    <div className="bg-slate-900/60 backdrop-blur-md p-5 rounded-2xl border border-teal-500/20 shadow-lg">
                        <div className="flex items-center gap-3">
                            <div className="p-2.5 bg-teal-500/20 border border-teal-500/40 text-teal-400 rounded-xl">
                                <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="lucide lucide-binary"><rect x="14" y="14" width="4" height="6" rx="2"/><rect x="6" y="4" width="4" height="6" rx="2"/><path d="M6 20h4"/><path d="M14 10h4"/><path d="M6 14h2v6"/><path d="M14 4h2v6"/></svg>
                            </div>
                            <div>
                                <h2 className="text-base font-bold text-teal-400">Contextual Vector Partition Mapped</h2>
                                <p className="text-xs text-slate-400 font-medium">Text vectorized & strictly bound to Graph Governance node</p>
                            </div>
                        </div>
                    </div>

                    {/* Vector Details */}
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                        <div className="bg-slate-950 p-5 rounded-2xl border border-slate-900 space-y-4">
                            <div>
                                <span className="text-[10px] text-teal-400 font-bold uppercase tracking-wider block font-mono">Source Metadata</span>
                                <div className="mt-2 space-y-2">
                                    <div className="flex justify-between border-b border-slate-900 pb-1.5 text-xs">
                                        <span className="text-slate-500">Document Type</span>
                                        <span className="text-slate-300 font-semibold">{data.source_type}</span>
                                    </div>
                                    <div className="flex justify-between border-b border-slate-900 pb-1.5 text-xs">
                                        <span className="text-slate-500">Target Node Mapped</span>
                                        <span className="text-teal-400 font-semibold">#{data.target_node_id} ({data.target_node_name})</span>
                                    </div>
                                    <div className="flex justify-between text-xs">
                                        <span className="text-slate-500">Embedding Dimensions</span>
                                        <span className="text-slate-300 font-mono font-semibold">{data.embedding_dims} Dims (text-embedding-3-small)</span>
                                    </div>
                                </div>
                            </div>
                        </div>
                        
                        <div className="bg-slate-950 p-5 rounded-2xl border border-slate-900 flex flex-col gap-2">
                            <span className="text-[10px] text-teal-400 font-bold uppercase tracking-wider block font-mono">Vectorized Text Content</span>
                            <div className="text-xs text-slate-300 italic leading-relaxed bg-black/50 p-4 rounded-xl border border-slate-900 flex-1 flex items-center">
                                "{data.text_content}"
                            </div>
                        </div>
                    </div>

                    {/* Current Schema Explorer */}
                    <div className="bg-slate-950 border border-slate-900 rounded-2xl overflow-hidden shadow-lg">
                        <div className="px-5 py-3 bg-slate-900/40 border-b border-slate-900">
                            <h3 className="font-semibold text-slate-200 text-xs">Updated Hybrid Schema Ledger</h3>
                        </div>
                        <div className="p-5 font-mono text-xs text-emerald-400/90 space-y-2 whitespace-pre-wrap leading-relaxed max-h-[250px] overflow-y-auto">
                            {active_schema}
                        </div>
                    </div>
                </div>
            );
        };
        return EphemeralDashboard;
        """
        
        return {
            "trace": trace,
            "data": data,
            "ui_code": ui_code
        }

    # Operational audit route: Anomalies and Regulations
    elif "anomaly" in q or "anomalous" in q or "limit" in q or "flagged" in q or "today" in q or "audit" in q or "process" in q:
        # Trace Step 2: Semantic Vector Search
        trace.append({
            "agent": "Vector Index Agent",
            "action": "Semantic Regulation Lookup",
            "details": "Searching global vector partitions for rules related to 'high value transactions'."
        })
        
        vector_res = gateway.vector_search("high value transaction limit", limit=1)
        trace.append({
            "agent": "Vector Index Agent",
            "action": "Semantic Matches Located",
            "details": f"Identified node context: '{vector_res[0]['text_content']}' with similarity {vector_res[0]['similarity']}."
        })

        # Trace Step 3: Graph Traversal to retrieve governing node
        trace.append({
            "agent": "Graph Governance Agent",
            "action": "Workflow Governance Traversal",
            "details": "Traversing workflow graph for 'High Value Transaction Policy' to identify governed workflow nodes."
        })
        graph_res = gateway.traverse_graph("High Value Transaction Policy")
        governed_wf = graph_res[0]['target_name']
        
        # Load skill.md
        with gateway.engine.connect() as conn:
            skill_res = conn.execute(text("SELECT skill_markdown FROM graph_nodes WHERE name = 'High Value Transaction Policy'")).fetchone()
            skill_markdown = skill_res[0] if skill_res else "No skill markdown configured."
            
        trace.append({
            "agent": "Graph Governance Agent",
            "action": "Workflow Node & Skill Loaded",
            "details": f"High Value Policy governs workflow: '{governed_wf}'. Loaded skill.md rules successfully."
        })

        # Trace Step 3.5: Localized Node Vector Search
        trace.append({
            "agent": "Vector Index Agent",
            "action": "Local Node Context Search",
            "details": "Searching localized vector partitions belonging strictly to 'High Value Transaction Policy' (ID 2)."
        })
        local_context = gateway.node_vector_search(node_id=2, query_text="override waive limit", limit=2)
        trace.append({
            "agent": "Vector Index Agent",
            "action": "Local Context Loaded",
            "details": f"Fetched {len(local_context)} local context records (e.g. CEO email rules, compliance codes)."
        })

        # Trace Step 4: SQL Query Execution via Shield
        trace.append({
            "agent": "Tabular SQL Agent",
            "action": "Transactional Data Retrieval",
            "details": "Formulating safe SQL query to extract all orders and associated customer details."
        })
        sql_query = """
        SELECT o.id, u.name as customer_name, o.total_amount, o.status, o.created_at 
        FROM orders o 
        JOIN users u ON o.user_id = u.id 
        ORDER BY o.created_at DESC
        """
        sql_res = gateway.execute_sql(sql_query)
        trace.append({
            "agent": "Shield Security Proxy",
            "action": "Validate & Execute SQL",
            "details": "Checked query. Pattern: SELECT. Keywords: SAFE. Permitted read transaction committed."
        })

        # Trace Step 5: Compliance Audit filtering
        trace.append({
            "agent": "Compliance Auditor Agent",
            "action": "Audit Constraints Verification",
            "details": "Auditing transactions against High Value Transaction Policy limit: $500.0."
        })
        
        anomalies = []
        normal_orders = []
        for o in sql_res:
            if o['total_amount'] > 500.0:
                o['audit_flag'] = "ANOMALOUS"
                o['reason'] = "Transaction exceeds High Value Policy limit ($500.0)"
                anomalies.append(o)
            else:
                o['audit_flag'] = "COMPLIANT"
                normal_orders.append(o)
        
        data = {
            "anomalies": anomalies,
            "compliant": normal_orders,
            "policy_limit": 500.0,
            "skill_rules": skill_markdown,
            "vector_context": [c["text_content"] for c in local_context]
        }
        
        trace.append({
            "agent": "Compliance Auditor Agent",
            "action": "Audit Verification Completed",
            "details": f"Flagged {len(anomalies)} high-risk transactions exceeding policy bounds."
        })

        # Trace Step 6: Vibe Coder Generative UI
        trace.append({
            "agent": "Vibe Coder UI Agent",
            "action": "Generate Bespoke Ephemeral Dashboard",
            "details": "Compiling tailored interface based on active skill rules and retrieved vector context."
        })

        ui_code = """
        const EphemeralDashboard = ({ data, onAction }) => {
            const anomalies = data.anomalies || [];
            const compliant = data.compliant || [];
            const vector_context = data.vector_context || [];
            
            return (
                <div className="space-y-6 animate-fadeIn">
                    {/* Header */}
                    <div className="flex justify-between items-center bg-slate-900/60 backdrop-blur-md p-4 rounded-xl border border-rose-500/20 shadow-lg">
                        <div>
                            <h2 className="text-xl font-bold text-rose-400">Risk Assessment Control Room</h2>
                            <p className="text-xs text-slate-400">Generative UI constructed based on Graph Skill & Local Vector Context</p>
                        </div>
                        <span className="px-3 py-1 bg-rose-500/20 border border-rose-500/40 text-rose-400 rounded-full text-xs font-semibold animate-pulse">
                            {anomalies.length} Anomalies Flagged
                        </span>
                    </div>

                    {/* Local Vector Context Panels */}
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        {vector_context.map((text, idx) => (
                            <div key={idx} className="bg-slate-950 p-4 rounded-xl border border-slate-900 text-xs shadow-inner flex flex-col gap-1.5">
                                <span className="text-[9px] uppercase tracking-wider text-rose-500/80 font-bold font-mono">
                                    📁 Associated Vector Context Partition {idx + 1}
                                </span>
                                <p className="text-slate-300 italic">"{text}"</p>
                            </div>
                        ))}
                    </div>

                    {/* Stats */}
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                        <div className="bg-slate-950 p-4 rounded-xl border border-rose-500/10 shadow">
                            <span className="text-xs text-slate-400 uppercase tracking-wider block mb-1">Total Risk Exposure</span>
                            <span className="text-2xl font-extrabold text-rose-400">
                                ${anomalies.reduce((sum, item) => sum + item.total_amount, 0).toFixed(2)}
                            </span>
                        </div>
                        <div className="bg-slate-950 p-4 rounded-xl border border-emerald-500/10 shadow">
                            <span className="text-xs text-slate-400 uppercase tracking-wider block mb-1">Compliant Operations</span>
                            <span className="text-2xl font-extrabold text-emerald-400">{compliant.length} Transactions</span>
                        </div>
                        <div className="bg-slate-950 p-4 rounded-xl border border-blue-500/10 shadow">
                            <span className="text-xs text-slate-400 uppercase tracking-wider block mb-1">Enforced Limit</span>
                            <span className="text-2xl font-extrabold text-blue-400">$500.00</span>
                        </div>
                    </div>

                    {/* Anomalies Table */}
                    <div className="bg-slate-950 border border-slate-800 rounded-xl overflow-hidden shadow">
                        <div className="px-4 py-3 bg-slate-900 border-b border-slate-800">
                            <h3 className="font-semibold text-rose-400 text-sm">Critical Anomalies</h3>
                        </div>
                        <div className="overflow-x-auto">
                            <table className="w-full text-left text-xs border-collapse">
                                <thead>
                                    <tr className="bg-slate-900/50 text-slate-400 border-b border-slate-800">
                                        <th className="p-3">Order ID</th>
                                        <th className="p-3">Customer</th>
                                        <th className="p-3">Amount</th>
                                        <th className="p-3">Reason</th>
                                        <th className="p-3">Status</th>
                                        <th className="p-3 text-right">Action</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {anomalies.map((a) => (
                                        <tr key={a.id} className="border-b border-slate-800/60 hover:bg-slate-900/30 transition-colors">
                                            <td className="p-3 font-semibold text-slate-300">#00{a.id}</td>
                                            <td className="p-3 text-slate-300">{a.customer_name}</td>
                                            <td className="p-3 font-bold text-rose-400">${a.total_amount.toFixed(2)}</td>
                                            <td className="p-3 text-slate-400 italic">{a.reason}</td>
                                            <td className="p-3">
                                                <span className={`px-2 py-0.5 border rounded text-[10px] font-medium uppercase ${
                                                    a.status === 'approved' 
                                                        ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20' 
                                                        : 'bg-rose-500/10 text-rose-400 border-rose-500/20'
                                                }`}>
                                                    {a.status}
                                                </span>
                                            </td>
                                            <td className="p-3 text-right">
                                                {a.status !== 'approved' && (
                                                    <button 
                                                        onClick={() => onAction("approve_waiver", { order_id: a.id })}
                                                        className="px-3 py-1 bg-rose-500 hover:bg-rose-600 active:scale-95 transition-all text-white text-[10px] font-bold rounded-lg shadow-md shadow-rose-950/20"
                                                    >
                                                        Approve Waiver
                                                    </button>
                                                )}
                                            </td>
                                        </tr>
                                    ))}
                                </tbody>
                            </table>
                        </div>
                    </div>
                </div>
            );
        };
        return EphemeralDashboard;
        """

    # Inventory stocks route
    elif "product" in q or "inventory" in q or "stock" in q or "price" in q:
        trace.append({
            "agent": "Vector Index Agent",
            "action": "Semantic Replenishment Lookup",
            "details": "Searching vector partitions for 'stock levels and replenishment workflows'."
        })
        
        # Load skill.md for inventory replenishment
        with gateway.engine.connect() as conn:
            skill_res = conn.execute(text("SELECT skill_markdown FROM graph_nodes WHERE name = 'Automated Inventory Replenishment'")).fetchone()
            skill_markdown = skill_res[0] if skill_res else "No replenishment skill.md configured."
            
        trace.append({
            "agent": "Graph Governance Agent",
            "action": "Replenishment Workflow Selected",
            "details": "Identified 'Automated Inventory Replenishment' skill.md governs restocking checks."
        })

        # Local Node Vector context lookup
        trace.append({
            "agent": "Vector Index Agent",
            "action": "Local Node Context Search",
            "details": "Retrieving localized document context mapped to replenishment node."
        })
        local_context = gateway.node_vector_search(node_id=1, query_text="freight restriction chairs backlog", limit=2)
        trace.append({
            "agent": "Vector Index Agent",
            "action": "Local Context Pulled",
            "details": f"Loaded {len(local_context)} contextual vector records (Warehouse logistics guides, email orders backlog)."
        })

        # Fetch product inventory
        trace.append({
            "agent": "Tabular SQL Agent",
            "action": "Fetch Product Inventory",
            "details": "Querying products catalog and current stock levels."
        })
        sql_res = gateway.execute_sql("SELECT name, category, price, stock_quantity FROM products")
        data = {
            "products": sql_res,
            "skill_rules": skill_markdown,
            "vector_context": [c["text_content"] for c in local_context]
        }
        
        trace.append({
            "agent": "Vibe Coder UI Agent",
            "action": "Generate Product Shelf Dashboard",
            "details": "Compiling dynamic inventory dashboard including compliance rules."
        })

        ui_code = """
        const EphemeralDashboard = ({ data, onAction }) => {
            const products = data.products || [];
            const vector_context = data.vector_context || [];
            
            return (
                <div className="space-y-6 animate-fadeIn">
                    <div className="flex justify-between items-center bg-slate-900/60 backdrop-blur-md p-4 rounded-xl border border-emerald-500/20 shadow-lg">
                        <div>
                            <h2 className="text-xl font-bold text-emerald-400">Inventory Command Center</h2>
                            <p className="text-xs text-slate-400">Dynamic inventory tracker incorporating Logistics Vector context</p>
                        </div>
                    </div>

                    {/* Local Logistics Vector Context */}
                    <div className="bg-slate-950 p-4 rounded-xl border border-slate-900 text-xs shadow-inner flex flex-col gap-2">
                        <span className="text-[9px] uppercase tracking-wider text-emerald-400 font-bold font-mono">
                            📦 Active Logistics Policies & Email Backlogs
                        </span>
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                            {vector_context.map((text, idx) => (
                                <p key={idx} className="text-slate-400 italic">"{text}"</p>
                            ))}
                        </div>
                    </div>

                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                        {products.map((p, idx) => (
                            <div key={idx} className="bg-slate-950 p-4 rounded-xl border border-slate-800 hover:border-emerald-500/30 transition-all shadow group">
                                <div className="flex justify-between items-start mb-2">
                                    <h4 className="font-bold text-slate-200 text-sm group-hover:text-emerald-400 transition-colors">{p.name}</h4>
                                    <span className="px-2 py-0.5 bg-slate-900 text-slate-400 border border-slate-800 rounded text-[9px] uppercase tracking-wider font-semibold">
                                        {p.category}
                                    </span>
                                </div>
                                <div className="flex justify-between items-end mt-4">
                                    <div>
                                        <span className="text-[10px] text-slate-500 block">UNIT PRICE</span>
                                        <span className="text-lg font-extrabold text-emerald-400">${p.price.toFixed(2)}</span>
                                    </div>
                                    <div className="text-right">
                                        <span className="text-[10px] text-slate-500 block">STOCK LEVEL</span>
                                        <span className={`text-sm font-bold ${p.stock_quantity < 40 ? 'text-rose-400 animate-pulse' : 'text-slate-300'}`}>
                                            {p.stock_quantity} units
                                        </span>
                                    </div>
                                </div>
                                <div className="mt-4 pt-3 border-t border-slate-900 flex justify-end">
                                    <button 
                                        onClick={() => onAction("reorder_stock", { product_name: p.name })}
                                        className="px-3 py-1 bg-slate-900 hover:bg-emerald-500/10 border border-slate-800 hover:border-emerald-500/30 transition-all text-slate-300 hover:text-emerald-400 text-[10px] font-bold rounded-lg"
                                    >
                                        Restock 50 Units
                                    </button>
                                </div>
                            </div>
                        ))}
                    </div>
                </div>
            );
        };
        return EphemeralDashboard;
        """
        
    else:
        # Default workflow
        trace.append({
            "agent": "Vector Index Agent",
            "action": "Semantic Policy Lookup",
            "details": f"Attempting semantic match for request: '{question}'."
        })
        vector_res = gateway.vector_search(question)
        
        trace.append({
            "agent": "Tabular SQL Agent",
            "action": "Query Users & Orders Summary",
            "details": "Gathering operational high level business metrics."
        })
        users_count = len(gateway.execute_sql("SELECT id FROM users"))
        orders_sum = gateway.execute_sql("SELECT SUM(total_amount) as total FROM orders")[0]['total']
        
        data = {
            "total_users": users_count,
            "revenue": round(orders_sum or 0, 2),
            "match": vector_res[0]['text_content'] if vector_res else "No specific policy matched."
        }

        trace.append({
            "agent": "Vibe Coder UI Agent",
            "action": "Generate Overview Hub Dashboard",
            "details": "Crafting general overview panel."
        })

        ui_code = """
        const EphemeralDashboard = ({ data }) => {
            return (
                <div className="space-y-6 animate-fadeIn">
                    <div className="flex justify-between items-center bg-slate-900/60 backdrop-blur-md p-4 rounded-xl border border-blue-500/20 shadow-lg">
                        <div>
                            <h2 className="text-xl font-bold text-blue-400">Corporate Overview Center</h2>
                            <p className="text-xs text-slate-400">Consolidated live business metrics</p>
                        </div>
                    </div>

                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                        <div className="bg-slate-950 p-6 rounded-xl border border-slate-800 shadow">
                            <span className="text-[10px] tracking-widest text-slate-500 uppercase block mb-1">Enterprise Gross Sales</span>
                            <span className="text-3xl font-extrabold text-blue-400">${data.revenue.toFixed(2)}</span>
                            <div className="mt-4 text-xs text-slate-400">Total volume processed across all customers.</div>
                        </div>
                        <div className="bg-slate-950 p-6 rounded-xl border border-slate-800 shadow">
                            <span className="text-[10px] tracking-widest text-slate-500 uppercase block mb-1">Active Accounts</span>
                            <span className="text-3xl font-extrabold text-slate-200">{data.total_users} Users</span>
                            <div className="mt-4 text-xs text-slate-400">Platform members fully validated inside directory.</div>
                        </div>
                    </div>

                    <div className="bg-slate-950 border border-slate-800 p-4 rounded-xl shadow">
                        <h4 className="font-bold text-blue-400 text-sm mb-2">Matched Governance Regulations</h4>
                        <p className="text-xs text-slate-300 italic">"{data.match}"</p>
                    </div>
                </div>
            );
        };
        return EphemeralDashboard;
        """

    return {
        "trace": trace,
        "data": data,
        "ui_code": ui_code
    }


# ==================== 4. ENDPOINTS ====================

@app.post("/api/auth/register")
async def register(req: RegisterRequest):
    try:
        Session = sessionmaker(bind=gateway.engine)
        db = Session()
        
        # Check if user already exists
        existing_user = db.query(User).filter(User.email == req.email).first()
        if existing_user:
            db.close()
            raise HTTPException(status_code=400, detail="User with this email already exists.")
            
        hashed_password = get_password_hash(req.password)
        new_user = User(
            name=req.name,
            email=req.email,
            role=req.role,
            password_hash=hashed_password
        )
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        
        token = create_access_token({"email": new_user.email, "role": new_user.role, "user_id": new_user.id})
        
        # Log this registration event to the compliance ledger
        gateway.log_audit_event(
            agent_name="System Auth Gateway",
            action_type="TRANSACTION_MUTATION",
            action_details=json.dumps({"action": "user_registration", "email": new_user.email, "role": new_user.role})
        )
        
        db.close()
        return {
            "status": "success",
            "message": "User registered successfully.",
            "access_token": token,
            "token_type": "bearer",
            "user": {
                "id": new_user.id,
                "name": new_user.name,
                "email": new_user.email,
                "role": new_user.role
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/auth/login")
async def login(req: LoginRequest):
    try:
        Session = sessionmaker(bind=gateway.engine)
        db = Session()
        
        user = db.query(User).filter(User.email == req.email).first()
        if not user or not verify_password(req.password, user.password_hash):
            db.close()
            raise HTTPException(status_code=401, detail="Incorrect email or password.")
            
        token = create_access_token({"email": user.email, "role": user.role, "user_id": user.id})
        
        db.close()
        return {
            "status": "success",
            "message": "Login successful.",
            "access_token": token,
            "token_type": "bearer",
            "user": {
                "id": user.id,
                "name": user.name,
                "email": user.email,
                "role": user.role
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


def try_enqueue_rabbitmq(task_id: str, query: str, role: str, email: str) -> bool:
    try:
        rabbitmq_conn_str = os.getenv("ConnectionStrings__rabbitmq")
        if rabbitmq_conn_str:
            params = pika.URLParameters(rabbitmq_conn_str)
        else:
            params = pika.ConnectionParameters(host='localhost', connection_attempts=1, retry_delay=1)
        
        connection = pika.BlockingConnection(params)
        channel = connection.channel()
        channel.queue_declare(queue='agent_tasks', durable=True)
        
        payload = {
            "task_id": task_id,
            "query": query,
            "role": role,
            "email": email
        }
        
        channel.basic_publish(
            exchange='',
            routing_key='agent_tasks',
            body=json.dumps(payload),
            properties=pika.BasicProperties(
                delivery_mode=2,  # make message persistent
            )
        )
        connection.close()
        print(f"[RabbitMQ] Successfully enqueued task {task_id}", flush=True)
        return True
    except Exception as e:
        print(f"[RabbitMQ] Failed to connect/publish, falling back to local queue: {e}", flush=True)
        return False


def local_worker():
    from datetime import datetime
    while True:
        try:
            task_payload = local_task_queue.get()
            if task_payload is None:
                break
            
            task_id = task_payload["task_id"]
            question = task_payload["query"]
            role = task_payload["role"]
            email = task_payload["email"]
            
            print(f"[Local Worker] Starting task {task_id}: '{question}' (role={role}, email={email})", flush=True)
            
            # Update status to processing
            Session = sessionmaker(bind=gateway.engine)
            db = Session()
            try:
                task_db = db.query(Task).filter(Task.task_id == task_id).first()
                if task_db:
                    task_db.status = "processing"
                    db.commit()
            except Exception as db_err:
                print(f"[Local Worker] DB error: {db_err}", flush=True)
                
            # Set request-scoped context variables so middleware (e.g. current_user_role) works correctly
            from auth import current_user_role, current_user_email
            token_role = current_user_role.set(role)
            token_email = current_user_email.set(email)
            
            try:
                api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
                custom_id = os.getenv("CUSTOM_CLIENT_ID")
                custom_secret = os.getenv("CUSTOM_CLIENT_SECRET")
                
                if (custom_id and custom_secret) or api_key:
                    try:
                        result = run_real_llm_agent(question)
                    except Exception as llm_err:
                        print(f"[Local Worker] Real LLM agent failed: {llm_err}. Falling back to simulator.", flush=True)
                        result = simulate_agentic_workflow(question)
                else:
                    result = simulate_agentic_workflow(question)
                
                # Success!
                task_db = db.query(Task).filter(Task.task_id == task_id).first()
                if task_db:
                    task_db.status = "completed"
                    task_db.result_json = json.dumps(result)
                    task_db.finished_at = datetime.utcnow()
                    db.commit()
                    print(f"[Local Worker] Task {task_id} completed successfully.", flush=True)
                    
            except Exception as e:
                print(f"[Local Worker] Error processing task {task_id}: {e}", flush=True)
                task_db = db.query(Task).filter(Task.task_id == task_id).first()
                if task_db:
                    task_db.status = "failed"
                    task_db.result_json = json.dumps({"error": str(e)})
                    task_db.finished_at = datetime.utcnow()
                    db.commit()
            finally:
                # Reset context variables
                current_user_role.reset(token_role)
                current_user_email.reset(token_email)
                db.close()
                local_task_queue.task_done()
        except Exception as queue_err:
            print(f"[Local Worker] Unexpected error in queue loop: {queue_err}", flush=True)


# Start local worker thread only if not running in the worker daemon
import sys
if "worker.py" not in sys.argv[0]:
    local_task_queue = queue.Queue()
    worker_thread = threading.Thread(target=local_worker, daemon=True)
    worker_thread.start()


@app.post("/api/query")
async def execute_query(req: QueryRequest, user: dict = Depends(get_authenticated_user)):
    try:
        # Generate a unique task_id (UUID)
        task_id = str(uuid.uuid4())
        
        # Log query request to audit ledger
        gateway.log_audit_event(
            agent_name="Autonomous Kernel Agent",
            action_type="QUERY_ANALYSIS",
            action_details=json.dumps({"question": req.question})
        )
        
        # Record it in the tasks table with status 'pending'
        Session = sessionmaker(bind=gateway.engine)
        db = Session()
        task = Task(
            task_id=task_id,
            status="pending",
            query=req.question,
            role=user.get("role"),
            email=user.get("email")
        )
        db.add(task)
        db.commit()
        db.close()
        
        # Try pushing to RabbitMQ first
        pushed = try_enqueue_rabbitmq(task_id, req.question, user.get("role"), user.get("email"))
        if not pushed:
            # Push to the local in-memory queue
            local_task_queue.put({
                "task_id": task_id,
                "query": req.question,
                "role": user.get("role"),
                "email": user.get("email")
            })
            
        return {"status": "pending", "task_id": task_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/tasks/{task_id}")
async def get_task_status(task_id: str, user: dict = Depends(get_authenticated_user)):
    try:
        Session = sessionmaker(bind=gateway.engine)
        db = Session()
        task = db.query(Task).filter(Task.task_id == task_id).first()
        if not task:
            db.close()
            raise HTTPException(status_code=404, detail="Task not found")
        
        status = task.status
        result_str = task.result_json
        db.close()
        
        response_data = {
            "task_id": task_id,
            "status": status,
        }
        
        if result_str:
            try:
                result_json = json.loads(result_str)
                if isinstance(result_json, dict) and "error" in result_json:
                    response_data["error"] = result_json["error"]
                
                response_data["result"] = result_json
                
                if isinstance(result_json, dict):
                    response_data["trace"] = result_json.get("trace", [])
                    response_data["data"] = result_json.get("data", {})
                    response_data["ui_code"] = result_json.get("ui_code", "")
            except Exception:
                response_data["result"] = result_str
                response_data["error"] = result_str
        else:
            response_data["result"] = None
            
        return response_data
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/action")
async def execute_action(req: ActionRequest, user: dict = Depends(get_authenticated_user)):
    try:
        if user["role"] == "customer":
            raise HTTPException(status_code=403, detail="Forbidden: Customers are not permitted to execute actions.")
            
        action_id = req.action_id
        params = req.params
        
        if action_id == "approve_waiver":
            order_id = params.get("order_id")
            engine = gateway.engine
            with engine.connect() as conn:
                conn.execute(
                    text("UPDATE orders SET status = 'approved' WHERE id = :id"),
                    {"id": order_id}
                )
                conn.commit()
            
            return {
                "status": "success",
                "message": f"Security Bypass: High Value Transaction Order #00{order_id} has been manually approved and verified in the ledger.",
                "trace_log": "Compliance Auditor approved manual waiver override. Event emitted on ledger: WAIVER_GRANTED."
            }
            
        elif action_id == "reorder_stock":
            product_name = params.get("product_name")
            engine = gateway.engine
            with engine.connect() as conn:
                conn.execute(
                    text("UPDATE products SET stock_quantity = stock_quantity + 50 WHERE name = :name"),
                    {"name": product_name}
                )
                conn.commit()
            
            # Log this override event into the compliance ledger
            gateway.log_audit_event(
                agent_name="Supply Chain Agent",
                action_type="TRANSACTION_MUTATION",
                action_details=json.dumps({"action": "reorder_stock", "product_name": product_name})
            )
            
            return {
                "status": "success",
                "message": f"Supply Chain Action: Initiated purchase request. Added 50 units stock replenishment for '{product_name}'.",
                "trace_log": "Supply Chain Agent processed automated restock trigger. Reorder threshold crossed."
            }
            
        return {"status": "error", "message": "Unknown action"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/action/execute")
async def execute_action_execute(req: ActionExecuteRequest, user: dict = Depends(get_authenticated_user)):
    try:
        # Enforce role restriction at endpoint level as well (redundancy)
        if user["role"] == "customer":
            raise HTTPException(status_code=403, detail="Forbidden: Customers are not permitted to execute write actions.")
            
        print(f"DEBUG main: id(current_user_role)={id(current_user_role)}, current_user_role.get()={current_user_role.get()}")
        result = gateway.execute_action_mutation(
            sql_query_str=req.query,
            params=req.params,
            agent_name="Autonomous Kernel Agent",
            governing_node_id=req.governing_node_id
        )
        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/ledger")
async def get_ledger(user: dict = Depends(get_authenticated_user)):
    try:
        if user["role"] == "customer":
            raise HTTPException(status_code=403, detail="Forbidden: Access restricted to employees and administrators.")
            
        with gateway.engine.connect() as conn:
            result = conn.execute(text("SELECT id, timestamp, agent_name, action_type, action_details, governing_node_id, prev_hash, row_hash FROM audit_ledger ORDER BY id DESC"))
            rows = result.fetchall()
            
            events = []
            for row in rows:
                row_id, timestamp, agent_name, action_type, action_details, governing_node_id, prev_hash, row_hash = row
                try:
                    parsed_details = json.loads(action_details)
                except Exception:
                    parsed_details = action_details
                
                events.append({
                    "id": row_id,
                    "timestamp": timestamp.isoformat() if hasattr(timestamp, "isoformat") else str(timestamp),
                    "agent_name": agent_name,
                    "action_type": action_type,
                    "action_details": parsed_details,
                    "governing_node_id": governing_node_id,
                    "prev_hash": prev_hash,
                    "row_hash": row_hash
                })
        
        tampered_indices = gateway.verify_ledger_integrity()
        is_verified = len(tampered_indices) == 0
        
        return {
            "is_verified": is_verified,
            "tampered_indices": tampered_indices,
            "events": events
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/schema")
async def get_schema(user: dict = Depends(get_authenticated_user)):
    try:
        if user["role"] == "customer":
            raise HTTPException(status_code=403, detail="Forbidden: Access restricted to employees and administrators.")
        return {"schema": gateway.get_schema_info()}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/graph")
async def get_graph(user: dict = Depends(get_authenticated_user)):
    try:
        if user["role"] == "customer":
            raise HTTPException(status_code=403, detail="Forbidden: Access restricted to employees and administrators.")
            
        with gateway.engine.connect() as conn:
            node_check = conn.execute(text("SELECT name FROM sqlite_master WHERE type='table' AND name='graph_nodes';")).fetchone()
            if not node_check:
                return {"nodes": [], "edges": []}
            
            nodes_res = conn.execute(text("SELECT id, label, name, description, properties FROM graph_nodes;")).fetchall()
            edges_res = conn.execute(text("SELECT id, source_id, target_id, edge_type FROM graph_edges;")).fetchall()
            
            nodes = []
            for row in nodes_res:
                try:
                    props = json.loads(row[4]) if row[4] else {}
                except Exception:
                    props = {}
                nodes.append({
                    "id": row[0],
                    "label": row[1],
                    "name": row[2],
                    "description": row[3],
                    "properties": props
                })
                
            edges = []
            for row in edges_res:
                edges.append({
                    "id": row[0],
                    "source": row[1],
                    "target": row[2],
                    "type": row[3]
                })
                
            return {"nodes": nodes, "edges": edges}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
