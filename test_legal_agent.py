import requests
import json
import sys

URL = "http://localhost:8080/LegalAgent/ask_legal_question"
HEADERS = {"Content-Type": "application/json"}

def main():
    print("⚖️  Hệ thống Kiểm thử Legal Support Agent-Py (Restate)")
    print("Đang kết nối tới Restate Ingress tại http://localhost:8080...")
    print("Gõ 'exit' hoặc 'quit' để thoát chương trình.")
    print("-" * 60)

    # Thử kiểm tra xem Restate Server có hoạt động không
    try:
        requests.get("http://localhost:8080", timeout=2)
    except requests.exceptions.ConnectionError:
        print("\n❌ [Lỗi kết nối]: Không thể kết nối tới Restate Server (port 8080).")
        print("👉 Hãy chắc chắn rằng bạn đã khởi động Restate Server (ví dụ: `docker compose up -d restate-server`).")
        print("👉 Và đừng quên đăng ký deployment bằng cách gọi Admin API (port 9070).")
        print("-" * 60)

    while True:
        try:
            question = input("\nĐặt câu hỏi pháp lý: ")
            
            if question.lower() in ['exit', 'quit']:
                print("Tạm biệt!")
                break
            if not question.strip():
                continue
                
            print("⏳ Đang xử lý câu hỏi của bạn (tra cứu GraphRAG & Gemini)...")
            
            # Request body cho Restate handler ask_legal_question(ctx, question)
            # Theo Restate protocol, tham số được truyền trong JSON object tương tự như sau:
            # {"question": "nội dung câu hỏi"}
            payload = {"question": question}
            
            response = requests.post(URL, headers=HEADERS, json=payload)

            if response.status_code == 200:
                result = response.json()
                print("\n🤖 Trả lời từ Agent:")
                print(result.get("answer", "Không có câu trả lời."))
                
                sources = result.get("sources", [])
                if sources:
                    print("\n📚 Nguồn tham chiếu (Source Nodes):")
                    for idx, src in enumerate(sources, 1):
                        print(f"  {idx}. Node ID: {src}")
                else:
                    print("\n📚 Nguồn tham chiếu: Không tìm thấy nguồn cụ thể.")
            else:
                print(f"\n❌ [Lỗi Server {response.status_code}]: {response.text}")

        except KeyboardInterrupt:
            print("\nTạm biệt!")
            break
        except requests.exceptions.ConnectionError:
            print("\n❌ [Lỗi kết nối]: Mất kết nối tới Restate Server.")
            break
        except Exception as e:
            print(f"\n❌ Đã xảy ra lỗi ngoài ý muốn: {e}")

if __name__ == "__main__":
    main()
