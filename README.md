# ✈️ TravelBuddy - Trợ Lý Du Lịch Thông Minh (ReAct Agent)

Chào mừng bạn đến với repo của **TravelBuddy**! Đây là bài Lab 4 xây dựng mạng lưới Agent sử dụng bộ công cụ **LangChain & LangGraph**. Nhiệm vụ của Agent là mô phỏng quá trình thao tác với hệ thống đặt vé, qua đó tính toán ngân sách và gợi ý khách sạn tự động một cách cực kỳ rành mạch dựa trên dữ liệu thật thay vì dự đoán lung tung (hallucination).

## 🌟 Điểm Nổi Bật Của Cấu Trúc Agent
- **Sử Dụng Trí Nhớ Phiên (Checkpointer):** Sử dụng `MemorySaver` của LangGraph để ghi nhận đầy đủ luồng context của người dùng. Tránh tình trạng cá vàng hỏi tới hỏi lui.
- **Suy luận Chuỗi Đa Bước (Multi-step Tool Chaining):** Sở hữu tư duy toán học tự động. Ví dụ khi lập hóa đơn trọn gói: Lấy giá vé từ DB (Tool 1) ➡️ Nhẩm lại tiền dư chia cho số ngày (Tool 2) ➡️ Dùng số tiền dư đó làm mức trần chốt phòng (Tool 3) ➡️ Quét hệ thống xuất hóa đơn cuối tổng kết (Tool 4).
- **Trực quan UI Bóc Tách Suy Nghĩ:** Chuyển đổi mã JSON thô kệch thành các Component Expander mượt mà của Streamlit để Giám khảo nhìn thấu đáo các tham số gọi hàm mà Agent xử lý trong nền.

---

## 🛠️ Hướng Dẫn Thiết Lập (Installation)

**1. Khởi tạo & Kích hoạt Môi trường Ảo (Khuyên dùng)**
```bash
python3 -m venv venv
source venv/bin/activate
```

**2. Cài đặt các thư viện lõi**
```bash
pip install langchain langchain-openai langgraph python-dotenv streamlit
```

**3. Cấu hình Khóa API**
Tạo file `.env` ở thư mục gốc để chứa API Key của nhà phát triển OpenAI cho tác vụ LLM nhúng:
```env
OPENAI_API_KEY=sk-xxxx...xxxx
```

---

## 🚀 Hướng Dẫn Chạy & Chấm Điểm Bài Lab

**Chúng tôi hỗ trợ 2 môi trường phục vụ việc giám định hệ thống:**

### Phương thức 1: Sử Dụng Web App Chấm Điểm Qua Giao Diện (Đề xuất)
Đây là màn hình giao diện tuyệt đẹp thiết kế riêng, có sẵn cấu hình sẵn 5 nút **Test Cases** để thao tác thuận tiện bằng 1 cú click!
- Ở terminal, gõ lệnh dưới đây:
```bash
streamlit run app.py
```
- App tự động mở trình duyệt ở liên kết: `http://localhost:8501`. 
- Bấm vào menu trái để duyệt các case giả lập hoặc chat trực tiếp, bên dưới sẽ phơi bày lịch sử `💭 AI đang tư duy tool...` rất thú vị. 
*(Tips: Mỗi khi chấm sang Test Case khác bạn nên bấm Xóa Lịch sử bộ nhớ nhé!)*

### Phương thức 2: Kích hoạt Terminal Truyền Thống
Để debug dạng luồng log console, chạy lệnh:
```bash
python agent.py
```

---

## 🧪 5 Test Case Tiêu Biểu Để Tra Tấn (Đã Pass 100%)

Nếu bạn Chat tự do, hãy thử áp dụng nguyên văn 5 kịch bản sau để kiểm chứng bộ khiên (Guardrail) của chúng tôi:
- **Test 1 (Check Missing Data):** *"Xin chào! Tôi đang muốn đi du lịch nhưng chưa biết đi đâu."* ➡️ Agent tự phân tích yêu cầu thiếu và hỏi thăm người dùng chắt lọc 4 thông tin cốt lõi ban đầu.
- **Test 2 (Chỉ Lấy Dữ Liệu Đơn Nhanh):** *"Tìm giúp tôi chuyến bay từ Hà Nội đi Đà Nẵng"* ➡️ Trả ngay thông tin chuyến bay, hiểu được user không cần thiết phải lập kế hoạch dài nên sẽ chặn lại việc hỏi budget dài dòng như robot.
- **Test 3 (Vận Hành Logic Chaining Đa Cú Pháp - Cực Khó):** *"Tôi ở Hà Nội, muốn đi Phú Quốc 2 đêm, budget 5 triệu. Tư vấn giúp!"* ➡️ Quan sát màn hình bật Tung 4 Tool đan chéo vào nhau từ Máy bay đến Tính Toán -> Khách hạn. Vượt qua xuất sắc!
- **Test 4 (Dịch vụ đặc thù thiếu thông tin):** *"Tôi muốn đặt khách sạn"* ➡️ Biết gác lại câu hỏi không cần thiết về vé máy bay, chỉ truy ra yếu tố thành phố/max_budget để test booking. 
- **Test 5 (Kiểm thử Hacker Xâm Nhập - Defense):** *"Giải giúp tôi bài tập lập trình Python về linked list"* ➡️ Agent thông minh xù lông từ chối nhã nhặn vì nằm ngòa vai trò Travel Assistant. 

Chúc bạn có một buổi trải nghiệm Test đầy mãn nhãn cùng TravelBuddy! 🌴
# day04_2A202600303
