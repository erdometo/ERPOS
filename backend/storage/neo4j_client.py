import re
from auth import current_user_role
from neo4j import GraphDatabase

ROLE_CLEARANCES = {
    "admin": 3,
    "employee": 2,
    "customer": 1
}

def inject_cypher_clearance(query: str, role: str) -> str:
    """
    Middleware that automatically appends structural security constraints
    (WHERE node.clearance_level <= user_clearance) to generated Cypher queries.
    """
    clearance = ROLE_CLEARANCES.get(role, 0)
    
    # 1. Regex to match node pattern bindings e.g. (n:GraphNode), (node:Regulation)
    # Match match patterns: MATCH (n:GraphNode) or (n:Workflow)
    pattern = re.compile(r"\((?P<var>\w+):(?:GraphNode|Workflow|Regulation)\)", re.IGNORECASE)
    
    matches = list(pattern.finditer(query))
    if not matches:
        return query

    # Iterate backwards to preserve indexes while rewriting
    modified_query = query
    for m in reversed(matches):
        var_name = m.group("var")
        end_pos = m.end()
        
        # Check if WHERE exists in the immediate vicinity
        snippet_after = modified_query[end_pos:end_pos+40].upper()
        if "WHERE" in snippet_after:
            # We append to the existing WHERE clause
            # Find the WHERE index
            where_idx = end_pos + snippet_after.index("WHERE") + 5
            modified_query = (
                modified_query[:where_idx] +
                f" {var_name}.clearance_level <= {clearance} AND " +
                modified_query[where_idx:]
            )
        else:
            # Inject a brand new WHERE clause
            modified_query = (
                modified_query[:end_pos] +
                f" WHERE {var_name}.clearance_level <= {clearance} " +
                modified_query[end_pos:]
            )
            
    return modified_query

class Neo4jGraphAdapter:
    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))
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

    def create_or_update_node(self, node_id, label, name, description, skill_markdown, properties, clearance_level=1):
        label_capitalized = label.strip().capitalize()
        if label_capitalized not in ["Workflow", "Regulation", "Agent"]:
            label_capitalized = "Workflow"
            
        with self.driver.session() as session:
            res = session.run("MATCH (n:GraphNode {name: $name}) RETURN n.id AS id", name=name)
            record = res.single()
            if record:
                exist_id = record["id"]
                session.run(f"""
                    MATCH (n:GraphNode {{id: $id}})
                    REMOVE n:Workflow REMOVE n:Regulation REMOVE n:Agent
                    SET n:{label_capitalized}
                    SET n.label = $label, n.description = $description, n.skill_markdown = $skill_markdown, n.properties = $properties, n.clearance_level = $clearance
                """, id=exist_id, label=label, description=description, skill_markdown=skill_markdown, properties=properties, clearance=clearance_level)
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
                        properties: $properties,
                        clearance_level: $clearance
                    }})
                """, id=node_id, name=name, label=label, description=description, skill_markdown=skill_markdown, properties=properties, clearance=clearance_level)
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

    def traverse_graph(self, start_node_name: str, role: str = None) -> list:
        if role is None:
            role = current_user_role.get() or "customer"
        clearance = ROLE_CLEARANCES.get(role, 1)
        
        with self.driver.session() as session:
            query = """
            MATCH (n1:GraphNode {name: $name})-[r]->(n2:GraphNode)
            WHERE n2.clearance_level <= $clearance AND n1.clearance_level <= $clearance
            RETURN n2.id AS target_id, n2.name AS target_name, n2.label AS target_label, n2.description AS target_desc, type(r) AS edge_type
            UNION
            MATCH (n2:GraphNode)-[r]->(n1:GraphNode {name: $name})
            WHERE n2.clearance_level <= $clearance AND n1.clearance_level <= $clearance
            RETURN n2.id AS target_id, n2.name AS target_name, n2.label AS target_label, n2.description AS target_desc, type(r) AS edge_type
            """
            result = session.run(query, name=start_node_name, clearance=clearance)
            return [dict(record) for record in result]

    def get_all_nodes_with_edges(self, role: str = None) -> list:
        if role is None:
            role = current_user_role.get() or "customer"
        clearance = ROLE_CLEARANCES.get(role, 1)
        nodes_list = []
        with self.driver.session() as session:
            res_nodes = session.run("""
                MATCH (n:GraphNode) 
                WHERE n.clearance_level <= $clearance
                RETURN n.id AS id, n.name AS name, n.label AS label, n.description AS description ORDER BY n.id ASC
            """, clearance=clearance)
            for record in res_nodes:
                node_id = record["id"]
                name = record["name"]
                label = record["label"]
                description = record["description"]
                
                res_edges = session.run("""
                    MATCH (n:GraphNode {id: $nid})-[r]->(target:GraphNode)
                    WHERE target.clearance_level <= $clearance
                    RETURN target.name AS name, type(r) AS edge_type
                """, nid=node_id, clearance=clearance)
                edges = [dict(r) for r in res_edges]
                nodes_list.append({
                    "id": node_id,
                    "name": name,
                    "label": label,
                    "description": description,
                    "edges": edges
                })
        return nodes_list

