import os
import json
import sqlparse
import math
import hashlib
from datetime import datetime
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from pydantic import BaseModel, Field, field_validator
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain_core.prompts import PromptTemplate

# Auth contexts
from auth import current_user_role, current_user_email

# Core / Storage modular drivers
from core.db import (
    engine, DB_FILE_PATH, log_audit_event, verify_ledger_integrity, secure_sql_query
)
from storage.neo4j_client import Neo4jGraphAdapter
from storage.qdrant_client import QdrantVectorAdapter

# Determine paths
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(CURRENT_DIR, ".env"))

# ==================== 1. SECURITY & GUARDRAILS LAYER ====================

class SQLQuery(BaseModel):
    query: str = Field(description="The SQL query to execute")
    
    @field_validator('query')
    @classmethod
    def validate_sql(cls, v: str) -> str:
        parsed = sqlparse.parse(v)
        if not parsed:
            raise ValueError("Invalid SQL")
        
        for statement in parsed:
            stmt_type = statement.get_type().upper()
            allowed_types = ['SELECT', 'EXPLAIN', 'SHOW']
            if stmt_type not in allowed_types:
                raise ValueError(f"UNAUTHORIZED QUERY TYPE: {stmt_type}. Only SELECT queries are allowed for read-only agents.")
            
            forbidden_keywords = ['DROP', 'DELETE', 'INSERT', 'UPDATE', 'ALTER', 'GRANT', 'REVOKE', 'TRUNCATE']
            upper_query = v.upper()
            for keyword in forbidden_keywords:
                if f" {keyword} " in upper_query or upper_query.startswith(f"{keyword} ") or f"\n{keyword} " in upper_query:
                    raise ValueError(f"FORBIDDEN KEYWORD DETECTED: {keyword}. Schema mutation blocked by middleware.")
        return v


class DBASchemaMutation(BaseModel):
    query: str = Field(description="The SQL DDL query to modify the schema")
    
    @field_validator('query')
    @classmethod
    def validate_ddl(cls, v: str) -> str:
        parsed = sqlparse.parse(v)
        if not parsed:
            raise ValueError("Invalid DDL SQL query.")
        
        for statement in parsed:
            stmt_type = statement.get_type().upper()
            allowed_types = ['CREATE', 'ALTER']
            if stmt_type not in allowed_types:
                raise ValueError(f"UNAUTHORIZED DDL OPERATION: {stmt_type}. Only CREATE and ALTER statements are allowed for database evolution.")
            
            forbidden_keywords = ['DROP', 'DELETE', 'TRUNCATE', 'RENAME TO']
            upper_query = v.upper()
            for keyword in forbidden_keywords:
                if f" {keyword} " in upper_query or upper_query.startswith(f"{keyword} ") or f"\n{keyword} " in upper_query:
                    raise ValueError(f"FORBIDDEN DESTRUCTIVE KEYWORD DETECTED: {keyword}. Schema mutation blocked by middleware.")
        return v


class GeneralizedActionMutation(BaseModel):
    query: str = Field(description="The parameterized SQL query to execute")
    params: dict = Field(default_factory=dict, description="Parameters for the query")
    
    @field_validator('query')
    @classmethod
    def validate_action(cls, v: str) -> str:
        parsed = sqlparse.parse(v)
        if not parsed:
            raise ValueError("Invalid SQL")
        
        for statement in parsed:
            stmt_type = statement.get_type().upper()
            allowed_types = ['UPDATE', 'INSERT']
            if stmt_type not in allowed_types:
                raise ValueError(f"UNAUTHORIZED ACTION TYPE: {stmt_type}. Only UPDATE and INSERT queries are allowed for action execution.")
            
            forbidden_keywords = ['DROP', 'DELETE', 'TRUNCATE', 'ALTER', 'CREATE', 'GRANT', 'REVOKE']
            upper_query = v.upper()
            for keyword in forbidden_keywords:
                if f" {keyword} " in upper_query or upper_query.startswith(f"{keyword} ") or f"\n{keyword} " in upper_query or upper_query.endswith(f" {keyword}"):
                    raise ValueError(f"FORBIDDEN KEYWORD DETECTED: {keyword}. Action execution blocked by middleware.")
            
            forbidden_tables = ['graph_nodes', 'graph_edges', 'vector_partitions', 'audit_ledger', 'sqlite_master', 'sqlite_sequence']
            lower_query = v.lower()
            for table in forbidden_tables:
                if table in lower_query:
                    raise ValueError(f"UNAUTHORIZED SYSTEM TABLE ACCESS: Attempted modification of system table '{table}' blocked.")
        return v


# ==================== 2. THE SHIELD GATEWAY ====================

class ShieldGateway:
    def __init__(self, db_path=DB_FILE_PATH):
        self.db_path = db_path
        self.engine = engine
        
        # Instantiate Graph adapter
        neo4j_uri = os.getenv("NEO4J_URI", "bolt://localhost:7687")
        neo4j_user = os.getenv("NEO4J_USER") or os.getenv("NEO4J_USERNAME") or "neo4j"
        neo4j_password = os.getenv("NEO4J_PASSWORD", "password")
        print(f"Connecting to Neo4j at {neo4j_uri}...")
        self.graph_adapter = Neo4jGraphAdapter(neo4j_uri, neo4j_user, neo4j_password)
        print("Successfully connected to Neo4j.")
            
        # Instantiate Vector adapter
        self.vector_adapter = QdrantVectorAdapter(CURRENT_DIR)
        print("Connecting to Qdrant...")
        # Verify connection immediately to fail loudly if Qdrant container is absent or unsuccessful
        qdrant_conn_test = self.vector_adapter._get_client()
        qdrant_conn_test.close()
        print("Successfully connected to Qdrant.")

        
        # Sync from SQLite if needed
        try:
            self.sync_from_sqlite_if_needed()
        except Exception as e:
            print(f"Failed to run auto-sync on init: {e}")

    def sync_from_sqlite_if_needed(self):
        if self.graph_adapter.is_empty():
            with self.engine.connect() as conn:
                node_check = conn.execute(text("SELECT name FROM sqlite_master WHERE type='table' AND name='graph_nodes';")).fetchone()
                if not node_check:
                    return
                
                nodes_res = conn.execute(text("SELECT id, label, name, description, skill_markdown, properties, clearance_level FROM graph_nodes;")).fetchall()
                if not nodes_res:
                    return
                    
                print("Graph store is empty, but SQLite contains nodes. Starting migration/synchronization...")
                
                for row in nodes_res:
                    node_id, label, name, description, skill_markdown, properties, clearance = row
                    self.graph_adapter.create_or_update_node(
                        node_id=node_id,
                        label=label,
                        name=name,
                        description=description,
                        skill_markdown=skill_markdown,
                        properties=properties,
                        clearance_level=clearance
                    )
                
                edges_res = conn.execute(text("SELECT source_id, target_id, edge_type, properties FROM graph_edges;")).fetchall()
                for row in edges_res:
                    source_id, target_id, edge_type, properties = row
                    self.graph_adapter.create_edge(
                        source_id=source_id,
                        target_id=target_id,
                        edge_type=edge_type,
                        properties=properties
                    )
                    
                vectors_res = conn.execute(text("SELECT node_id, source_type, text_content, embedding, clearance_level FROM vector_partitions;")).fetchall()
                records = []
                for row in vectors_res:
                    node_id, source_type, text_content, embedding_json, clearance = row
                    vector = json.loads(embedding_json)
                    records.append({
                        "node_id": node_id,
                        "source_type": source_type,
                        "text_content": text_content,
                        "vector": vector,
                        "clearance_level": clearance
                    })
                if hasattr(self.vector_adapter, "upsert_vectors_batch"):
                    self.vector_adapter.upsert_vectors_batch(records)
                else:
                    for r in records:
                        self.vector_adapter.upsert_vector(
                            node_id=r["node_id"],
                            source_type=r["source_type"],
                            text_content=r["text_content"],
                            vector=r["vector"],
                            clearance_level=r["clearance_level"]
                        )
                print("Synchronization completed successfully.")

    def clear_graph_and_vector_stores(self):
        try:
            self.graph_adapter.clear_all()
        except Exception as e:
            print(f"Failed to clear graph store: {e}")
        try:
            self.vector_adapter.clear_all()
        except Exception as e:
            print(f"Failed to clear vector store: {e}")

    # --- DELEGATED AUDIT LEDGER HELPERS ---
    def log_audit_event(self, agent_name: str, action_type: str, action_details: str, governing_node_id: int = None):
        return log_audit_event(agent_name, action_type, action_details, governing_node_id)

    def verify_ledger_integrity(self) -> list:
        return verify_ledger_integrity()

    # --- GENERALIZED MUTATION ACTION ENGINE ---
    def execute_action_mutation(self, sql_query_str: str, params: dict = None, agent_name: str = "Autonomous Kernel Agent", governing_node_id: int = None, role: str = None):
        try:
            if role is None:
                role = current_user_role.get()
            if role == "customer":
                raise PermissionError("UNAUTHORIZED ACTION: Customers are not permitted to execute write actions.")
            elif role is None:
                raise PermissionError("UNAUTHORIZED ACTION: Unauthenticated users are not permitted to execute write actions.")

            if params is None:
                params = {}
            # Validate query and parameters
            validated = GeneralizedActionMutation(query=sql_query_str.strip(), params=params)
            
            # Simple bind parameter presence validation
            import re
            bind_pattern = re.compile(r":([a-zA-Z0-9_]+)")
            missing_params = []
            for param_name in bind_pattern.findall(validated.query):
                if param_name not in validated.params or validated.params[param_name] is None or validated.params[param_name] == "":
                    missing_params.append(param_name)
            if missing_params:
                raise ValueError(f"Missing or invalid value for bind parameter(s): {', '.join(missing_params)}")
                
            with self.engine.begin() as conn:
                conn.execute(text(validated.query), validated.params)
            
            # Log action to audit ledger
            self.log_audit_event(
                agent_name=agent_name,
                action_type="TRANSACTION_MUTATION",
                action_details=json.dumps({"query": validated.query, "params": validated.params}),
                governing_node_id=governing_node_id
            )
            
            return {
                "status": "success",
                "message": "Action executed successfully and recorded in the audit ledger."
            }
        except Exception as e:
            return {"error": f"Action Execution Blocked: {str(e)}"}

    # --- A. SQL GATEWAY (Transactional with RBAC) ---
    def execute_sql(self, sql_query_str: str, role: str = None, email: str = None):
        try:
            validated = SQLQuery(query=sql_query_str.strip())
            
            # Retrieve authentication context
            if role is None:
                role = current_user_role.get() or "customer"
            if email is None:
                email = current_user_email.get() or ""
            
            # Enforce dynamic database-level RBAC constraint rewriting
            secured_query = secure_sql_query(validated.query, role, email)
            
            with self.engine.connect() as conn:
                result = conn.execute(text(secured_query))
                columns = result.keys()
                rows = []
                for row in result.fetchall():
                    d = dict(zip(columns, row))
                    if 'id' in d and 'order_id' not in d:
                        d['order_id'] = d['id']
                    if 'order_id' in d and 'id' not in d:
                        d['id'] = d['order_id']
                    rows.append(d)
                return rows
        except Exception as e:
            return {"error": f"SQL Execution Blocked: {str(e)}"}

    # --- B. GRAPH GATEWAY (Workflows & Regulations) ---
    def traverse_graph(self, start_node_name: str, role: str = None):
        try:
            self.sync_from_sqlite_if_needed()
            return self.graph_adapter.traverse_graph(start_node_name, role=role)
        except Exception as e:
            return {"error": f"Graph Traversal Error: {str(e)}"}

    # --- C. VECTOR GATEWAY (Global Semantic Search with RBAC) ---
    def vector_search(self, query_text: str, limit=2, role: str = None):
        try:
            self.sync_from_sqlite_if_needed()
            
            api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
            if api_key:
                embeddings_model = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-2", google_api_key=api_key)
                query_vector = embeddings_model.embed_query(query_text)
            else:
                query_vector = [0.1, 0.1, 0.1]
                q_lower = query_text.lower()
                if "high" in q_lower or "value" in q_lower or "limit" in q_lower or "over" in q_lower or "waiver" in q_lower:
                    query_vector = [0.9, 0.1, 0.05]
                elif "discount" in q_lower:
                    query_vector = [0.05, 0.9, 0.1]
                elif "workflow" in q_lower or "process" in q_lower or "logistic" in q_lower or "chair" in q_lower:
                    query_vector = [0.1, 0.1, 0.9]

            return self.vector_adapter.search_vectors(query_vector, limit=limit, role=role)
        except Exception as e:
            return {"error": f"Vector Search Error: {str(e)}"}

    # --- D. LOCALIZED VECTOR GATEWAY (Node-Level Semantic Search with RBAC) ---
    def node_vector_search(self, node_id: int, query_text: str, limit=2, role: str = None):
        try:
            self.sync_from_sqlite_if_needed()
            
            api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
            if api_key:
                embeddings_model = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-2", google_api_key=api_key)
                query_vector = embeddings_model.embed_query(query_text)
            else:
                query_vector = [0.1, 0.1, 0.1]
                q_lower = query_text.lower()
                if "limit" in q_lower or "high" in q_lower or "value" in q_lower or "waiver" in q_lower:
                    query_vector = [0.9, 0.1, 0.05]
                elif "warehouse" in q_lower or "logistic" in q_lower or "chair" in q_lower or "bulk" in q_lower:
                    query_vector = [0.1, 0.9, 0.05]

            return self.vector_adapter.search_vectors_by_node(node_id, query_vector, limit=limit, role=role)
        except Exception as e:
            return {"error": f"Node Vector Search Error: {str(e)}"}

    # --- E. EVOLUTIONARY DBA MUTATION GATEWAY ---
    def execute_ddl(self, ddl_sql: str, agent_name: str = "Autonomous Kernel Agent", governing_node_id: int = None, role: str = None):
        try:
            if role is None:
                role = current_user_role.get()
            if role != "admin":
                raise PermissionError("UNAUTHORIZED DDL OPERATION: Only administrators are permitted to evolve the database schema.")

            validated = DBASchemaMutation(query=ddl_sql.strip())
            with self.engine.begin() as conn:
                conn.execute(text(validated.query))
            
            # Log to audit ledger
            self.log_audit_event(
                agent_name=agent_name,
                action_type="SCHEMA_EVOLUTION",
                action_details=json.dumps({"ddl_query": validated.query}),
                governing_node_id=governing_node_id
            )
            
            return {"status": "success", "message": "Database schema evolved successfully."}
        except Exception as e:
            return {"error": f"DBA Schema Mutation Blocked: {str(e)}"}

    # --- F. DYNAMIC SCHEMA INTROSPECTION ---
    def get_schema_info(self, role: str = None) -> str:
        try:
            self.sync_from_sqlite_if_needed()
            
            schema_details = []
            with self.engine.connect() as conn:
                schema_details.append("### 1. Tabular SQL Schema")
                result = conn.execute(text("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' AND name NOT IN ('graph_nodes', 'graph_edges', 'vector_partitions');"))
                tables = [row[0] for row in result.fetchall()]
                
                for table in tables:
                    info_res = conn.execute(text(f"PRAGMA table_info({table});"))
                    columns = [f"{c[1]} ({c[2]})" for c in info_res.fetchall()]
                    schema_details.append(f"- **{table}**: {', '.join(columns)}")
                
                schema_details.append("\n### 2. Graph Governance Ledger (Workflows & Regulations)")
                nodes = self.graph_adapter.get_all_nodes_with_edges(role=role)
                if nodes:
                    for node in nodes:
                        node_id = node["id"]
                        name = node["name"]
                        label = node["label"]
                        description = node["description"]
                        edges = node["edges"]
                        
                        edge_names = [e["name"] for e in edges]
                        edge_str = f" [governs: {', '.join(edge_names)}]" if edge_names else ""
                        schema_details.append(f"- **Node #{node_id}** ({label.upper()}): {name}{edge_str}\n  *Description: {description}*")
                else:
                    schema_details.append("- *Graph Ledger tables not initialized yet.*")

                schema_details.append("\n### 3. Contextual Vector Partition Distribution")
                node_counts = {}
                for col in ["erp_vectors_768", "erp_vectors_3"]:
                    try:
                        res = self.vector_adapter.scroll_vectors(
                            collection_name=col,
                            limit=1000
                        )
                        for point in res:
                            p = point.payload or {}
                            nid = p.get("node_id")
                            if nid is not None:
                                node_counts[nid] = node_counts.get(nid, 0) + 1
                    except Exception:
                        pass
                        
                if node_counts:
                    for nid, count in node_counts.items():
                        node_name = self.graph_adapter.get_node_name_by_id(nid) or f"Unknown Node #{nid}"
                        schema_details.append(f"- **Node '{node_name}'**: {count} vectorized rules/documents mapped.")
                else:
                    schema_details.append("- *No vector partition mappings created yet.*")
                
            return "\n".join(schema_details)
        except Exception as e:
            return f"Schema extraction error: {str(e)}"

    # --- G. EVOLUTIONARY GRAPH MUTATION GATEWAY ---
    def execute_graph_mutation(self, label: str, name: str, description: str, skill_markdown: str, properties: str = "{}", target_edges: list = None, agent_name: str = "Autonomous Kernel Agent", governing_node_id: int = None, role: str = None):
        try:
            if role is None:
                role = current_user_role.get()
            if role != "admin":
                raise PermissionError("UNAUTHORIZED GRAPH EVOLUTION: Only administrators are permitted to evolve the governance graph topology.")

            if label.upper() not in ['WORKFLOW', 'REGULATION', 'AGENT']:
                raise ValueError(f"UNAUTHORIZED GRAPH NODE LABEL: {label}. Label must be WORKFLOW, REGULATION, or AGENT.")
            
            if not name.strip():
                raise ValueError("Node name cannot be empty.")
            
            self.sync_from_sqlite_if_needed()
            
            node_id, msg = self.graph_adapter.create_or_update_node(
                node_id=None,
                label=label,
                name=name,
                description=description,
                skill_markdown=skill_markdown,
                properties=properties
            )
            
            if target_edges:
                for edge in target_edges:
                    target_name = edge.get("target_name")
                    edge_type = edge.get("edge_type", "GOVERNS")
                    target_id = self.graph_adapter.get_node_id_by_name(target_name)
                    if target_id is not None:
                        self.graph_adapter.create_edge(
                            source_id=node_id,
                            target_id=target_id,
                            edge_type=edge_type
                        )
            
            # Log graph evolution to audit ledger
            self.log_audit_event(
                agent_name=agent_name,
                action_type="GRAPH_EVOLUTION",
                action_details=json.dumps({
                    "label": label,
                    "name": name,
                    "description": description,
                    "skill_markdown": skill_markdown,
                    "properties": properties,
                    "target_edges": target_edges
                }),
                governing_node_id=governing_node_id
            )
            
            return {"status": "success", "message": msg}
        except Exception as e:
            return {"error": f"Graph Evolution Blocked: {str(e)}"}

    # --- H. EVOLUTIONARY VECTOR MUTATION GATEWAY ---
    def execute_vector_mutation(self, node_id: int, source_type: str, text_content: str, agent_name: str = "Autonomous Kernel Agent", governing_node_id: int = None, role: str = None):
        try:
            if role is None:
                role = current_user_role.get()
            if role != "admin":
                raise PermissionError("UNAUTHORIZED VECTOR EVOLUTION: Only administrators are permitted to partition and evolve the vector context.")

            if source_type.upper() not in ['LAW', 'EMAIL', 'INTERNAL_DOC', 'POLICY']:
                raise ValueError(f"UNAUTHORIZED VECTOR SOURCE TYPE: {source_type}. Must be LAW, EMAIL, INTERNAL_DOC, or POLICY.")
            
            if not text_content.strip():
                raise ValueError("Text content cannot be empty.")
            
            self.sync_from_sqlite_if_needed()
            
            # Verify node exists
            if not self.graph_adapter.node_exists(node_id):
                raise ValueError(f"Target Graph Node ID {node_id} does not exist in the database.")
            
            api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
            if api_key:
                embeddings_model = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-2", google_api_key=api_key)
                vector = embeddings_model.embed_query(text_content)
            else:
                vector = [0.1, 0.1, 0.1]
                q_lower = text_content.lower()
                if "high" in q_lower or "value" in q_lower or "limit" in q_lower or "over" in q_lower or "waiver" in q_lower:
                    vector = [0.9, 0.1, 0.05]
                elif "discount" in q_lower:
                    vector = [0.05, 0.9, 0.1]
                elif "workflow" in q_lower or "process" in q_lower or "logistic" in q_lower or "chair" in q_lower:
                    vector = [0.1, 0.1, 0.9]
            
            self.vector_adapter.upsert_vector(node_id, source_type, text_content, vector)
            
            # Log vector evolution to audit ledger
            self.log_audit_event(
                agent_name=agent_name,
                action_type="VECTOR_EVOLUTION",
                action_details=json.dumps({
                    "node_id": node_id,
                    "source_type": source_type,
                    "text_content": text_content
                }),
                governing_node_id=governing_node_id
            )
            
            return {
                "status": "success", 
                "message": f"Successfully vectorized and mapped '{source_type}' context to Graph Node ID {node_id}."
            }
        except Exception as e:
            return {"error": f"Vector Evolution Blocked: {str(e)}"}
