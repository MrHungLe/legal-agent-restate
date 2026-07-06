import os
from typing import Dict, Any
from langchain_neo4j import Neo4jGraph
from gemini_llm import get_embedding # Import hàm nhúng vector từ file gemini_llm

def query_graph_rag(query: str) -> Dict[str, Any]:
    """
    Kết nối đến Neo4j Aura và truy vấn GraphRAG bằng Vector Search.
    """
    uri = os.environ.get("NEO4J_URI")
    username = os.environ.get("NEO4J_USERNAME")
    password = os.environ.get("NEO4J_PASSWORD")
    
    if not uri or not username or not password:
        raise ValueError("Thông tin kết nối Neo4j chưa được cấu hình đầy đủ trong biến môi trường.")
        
    try:
        print(f"[GraphRAG] Khởi tạo kết nối Neo4j để tra cứu query: '{query}'")
        
        graph = Neo4jGraph(
            url=uri,
            username=username,
            password=password
        )
        
        # 1. Biến đổi câu hỏi thành Vector
        print("[GraphRAG] Đang tạo vector embedding cho câu hỏi...")
        query_embedding = get_embedding(query)
        
        # 2. Truy vấn Cypher sử dụng Vector Index (Giả sử index tên là 'legal_chunks')
        cypher_query = """
        CALL db.index.vector.queryNodes('legal_chunks', 3, $embedding)
        YIELD node, score
        RETURN node.text AS context, labels(node) AS type, node.id AS id, score
        """
        
        results = graph.query(cypher_query, params={"embedding": query_embedding})
        
        if not results:
             return {
                 "context": "Không tìm thấy thông tin cụ thể trong cơ sở dữ liệu pháp luật hiện tại. Vui lòng liên hệ trực tiếp với chuyên gia pháp lý.",
                 "sourceNodes": []
             }
             
        # Tổng hợp context từ kết quả
        context_lines = []
        source_nodes = []
        for res in results:
            if res.get('context'):
                # Kèm theo score để dễ debug độ chính xác
                score = round(res.get('score', 0), 4)
                context_lines.append(f"- (Độ tin cậy: {score}): {res.get('context')}")
            if res.get('id'):
                source_nodes.append(str(res.get('id')))
                
        return {
            "context": "\n".join(context_lines),
            "sourceNodes": source_nodes
        }
        
    except Exception as e:
        print(f"[GraphRAG Error] Lỗi khi lấy context từ Neo4j: {e}")
        raise Exception(f"Neo4j GraphRAG Error: {str(e)}")