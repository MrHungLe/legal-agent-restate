import os
import google.generativeai as genai

def get_embedding(text: str) -> list[float]:
    """
    Tạo vector embedding cho văn bản bằng Gemini để dùng cho Vector Search.
    """
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY is not set")
    
    genai.configure(api_key=api_key)
    result = genai.embed_content(
        model="models/text-embedding-004",
        content=text,
        task_type="retrieval_document",
    )
    return result['embedding']

def generate_legal_answer(question: str, context: str) -> str:
    """
    Generate an answer using Google Gemini based on the provided context
    """
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key or api_key == "your_gemini_api_key_here":
        raise ValueError("GEMINI_API_KEY is not set in environment variables")

    try:
        genai.configure(api_key=api_key)
        
        system_instruction = """
        Bạn là một chuyên gia pháp lý am hiểu sâu sắc về hệ thống pháp luật Việt Nam.
        Nhiệm vụ của bạn là tư vấn và trả lời câu hỏi pháp lý của người dùng.

        Yêu cầu nghiêm ngặt:
        1. CHỈ sử dụng thông tin từ "Context" được cung cấp để trả lời.
        2. Nếu "Context" không có đủ thông tin, hãy trả lời rõ ràng là "Dựa trên dữ liệu hiện tại, tôi không đủ thông tin để trả lời chính xác, vui lòng tham khảo thêm chuyên gia."
        3. Không tự bịa đặt, suy đoán hoặc sử dụng kiến thức bên ngoài Context.
        4. Trả lời một cách chuyên nghiệp, dễ hiểu, trích dẫn rõ nguồn luật nếu có trong Context.
        """
        
        # ĐÃ SỬA LỖI MODEL TẠI ĐÂY
        model = genai.GenerativeModel(
            model_name="gemini-1.5-flash",
            system_instruction=system_instruction,
            generation_config=genai.GenerationConfig(
                temperature=0.2, 
            )
        )

        prompt = f"""
        [Context từ hệ thống tra cứu pháp luật (GraphRAG)]:
        {context}

        [Câu hỏi của người dùng]:
        {question}

        Câu trả lời của bạn:
        """

        response = model.generate_content(prompt)
        return response.text
        
    except Exception as e:
        print(f"[Gemini Error] Failed to generate answer: {e}")
        raise Exception(f"Gemini LLM Error: {str(e)}")