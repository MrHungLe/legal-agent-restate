import os
from google import genai
from google.genai import types

def get_embedding(text: str) -> list[float]:
    """
    Tạo vector embedding cho văn bản bằng Gemini SDK mới (google-genai).
    """
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY is not set")
    
    # Khởi tạo client theo SDK mới
    client = genai.Client(api_key=api_key)
    
    result = client.models.embed_content(
        model="text-embedding-004",
        contents=text,
    )
    # SDK mới trả về object ContentEmbedding, truy cập qua .embedding.values
    return result.embedding.values
    print(f"✅ [get_embedding] OUTPUT - Tạo embedding thành công. Kích thước vector: {len(embedding_values)} | Xem trước 5 phần tử đầu: {embedding_values[:5]}...")
    return embedding_values

def generate_legal_answer(question: str, context: str) -> str:
    """
    Generate an answer using Google Gemini based on the provided context (google-genai SDK)
    """
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY is not set in environment variables")

    try:
        client = genai.Client(api_key=api_key)
        
        system_instruction = """
        Bạn là một chuyên gia pháp lý am hiểu sâu sắc về hệ thống pháp luật Việt Nam.
        Nhiệm vụ của bạn là tư vấn và trả lời câu hỏi pháp lý của người dùng.

        Yêu cầu nghiêm ngặt:
        1. CHỈ sử dụng thông tin từ "Context" được cung cấp để trả lời.
        2. Nếu "Context" không có đủ thông tin, hãy trả lời rõ ràng là "Dựa trên dữ liệu hiện tại, tôi không đủ thông tin để trả lời chính xác, vui lòng tham khảo thêm chuyên gia."
        3. Không tự bịa đặt, suy đoán hoặc sử dụng kiến thức bên ngoài Context.
        4. Trả lời một cách chuyên nghiệp, dễ hiểu, trích dẫn rõ nguồn luật nếu có trong Context.
        """
        
        prompt = f"""
        [Context từ hệ thống tra cứu pháp luật (GraphRAG)]:
        {context}

        [Câu hỏi của người dùng]:
        {question}

        Câu trả lời của bạn:
        """

        # Cú pháp cấu hình hệ thống và tạo nội dung mới
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
            config=types.GenerateContentConfig(
                system_instruction=system_instruction,
                temperature=0.2, 
            )
        )
        print(f"✅ [generate_legal_answer] OUTPUT - Kết quả từ Gemini:\n---\n{response.text}\n---")
        return response.text
        
    except Exception as e:
        print(f"[Gemini Error] Failed to generate answer: {e}")
        raise Exception(f"Gemini LLM Error: {str(e)}")