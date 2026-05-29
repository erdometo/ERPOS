import os
from dotenv import load_dotenv
from auth import current_user_role
from qdrant_client import QdrantClient
from qdrant_client.http import models as qdrant_models

ROLE_CLEARANCES = {
    "admin": 3,
    "employee": 2,
    "customer": 1
}

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

    def upsert_vector(self, node_id, source_type, text_content, vector, clearance_level=1):
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
                            "text_content": text_content,
                            "clearance_level": int(clearance_level)
                        }
                    )
                ]
            )
        finally:
            client.close()

    def search_vectors(self, query_vector, limit=2, role: str = None) -> list:
        dim = len(query_vector)
        client = self._get_client()
        if role is None:
            role = current_user_role.get() or "customer"
        clearance = ROLE_CLEARANCES.get(role, 1)
        
        try:
            self._ensure_collection(client, dim)
            collection_name = f"erp_vectors_{dim}"
            
            # Enforce security clearance filtering at query time
            filter_query = qdrant_models.Filter(
                must=[
                    qdrant_models.FieldCondition(
                        key="clearance_level",
                        range=qdrant_models.Range(lte=clearance)
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

    def search_vectors_by_node(self, node_id: int, query_vector, limit=2, role: str = None) -> list:
        dim = len(query_vector)
        client = self._get_client()
        if role is None:
            role = current_user_role.get() or "customer"
        clearance = ROLE_CLEARANCES.get(role, 1)
        
        try:
            self._ensure_collection(client, dim)
            collection_name = f"erp_vectors_{dim}"
            
            # Filter matches by node_id AND user clearance level
            filter_query = qdrant_models.Filter(
                must=[
                    qdrant_models.FieldCondition(
                        key="node_id",
                        match=qdrant_models.MatchValue(value=int(node_id))
                    ),
                    qdrant_models.FieldCondition(
                        key="clearance_level",
                        range=qdrant_models.Range(lte=clearance)
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
