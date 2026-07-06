import restate
from datetime import timedelta
from typing import Dict, Any

from graphrag import query_graph_rag
from gemini_llm import generate_legal_answer

legal_agent_service = restate.Service("LegalAgent")

@legal_agent_service.handler()
async def ask_legal_question(ctx: restate.Context, question: str) -> Dict[str, Any]:
    print(f"[LegalAgent] Received question: {question}")
    print("\n" + "==================================================")
    print(f"🚀 [Restate Service] >>> BẮT ĐẦU NHẬN REQUEST MỚI <<<")
    print(f"📥 Câu hỏi từ Client: '{question}'")
    print("==================================================")
    # Bước 2: Query GraphRAG
    try:
        print("\n⏳ [Restate Service] Đang kích hoạt bước 'query-graphrag' qua Context.run()...")
        rag_response = await ctx.run(
            "query-graphrag", 
            lambda: query_graph_rag(question)
        )
    except Exception as e:
        # Nếu lỗi do code hoặc cấu hình Neo4j sai, ném TerminalError để dừng vòng lặp retry
        raise restate.TerminalError(f"Fatal GraphRAG Error: {str(e)}")

    print("[LegalAgent] Retrieved context from GraphRAG")

    # Bước 3: Gọi Gemini LLM
    try:
        answer = await ctx.run(
            "generate-gemini-answer", 
            lambda: generate_legal_answer(question, rag_response["context"])
        )
    except Exception as e:
        # Ném TerminalError để báo lỗi trực tiếp về client thay vì treo máy
        raise restate.TerminalError(f"Fatal Gemini Error: {str(e)}")

    print("[LegalAgent] Generated answer from Gemini")

    return {
        "question": question,
        "answer": answer,
        "sources": rag_response["sourceNodes"]
    }