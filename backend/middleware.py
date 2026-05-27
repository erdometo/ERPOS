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
from auth import current_user_role
from neo4j import GraphDatabase
from qdrant_client import QdrantClient
from qdrant_client.http import models as qdrant_models

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
            
            # Completely block destructive operations
            forbidden_keywords = ['DROP', 'DELETE', 'TRUNCATE', 'ALTER', 'CREATE', 'GRANT', 'REVOKE']
            upper_query = v.upper()
            for keyword in forbidden_keywords:
                if f" {keyword} " in upper_query or upper_query.startswith(f"{keyword} ") or f"\n{keyword} " in upper_query or upper_query.endswith(f" {keyword}"):
                    raise ValueError(f"FORBIDDEN KEYWORD DETECTED: {keyword}. Action execution blocked by middleware.")
            
            # Block system tables
            forbidden_tables = ['graph_nodes', 'graph_edges', 'vector_partitions', 'audit_ledger', 'sqlite_master', 'sqlite_sequence']
            lower_query = v.lower()
            for table in forbidden_tables:
                if table in lower_query:
                    raise ValueError(f"UNAUTHORIZED SYSTEM TABLE ACCESS: Attempted modification of system table '{table}' blocked.")
        return v


# ==================== 2. THE MULTI-MODEL MIDDLEWARE GATEWAY ====================
# ==================== NEO4J / QDRANT ADAPTERS ====================
class Neo4jGraphAdapter:
    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))
        # Verify connection
        with self.driver.session() as session:
            session.run("RETURN 1")

    def close(self):
        self.driver.close()

    def clear_all(self):
        with self.driver.session() as session:
            session.run("MATCH (n:GraphNode) DETACH DELETE n")

    def is_empty(self) -> bool:
        with self.driver.session() as session:
            result = session.run("MATCH (n:GraphNode) RETURN count(n) AS c")
            record = result.single()
            return record["c"] == 0 if record else True

    def node_exists(self, node_id: int) -> bool:
        with self.driver.session() as session:
            result = session.run("MATCH (n:GraphNode {id: $id}) RETURN n.id LIMIT 1", id=node_id)
            return result.single() is not None

    def get_node_name_by_id(self, node_id: int) -> str:
        with self.driver.session() as session:
            result = session.run("MATCH (n:GraphNode {id: $id}) RETURN n.name AS name LIMIT 1", id=node_id)
            record = result.single()
            return record["name"] if record else None

    def get_node_id_by_name(self, name: str) -> int:
        with self.driver.session() as session:
            res = session.run("MATCH (n:GraphNode {name: $name}) RETURN n.id AS id LIMIT 1", name=name)
            record = res.single()
            return record["id"] if record else None

    def create_or_update_node(self, node_id, label, name, description, skill_markdown, properties):
        label_capitalized = label.strip().capitalize()
        if label_capitalized not in ["Workflow", "Regulation", "Agent"]:
            label_capitalized = "Workflow"
            
        with self.driver.session() as session:
            # Check if exists by name
            res = session.run("MATCH (n:GraphNode {name: $name}) RETURN n.id AS id", name=name)
            record = res.single()
            if record:
                exist_id = record["id"]
                session.run(f"""
                    MATCH (n:GraphNode {{id: $id}})
                    REMOVE n:Workflow REMOVE n:Regulation REMOVE n:Agent
                    SET n:{label_capitalized}
                    SET n.label = $label, n.description = $description, n.skill_markdown = $skill_markdown, n.properties = $properties
                """, id=exist_id, label=label, description=description, skill_markdown=skill_markdown, properties=properties)
                return exist_id, f"Graph Node '{name}' (ID {exist_id}) evolved successfully."
            else:
                if node_id is None:
                    res_max = session.run("MATCH (n:GraphNode) RETURN max(n.id) AS max_id")
                    rec_max = res_max.single()
                    max_id = rec_max["max_id"] if rec_max and rec_max["max_id"] is not None else 0
                    node_id = max_id + 1
                
                session.run(f"""
                    CREATE (n:GraphNode:{label_capitalized} {{
                        id: $id,
                        name: $name,
                        label: $label,
                        description: $description,
                        skill_markdown: $skill_markdown,
                        properties: $properties
                    }})
                """, id=node_id, name=name, label=label, description=description, skill_markdown=skill_markdown, properties=properties)
                return node_id, f"Created new Graph Node '{name}' (ID {node_id}) successfully."

    def create_edge(self, source_id, target_id, edge_type, properties="{}"):
        edge_type_sanitized = edge_type.strip().upper()
        if not edge_type_sanitized.isalnum():
            edge_type_sanitized = "GOVERNS"
            
        with self.driver.session() as session:
            res = session.run("""
                MATCH (source:GraphNode {id: $source_id})-[r]-(target:GraphNode {id: $target_id})
                RETURN r
            """, source_id=source_id, target_id=target_id)
            if res.single() is None:
                session.run(f"""
                    MATCH (source:GraphNode {{id: $source_id}})
                    MATCH (target:GraphNode {{id: $target_id}})
                    CREATE (source)-[r:{edge_type_sanitized} {{properties: $properties}}]->(target)
                """, source_id=source_id, target_id=target_id, properties=properties)

    def traverse_graph(self, start_node_name: str) -> list:
        with self.driver.session() as session:
            query = """
            MATCH (n1:GraphNode {name: $name})-[r]->(n2:GraphNode)
            RETURN n2.id AS target_id, n2.name AS target_name, n2.label AS target_label, n2.description AS target_desc, type(r) AS edge_type
            UNION
            MATCH (n2:GraphNode)-[r]->(n1:GraphNode {name: $name})
            RETURN n2.id AS target_id, n2.name AS target_name, n2.label AS target_label, n2.description AS target_desc, type(r) AS edge_type
            """
            result = session.run(query, name=start_node_name)
            return [dict(record) for record in result]

    def get_all_nodes_with_edges(self) -> list:
        nodes_list = []
        with self.driver.session() as session:
            res_nodes = session.run("MATCH (n:GraphNode) RETURN n.id AS id, n.name AS name, n.label AS label, n.description AS description ORDER BY n.id ASC")
            for record in res_nodes:
                node_id = record["id"]
                name = record["name"]
                label = record["label"]
                description = record["description"]
                
                res_edges = session.run("""
                    MATCH (n:GraphNode {id: $nid})-[r]->(target:GraphNode)
                    RETURN target.name AS name, type(r) AS edge_type
                """, nid=node_id)
                edges = [dict(r) for r in res_edges]
                nodes_list.append({
                    "id": node_id,
                    "name": name,
                    "label": label,
                    "description": description,
                    "edges": edges
                })
        return nodes_list


class JSONGraphAdapter:
    def __init__(self, filepath):
        self.filepath = filepath
        if not os.path.exists(self.filepath):
            self._save_graph({"nodes": [], "edges": []})

    def _load_graph(self):
        try:
            with open(self.filepath, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {"nodes": [], "edges": []}

    def _save_graph(self, data):
        with open(self.filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def clear_all(self):
        self._save_graph({"nodes": [], "edges": []})

    def is_empty(self) -> bool:
        data = self._load_graph()
        return len(data.get("nodes", [])) == 0

    def node_exists(self, node_id: int) -> bool:
        data = self._load_graph()
        return any(n["id"] == node_id for n in data.get("nodes", []))

    def get_node_name_by_id(self, node_id: int) -> str:
        data = self._load_graph()
        for n in data.get("nodes", []):
            if n["id"] == node_id:
                return n["name"]
        return None

    def get_node_id_by_name(self, name: str) -> int:
        data = self._load_graph()
        for n in data.get("nodes", []):
            if n["name"] == name:
                return n["id"]
        return None

    def create_or_update_node(self, node_id, label, name, description, skill_markdown, properties):
        data = self._load_graph()
        nodes = data.setdefault("nodes", [])
        
        existing_node = None
        for n in nodes:
            if n["name"] == name:
                existing_node = n
                break
                
        if existing_node:
            existing_node["label"] = label.lower()
            existing_node["description"] = description
            existing_node["skill_markdown"] = skill_markdown
            existing_node["properties"] = properties
            self._save_graph(data)
            return existing_node["id"], f"Graph Node '{name}' (ID {existing_node['id']}) evolved successfully."
        else:
            if node_id is None:
                node_id = max([n["id"] for n in nodes]) + 1 if nodes else 1
            new_node = {
                "id": node_id,
                "name": name,
                "label": label.lower(),
                "description": description,
                "skill_markdown": skill_markdown,
                "properties": properties
            }
            nodes.append(new_node)
            self._save_graph(data)
            return node_id, f"Created new Graph Node '{name}' (ID {node_id}) successfully."

    def create_edge(self, source_id, target_id, edge_type, properties="{}"):
        data = self._load_graph()
        edges = data.setdefault("edges", [])
        
        exists = False
        for e in edges:
            s_id = e["source_id"]
            t_id = e["target_id"]
            if (s_id == source_id and t_id == target_id) or (s_id == target_id and t_id == source_id):
                exists = True
                break
                
        if not exists:
            edges.append({
                "source_id": source_id,
                "target_id": target_id,
                "edge_type": edge_type.strip().upper(),
                "properties": properties
            })
            self._save_graph(data)

    def traverse_graph(self, start_node_name: str) -> list:
        data = self._load_graph()
        nodes = data.get("nodes", [])
        edges = data.get("edges", [])
        
        start_node = None
        for n in nodes:
            if n["name"] == start_node_name:
                start_node = n
                break
                
        if not start_node:
            return []
            
        nid = start_node["id"]
        results = []
        for e in edges:
            target_id = None
            if e["source_id"] == nid:
                target_id = e["target_id"]
            elif e["target_id"] == nid:
                target_id = e["source_id"]
                
            if target_id is not None:
                t_node = None
                for n in nodes:
                    if n["id"] == target_id:
                        t_node = n
                        break
                if t_node:
                    results.append({
                        "target_id": t_node["id"],
                        "target_name": t_node["name"],
                        "target_label": t_node["label"],
                        "target_desc": t_node["description"],
                        "edge_type": e["edge_type"]
                    })
        return results

    def get_all_nodes_with_edges(self) -> list:
        data = self._load_graph()
        nodes = sorted(data.get("nodes", []), key=lambda x: x["id"])
        edges = data.get("edges", [])
        
        nodes_list = []
        for n in nodes:
            nid = n["id"]
            node_edges = []
            for e in edges:
                if e["source_id"] == nid:
                    t_name = None
                    for tn in nodes:
                        if tn["id"] == e["target_id"]:
                            t_name = tn["name"]
                            break
                    if t_name:
                        node_edges.append({
                            "name": t_name,
                            "edge_type": e["edge_type"]
                        })
            nodes_list.append({
                "id": nid,
                "name": n["name"],
                "label": n["label"],
                "description": n["description"],
                "edges": node_edges
            })
        return nodes_list


class QdrantVectorAdapter:
    def __init__(self, current_dir):
        self.current_dir = current_dir

    def _get_client(self):
        qdrant_host = os.getenv("QDRANT_HOST")
        qdrant_port = os.getenv("QDRANT_PORT")
        qdrant_api_key = os.getenv("QDRANT_API_KEY")
        
        client = None
        if qdrant_host:
            try:
                port = int(qdrant_port) if qdrant_port else 6333
                print(f"Connecting to Qdrant server at {qdrant_host}:{port}...")
                client = QdrantClient(host=qdrant_host, port=port, api_key=qdrant_api_key, timeout=5)
                client.get_collections()
                print("Successfully connected to Qdrant server.")
            except Exception as e:
                print(f"Failed to connect to Qdrant server: {e}. Falling back to local persistent Qdrant database.")
                client = None
                
        if not client:
            qdrant_db_path = os.path.join(self.current_dir, "qdrant_db")
            print(f"Initializing local persistent Qdrant client at {qdrant_db_path}...")
            client = QdrantClient(path=qdrant_db_path)
        return client

    def _ensure_collection(self, client, dim: int):
        collection_name = f"erp_vectors_{dim}"
        try:
            collections = client.get_collections().collections
            exists = any(c.name == collection_name for c in collections)
            if not exists:
                client.create_collection(
                    collection_name=collection_name,
                    vectors_config=qdrant_models.VectorParams(
                        size=dim,
                        distance=qdrant_models.Distance.COSINE
                    )
                )
                print(f"Created Qdrant collection '{collection_name}' with dimension {dim}.")
        except Exception as e:
            print(f"Error ensuring Qdrant collection {collection_name}: {e}")

    def clear_all(self):
        client = self._get_client()
        try:
            for dim in [3, 768]:
                collection_name = f"erp_vectors_{dim}"
                try:
                    client.delete_collection(collection_name=collection_name)
                except Exception:
                    pass
        finally:
            client.close()

    def is_empty(self) -> bool:
        client = self._get_client()
        try:
            for dim in [3, 768]:
                collection_name = f"erp_vectors_{dim}"
                try:
                    res = client.count(collection_name=collection_name)
                    if res.count > 0:
                        return False
                except Exception:
                    pass
            return True
        finally:
            client.close()

    def upsert_vector(self, node_id, source_type, text_content, vector):
        dim = len(vector)
        client = self._get_client()
        try:
            self._ensure_collection(client, dim)
            collection_name = f"erp_vectors_{dim}"
            
            import uuid
            point_id = str(uuid.uuid4())
            
            client.upsert(
                collection_name=collection_name,
                points=[
                    qdrant_models.PointStruct(
                        id=point_id,
                        vector=vector,
                        payload={
                            "node_id": int(node_id),
                            "source_type": source_type.lower(),
                            "text_content": text_content
                        }
                    )
                ]
            )
        finally:
            client.close()

    def search_vectors(self, query_vector, limit=2) -> list:
        dim = len(query_vector)
        client = self._get_client()
        try:
            self._ensure_collection(client, dim)
            collection_name = f"erp_vectors_{dim}"
            
            results = client.query_points(
                collection_name=collection_name,
                query=query_vector,
                limit=limit
            )
            matches = []
            for hit in results.points:
                payload = hit.payload or {}
                matches.append({
                    "source_type": payload.get("source_type"),
                    "node_id": payload.get("node_id"),
                    "text_content": payload.get("text_content"),
                    "similarity": round(hit.score, 4)
                })
            return matches
        except Exception as e:
            print(f"Qdrant search error: {e}")
            return []
        finally:
            client.close()

    def search_vectors_by_node(self, node_id: int, query_vector, limit=2) -> list:
        dim = len(query_vector)
        client = self._get_client()
        try:
            self._ensure_collection(client, dim)
            collection_name = f"erp_vectors_{dim}"
            
            filter_query = qdrant_models.Filter(
                must=[
                    qdrant_models.FieldCondition(
                        key="node_id",
                        match=qdrant_models.MatchValue(value=int(node_id))
                    )
                ]
            )
            results = client.query_points(
                collection_name=collection_name,
                query=query_vector,
                query_filter=filter_query,
                limit=limit
            )
            matches = []
            for hit in results.points:
                payload = hit.payload or {}
                matches.append({
                    "source_type": payload.get("source_type"),
                    "text_content": payload.get("text_content"),
                    "similarity": round(hit.score, 4)
                })
            return matches
        except Exception as e:
            print(f"Qdrant node search error: {e}")
            return []
        finally:
            client.close()

    def scroll_vectors(self, collection_name, limit=1000):
        client = self._get_client()
        try:
            res, _ = client.scroll(
                collection_name=collection_name,
                limit=limit,
                with_payload=True,
                with_vectors=False
            )
            return res
        except Exception:
            return []
        finally:
            client.close()


# ==================== 2. THE MULTI-MODEL MIDDLEWARE GATEWAY ====================
class ShieldGateway:
    def __init__(self, db_path=DB_FILE_PATH):
        self.db_path = db_path
        self.engine = create_engine(f"sqlite:///{db_path}")
        
        # Instantiate Graph adapter
        neo4j_uri = os.getenv("NEO4J_URI", "bolt://localhost:7687")
        neo4j_user = os.getenv("NEO4J_USER") or os.getenv("NEO4J_USERNAME") or "neo4j"
        neo4j_password = os.getenv("NEO4J_PASSWORD", "password")
        try:
            print(f"Connecting to Neo4j at {neo4j_uri}...")
            self.graph_adapter = Neo4jGraphAdapter(neo4j_uri, neo4j_user, neo4j_password)
            print("Successfully connected to Neo4j.")
        except Exception as e:
            print(f"Failed to connect to Neo4j: {e}. Falling back to local JSON graph database.")
            json_db_path = os.path.join(CURRENT_DIR, "graph_db.json")
            self.graph_adapter = JSONGraphAdapter(json_db_path)
            
        # Instantiate Vector adapter
        self.vector_adapter = QdrantVectorAdapter(CURRENT_DIR)
        
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
                
                nodes_res = conn.execute(text("SELECT id, label, name, description, skill_markdown, properties FROM graph_nodes;")).fetchall()
                if not nodes_res:
                    return
                    
                print("Graph store is empty, but SQLite contains nodes. Starting migration/synchronization...")
                
                for row in nodes_res:
                    node_id, label, name, description, skill_markdown, properties = row
                    self.graph_adapter.create_or_update_node(
                        node_id=node_id,
                        label=label,
                        name=name,
                        description=description,
                        skill_markdown=skill_markdown,
                        properties=properties
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
                    
                vectors_res = conn.execute(text("SELECT node_id, source_type, text_content, embedding FROM vector_partitions;")).fetchall()
                for row in vectors_res:
                    node_id, source_type, text_content, embedding_json = row
                    vector = json.loads(embedding_json)
                    self.vector_adapter.upsert_vector(
                        node_id=node_id,
                        source_type=source_type,
                        text_content=text_content,
                        vector=vector
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

    # --- AUDIT LEDGER HELPERS ---
    def log_audit_event(self, agent_name: str, action_type: str, action_details: str, governing_node_id: int = None):
        try:
            timestamp = datetime.utcnow().replace(microsecond=0)
            with self.engine.connect() as conn:
                # Get the last row's hash
                last_res = conn.execute(text("SELECT row_hash FROM audit_ledger ORDER BY id DESC LIMIT 1")).fetchone()
                prev_hash = last_res[0] if last_res else "0" * 64
                
                # Compute hash (robust formatting: replace space with T, strip microseconds)
                ts_str = timestamp.isoformat()
                if " " in ts_str:
                    ts_str = ts_str.replace(" ", "T")
                if "." in ts_str:
                    ts_str = ts_str.split(".")[0]
                
                data_str = f"{ts_str}|{agent_name}|{action_type}|{action_details}|{prev_hash}"
                row_hash = hashlib.sha256(data_str.encode("utf-8")).hexdigest()
                
                # Insert row
                ins_q = text("""
                    INSERT INTO audit_ledger (timestamp, agent_name, action_type, action_details, governing_node_id, prev_hash, row_hash)
                    VALUES (:timestamp, :agent_name, :action_type, :action_details, :governing_node_id, :prev_hash, :row_hash)
                """)
                conn.execute(ins_q, {
                    "timestamp": timestamp,
                    "agent_name": agent_name,
                    "action_type": action_type,
                    "action_details": action_details,
                    "governing_node_id": governing_node_id,
                    "prev_hash": prev_hash,
                    "row_hash": row_hash
                })
                conn.commit()
            return {"status": "success", "row_hash": row_hash}
        except Exception as e:
            print(f"Failed to log audit event: {e}")
            return {"error": str(e)}

    def verify_ledger_integrity(self) -> list:
        tampered_indices = []
        try:
            with self.engine.connect() as conn:
                result = conn.execute(text("SELECT id, timestamp, agent_name, action_type, action_details, prev_hash, row_hash FROM audit_ledger ORDER BY id ASC"))
                rows = result.fetchall()
                
                expected_prev_hash = "0" * 64
                for row in rows:
                    row_id, timestamp, agent_name, action_type, action_details, prev_hash, row_hash = row
                    
                    # Robust format conversion (replace space with T, strip microseconds)
                    ts_str = str(timestamp)
                    if " " in ts_str:
                        ts_str = ts_str.replace(" ", "T")
                    if "." in ts_str:
                        ts_str = ts_str.split(".")[0]
                    
                    # Recompute hash
                    data_str = f"{ts_str}|{agent_name}|{action_type}|{action_details}|{prev_hash}"
                    computed_hash = hashlib.sha256(data_str.encode("utf-8")).hexdigest()
                    
                    # Verify block linkage
                    if prev_hash != expected_prev_hash:
                        tampered_indices.append(row_id)
                    # Verify block content integrity
                    elif row_hash != computed_hash:
                        tampered_indices.append(row_id)
                        
                    expected_prev_hash = row_hash
        except Exception as e:
            print(f"Ledger verification error: {e}")
        return tampered_indices

    # --- GENERALIZED MUTATION ACTION ENGINE ---
    def execute_action_mutation(self, sql_query_str: str, params: dict = None, agent_name: str = "Autonomous Kernel Agent", governing_node_id: int = None):
        try:
            # Enforce Authorization: Only Admins and Employees can execute write actions
            print(f"DEBUG middleware: id(current_user_role)={id(current_user_role)}, current_user_role.get()={current_user_role.get()}")
            role = current_user_role.get()
            if role == "customer":
                raise PermissionError("UNAUTHORIZED ACTION: Customers are not permitted to execute write actions.")
            elif role is None:
                raise PermissionError("UNAUTHORIZED ACTION: Unauthenticated users are not permitted to execute write actions.")

            if params is None:
                params = {}
            # Validate query and parameters using GeneralizedActionMutation
            validated = GeneralizedActionMutation(query=sql_query_str.strip(), params=params)
            
            with self.engine.connect() as conn:
                conn.execute(text(validated.query), validated.params)
                conn.commit()
            
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
            self.sync_from_sqlite_if_needed()
            return self.graph_adapter.traverse_graph(start_node_name)
        except Exception as e:
            return {"error": f"Graph Traversal Error: {str(e)}"}

    # --- C. VECTOR GATEWAY (Global Semantic Search) ---
    def vector_search(self, query_text: str, limit=2):
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

            return self.vector_adapter.search_vectors(query_vector, limit=limit)
        except Exception as e:
            return {"error": f"Vector Search Error: {str(e)}"}

    # --- D. LOCALIZED VECTOR GATEWAY (Node-Level Semantic Search) ---
    def node_vector_search(self, node_id: int, query_text: str, limit=2):
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

            return self.vector_adapter.search_vectors_by_node(node_id, query_vector, limit=limit)
        except Exception as e:
            return {"error": f"Node Vector Search Error: {str(e)}"}

    # --- E. EVOLUTIONARY DBA MUTATION GATEWAY ---
    def execute_ddl(self, ddl_sql: str, agent_name: str = "Autonomous Kernel Agent", governing_node_id: int = None):
        try:
            # Enforce Authorization: Only Admins can evolve the database schema
            role = current_user_role.get()
            if role != "admin":
                raise PermissionError("UNAUTHORIZED DDL OPERATION: Only administrators are permitted to evolve the database schema.")

            validated = DBASchemaMutation(query=ddl_sql.strip())
            with self.engine.connect() as conn:
                conn.execute(text(validated.query))
                conn.commit()
            
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
    def get_schema_info(self) -> str:
        try:
            self.sync_from_sqlite_if_needed()
            
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
                nodes = self.graph_adapter.get_all_nodes_with_edges()
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

                # 3. Vector Partitions
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
    def execute_graph_mutation(self, label: str, name: str, description: str, skill_markdown: str, properties: str = "{}", target_edges: list = None, agent_name: str = "Autonomous Kernel Agent", governing_node_id: int = None):
        try:
            # Enforce Authorization: Only Admins can evolve the graph schema
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
    def execute_vector_mutation(self, node_id: int, source_type: str, text_content: str, agent_name: str = "Autonomous Kernel Agent", governing_node_id: int = None):
        try:
            # Enforce Authorization: Only Admins can evolve vector context
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

