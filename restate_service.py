import restate
from datetime import timedelta
from typing import Dict, Any

from graphrag import query_graph_rag
from gemini_llm import generate_legal_answer

# Define the Restate service
legal_agent_service = restate.Service("LegalAgent")

@legal_agent_service.handler()
async def ask_legal_question(ctx: restate.Context, question: str) -> Dict[str, Any]:
    """
    Handler to ask a legal question
    
    Args:
        ctx: The Restate Context, used for durable execution
        question: The user's question
        
    Returns:
        Dictionary with question, answer and sources
    """
    print(f"[LegalAgent] Received question: {question}")

    # Bước 1: Nhận câu hỏi (đã có ở tham số `question`)

    # Bước 2: Query GraphRAG sử dụng ctx.run()
    # Việc bọc trong ctx.run() giúp đảm bảo kết quả lấy từ GraphRAG sẽ được persist
    # Nếu service bị crash sau bước này, Restate sẽ không gọi lại GraphRAG mà lấy từ journal
    # Restate python SDK uses ctx.run(name, lambda_func)
    
    rag_response = await ctx.run(
        "query-graphrag", 
        lambda: query_graph_rag(question)
    )

    print("[LegalAgent] Retrieved context from GraphRAG")

    # Bước 3: Gọi Gemini LLM sử dụng ctx.run()
    # Tương tự, gọi external API (Gemini) phải được bọc trong ctx.run()
    answer = await ctx.run(
        "generate-gemini-answer", 
        lambda: generate_legal_answer(question, rag_response["context"])
    )

    print("[LegalAgent] Generated answer from Gemini")

    # Bước 4: Trả về kết quả
    return {
        "question": question,
        "answer": answer,
        "sources": rag_response["sourceNodes"]
    }
