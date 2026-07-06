import restate
from typing import Dict, Any

from graphrag import query_graph_rag
from gemini_llm import generate_legal_answer

legal_agent_service = restate.Service("LegalAgent")

@legal_agent_service.handler()
async def ask_legal_question(ctx: restate.Context, req: Dict[str, Any]) -> Dict[str, Any]:
    # Restate truyền body JSON trực tiếp vào req
    question = req.get("question", "") if isinstance(req, dict) else str(req)

    print(f"\n{'='*60}")
    print(f"🚀 [Restate Service] >>> BẮT ĐẦU NHẬN REQUEST MỚI <<<")
    print(f"📥 Câu hỏi từ Client: '{question}'")
    print(f"{'='*60}")

    if not question:
        raise restate.TerminalError("Câu hỏi không được để trống.")

    # --- Bước 1: Query GraphRAG (dùng nested function thay vì lambda) ---
    print("\n⏳ [Restate Service] Đang kích hoạt bước 'query-graphrag'...")

    # Capture question vào local var để tránh closure issue
    _question = question

    async def run_graphrag() -> Dict[str, Any]:
        return query_graph_rag(_question)

    try:
        rag_response = await ctx.run("query-graphrag", run_graphrag)
    except Exception as e:
        # TerminalError = Restate KHÔNG retry, trả lỗi về client ngay
        raise restate.TerminalError(f"Fatal GraphRAG Error: {str(e)}")

    print(f"✅ [LegalAgent] Retrieved context from GraphRAG.")

    # --- Bước 2: Gọi Gemini LLM ---
    print("\n⏳ [Restate Service] Đang kích hoạt bước 'generate-gemini-answer'...")

    _context = rag_response.get("context", "")
    _sources = rag_response.get("sourceNodes", [])

    async def run_gemini() -> str:
        return generate_legal_answer(_question, _context)

    try:
        answer = await ctx.run("generate-gemini-answer", run_gemini)
    except Exception as e:
        raise restate.TerminalError(f"Fatal Gemini Error: {str(e)}")

    print(f"✅ [LegalAgent] Generated answer from Gemini.")

    return {
        "question": question,
        "answer": answer,
        "sources": _sources,
    }