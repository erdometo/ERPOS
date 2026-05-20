import os
import json
import sqlparse
import math
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from pydantic import BaseModel, Field, field_validator
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_core.prompts import PromptTemplate

# Determine active path
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
DB_FILE_PATH = os.path.join(CURRENT_DIR, "erp_database.db")
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
            
            # Strictly prevent destructive alterations
            forbidden_keywords = ['DROP', 'DELETE', 'TRUNCATE', 'RENAME TO']
            upper_query = v.upper()
            for keyword in forbidden_keywords:
                if f" {keyword} " in upper_query or upper_query.startswith(f"{keyword} ") or f"\n{keyword} " in upper_query:
                    raise ValueError(f"FORBIDDEN DESTRUCTIVE KEYWORD DETECTED: {keyword}. Schema mutation blocked by middleware.")
        return v


# ==================== 2. THE MULTI-MODEL MIDDLEWARE GATEWAY ====================
class ShieldGateway:
    def __init__(self, db_path=DB_FILE_PATH):
        self.db_path = db_path
        self.engine = create_engine(f"sqlite:///{db_path}")

    # --- A. SQL GATEWAY (Transactional) ---
    def execute_sql(self, sql_query_str: str):
        try:
            validated = SQLQuery(query=sql_query_str.strip())
            with self.engine.connect() as conn:
                result = conn.execute(text(validated.query))
                columns = result.keys()
                return [dict(zip(columns, row)) for row in result.fetchall()]
        except Exception as e:
            return {"error": f"SQL Execution Blocked: {str(e)}"}

    # --- B. GRAPH GATEWAY (Workflows & Regulations) ---
    def traverse_graph(self, start_node_name: str):
        try:
            query = """
            SELECT n2.id AS target_id, n2.name AS target_name, n2.label AS target_label, n2.description AS target_desc, e.edge_type
            FROM graph_nodes n1
            JOIN graph_edges e ON n1.id = e.source_id
            JOIN graph_nodes n2 ON e.target_id = n2.id
            WHERE n1.name = :name
            UNION
            SELECT n1.id AS target_id, n1.name AS target_name, n1.label AS target_label, n1.description AS target_desc, e.edge_type
            FROM graph_nodes n1
            JOIN graph_edges e ON n1.id = e.target_id
            JOIN graph_nodes n2 ON e.source_id = n2.id
            WHERE n2.name = :name
            """
            with self.engine.connect() as conn:
                result = conn.execute(text(query), {"name": start_node_name})
                columns = result.keys()
                return [dict(zip(columns, row)) for row in result.fetchall()]
        except Exception as e:
            return {"error": f"Graph Traversal Error: {str(e)}"}

    # --- C. VECTOR GATEWAY (Global Semantic Search) ---
    def vector_search(self, query_text: str, limit=2):
        try:
            api_key = os.getenv("OPENAI_API_KEY")
            with self.engine.connect() as conn:
                result = conn.execute(text("SELECT source_type, node_id, text_content, embedding FROM vector_partitions"))
                rows = result.fetchall()
                
                if api_key:
                    embeddings_model = OpenAIEmbeddings(model="text-embedding-3-small")
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

                matches = []
                for row in rows:
                    doc_vector = json.loads(row[3])
                    dot_product = sum(a*b for a,b in zip(query_vector, doc_vector))
                    norm_a = math.sqrt(sum(a*a for a in query_vector))
                    norm_b = math.sqrt(sum(b*b for b in doc_vector))
                    similarity = dot_product / (norm_a * norm_b) if norm_a and norm_b else 0
                    
                    matches.append({
                        "source_type": row[0],
                        "node_id": row[1],
                        "text_content": row[2],
                        "similarity": round(similarity, 4)
                    })
                
                matches.sort(key=lambda x: x["similarity"], reverse=True)
                return matches[:limit]
        except Exception as e:
            return {"error": f"Vector Search Error: {str(e)}"}

    # --- D. LOCALIZED VECTOR GATEWAY (Node-Level Semantic Search) ---
    def node_vector_search(self, node_id: int, query_text: str, limit=2):
        try:
            api_key = os.getenv("OPENAI_API_KEY")
            with self.engine.connect() as conn:
                result = conn.execute(
                    text("SELECT source_type, text_content, embedding FROM vector_partitions WHERE node_id = :node_id"),
                    {"node_id": node_id}
                )
                rows = result.fetchall()
                
                if not rows:
                    return []
                
                if api_key:
                    embeddings_model = OpenAIEmbeddings(model="text-embedding-3-small")
                    query_vector = embeddings_model.embed_query(query_text)
                else:
                    query_vector = [0.1, 0.1, 0.1]
                    q_lower = query_text.lower()
                    if "limit" in q_lower or "high" in q_lower or "value" in q_lower or "waiver" in q_lower:
                        query_vector = [0.9, 0.1, 0.05]
                    elif "warehouse" in q_lower or "logistic" in q_lower or "chair" in q_lower or "bulk" in q_lower:
                        query_vector = [0.1, 0.9, 0.05]

                matches = []
                for row in rows:
                    doc_vector = json.loads(row[2])
                    dot_product = sum(a*b for a,b in zip(query_vector, doc_vector))
                    norm_a = math.sqrt(sum(a*a for a in query_vector))
                    norm_b = math.sqrt(sum(b*b for b in doc_vector))
                    similarity = dot_product / (norm_a * norm_b) if norm_a and norm_b else 0
                    
                    matches.append({
                        "source_type": row[0],
                        "text_content": row[1],
                        "similarity": round(similarity, 4)
                    })
                
                matches.sort(key=lambda x: x["similarity"], reverse=True)
                return matches[:limit]
        except Exception as e:
            return {"error": f"Node Vector Search Error: {str(e)}"}

    # --- E. EVOLUTIONARY DBA MUTATION GATEWAY ---
    def execute_ddl(self, ddl_sql: str):
        try:
            validated = DBASchemaMutation(query=ddl_sql.strip())
            with self.engine.connect() as conn:
                conn.execute(text(validated.query))
                conn.commit()
            return {"status": "success", "message": "Database schema evolved successfully."}
        except Exception as e:
            return {"error": f"DBA Schema Mutation Blocked: {str(e)}"}

    # --- F. DYNAMIC SCHEMA INTROSPECTION ---
    def get_schema_info(self) -> str:
        try:
            schema_details = []
            with self.engine.connect() as conn:
                # 1. SQL Tables
                schema_details.append("### 1. Tabular SQL Schema")
                result = conn.execute(text("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' AND name NOT IN ('graph_nodes', 'graph_edges', 'vector_partitions');"))
                tables = [row[0] for row in result.fetchall()]
                
                for table in tables:
                    info_res = conn.execute(text(f"PRAGMA table_info({table});"))
                    columns = [f"{c[1]} ({c[2]})" for c in info_res.fetchall()]
                    schema_details.append(f"- **{table}**: {', '.join(columns)}")
                
                # 2. Graph Ledger
                schema_details.append("\n### 2. Graph Governance Ledger (Workflows & Regulations)")
                # Check if graph_nodes table exists
                node_check = conn.execute(text("SELECT name FROM sqlite_master WHERE type='table' AND name='graph_nodes';")).fetchone()
                if node_check:
                    nodes_res = conn.execute(text("SELECT id, name, label, description FROM graph_nodes;")).fetchall()
                    for node in nodes_res:
                        node_id, name, label, description = node
                        # Fetch edges governed or dependent
                        edges_res = conn.execute(text("""
                            SELECT n2.name, e.edge_type 
                            FROM graph_edges e
                            JOIN graph_nodes n2 ON e.target_id = n2.id
                            WHERE e.source_id = :nid
                        """), {"nid": node_id}).fetchall()
                        edge_str = f" [governs: {', '.join([e[0] for e in edges_res])}]" if edges_res else ""
                        schema_details.append(f"- **Node #{node_id}** ({label.upper()}): {name}{edge_str}\n  *Description: {description}*")
                else:
                    schema_details.append("- *Graph Ledger tables not initialized yet.*")

                # 3. Vector Partitions
                schema_details.append("\n### 3. Contextual Vector Partition Distribution")
                vector_check = conn.execute(text("SELECT name FROM sqlite_master WHERE type='table' AND name='vector_partitions';")).fetchone()
                if vector_check:
                    vectors_res = conn.execute(text("""
                        SELECT n.name, COUNT(v.id) 
                        FROM vector_partitions v
                        JOIN graph_nodes n ON v.node_id = n.id
                        GROUP BY v.node_id;
                    """)).fetchall()
                    if vectors_res:
                        for v in vectors_res:
                            schema_details.append(f"- **Node '{v[0]}'**: {v[1]} vectorized rules/documents mapped.")
                    else:
                        schema_details.append("- *No vector partition mappings created yet.*")
                else:
                    schema_details.append("- *Vector partition tables not initialized yet.*")
                
            return "\n".join(schema_details)
        except Exception as e:
            return f"Schema extraction error: {str(e)}"

    # --- G. EVOLUTIONARY GRAPH MUTATION GATEWAY ---
    def execute_graph_mutation(self, label: str, name: str, description: str, skill_markdown: str, properties: str = "{}", target_edges: list = None):
        try:
            if label.upper() not in ['WORKFLOW', 'REGULATION', 'AGENT']:
                raise ValueError(f"UNAUTHORIZED GRAPH NODE LABEL: {label}. Label must be WORKFLOW, REGULATION, or AGENT.")
            
            if not name.strip():
                raise ValueError("Node name cannot be empty.")
            
            with self.engine.connect() as conn:
                # Check if node already exists
                check_q = text("SELECT id FROM graph_nodes WHERE name = :name")
                res = conn.execute(check_q, {"name": name}).fetchone()
                
                if res:
                    # Update existing node
                    node_id = res[0]
                    upd_q = text("""
                        UPDATE graph_nodes 
                        SET label = :label, description = :description, skill_markdown = :skill_markdown, properties = :properties 
                        WHERE id = :id
                    """)
                    conn.execute(upd_q, {
                        "label": label.lower(),
                        "description": description,
                        "skill_markdown": skill_markdown,
                        "properties": properties,
                        "id": node_id
                    })
                    msg = f"Graph Node '{name}' (ID {node_id}) evolved successfully."
                else:
                    # Insert new node
                    ins_q = text("""
                        INSERT INTO graph_nodes (label, name, description, skill_markdown, properties) 
                        VALUES (:label, :name, :description, :skill_markdown, :properties)
                    """)
                    conn.execute(ins_q, {
                        "label": label.lower(),
                        "name": name,
                        "description": description,
                        "skill_markdown": skill_markdown,
                        "properties": properties
                    })
                    node_id = conn.execute(text("SELECT last_insert_rowid()")).fetchone()[0]
                    msg = f"Created new Graph Node '{name}' (ID {node_id}) successfully."
                
                # Add target edges if requested
                if target_edges:
                    for edge in target_edges:
                        target_name = edge.get("target_name")
                        edge_type = edge.get("edge_type", "GOVERNS")
                        
                        target_res = conn.execute(text("SELECT id FROM graph_nodes WHERE name = :target_name"), {"target_name": target_name}).fetchone()
                        if target_res:
                            target_id = target_res[0]
                            # Check if edge already exists
                            edge_check = conn.execute(text("""
                                SELECT id FROM graph_edges 
                                WHERE (source_id = :source_id AND target_id = :target_id) 
                                   OR (source_id = :target_id AND target_id = :source_id)
                            """), {"source_id": node_id, "target_id": target_id}).fetchone()
                            
                            if not edge_check:
                                conn.execute(text("""
                                    INSERT INTO graph_edges (source_id, target_id, edge_type, properties)
                                    VALUES (:source_id, :target_id, :edge_type, '{}')
                                """), {"source_id": node_id, "target_id": target_id, "edge_type": edge_type.upper()})
                conn.commit()
            return {"status": "success", "message": msg}
        except Exception as e:
            return {"error": f"Graph Evolution Blocked: {str(e)}"}

    # --- H. EVOLUTIONARY VECTOR MUTATION GATEWAY ---
    def execute_vector_mutation(self, node_id: int, source_type: str, text_content: str):
        try:
            if source_type.upper() not in ['LAW', 'EMAIL', 'INTERNAL_DOC', 'POLICY']:
                raise ValueError(f"UNAUTHORIZED VECTOR SOURCE TYPE: {source_type}. Must be LAW, EMAIL, INTERNAL_DOC, or POLICY.")
            
            if not text_content.strip():
                raise ValueError("Text content cannot be empty.")
            
            api_key = os.getenv("OPENAI_API_KEY")
            if api_key:
                embeddings_model = OpenAIEmbeddings(model="text-embedding-3-small")
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
            
            vector_json = json.dumps(vector)
            
            with self.engine.connect() as conn:
                # Verify node exists
                node_res = conn.execute(text("SELECT id FROM graph_nodes WHERE id = :node_id"), {"node_id": node_id}).fetchone()
                if not node_res:
                    raise ValueError(f"Target Graph Node ID {node_id} does not exist in the database.")
                
                ins_q = text("""
                    INSERT INTO vector_partitions (node_id, source_type, text_content, embedding)
                    VALUES (:node_id, :source_type, :text_content, :embedding)
                """)
                conn.execute(ins_q, {
                    "node_id": node_id,
                    "source_type": source_type.lower(),
                    "text_content": text_content,
                    "embedding": vector_json
                })
                conn.commit()
            
            return {
                "status": "success", 
                "message": f"Successfully vectorized and mapped '{source_type}' context to Graph Node ID {node_id}."
            }
        except Exception as e:
            return {"error": f"Vector Evolution Blocked: {str(e)}"}

