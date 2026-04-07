import os
from typing import Annotated
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.checkpoint.memory import MemorySaver
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage
from tools import search_flights, search_hotels, calculate_budget
from dotenv import load_dotenv

# Tải các biến môi trường từ file .env (ở đây là lấy khóa OPENAI_API_KEY)
load_dotenv()

# ============================================================================
# 1. Đọc System Prompt
# Đọc nội dung hướng dẫn chi tiết (vai trò, luật lệ, quy trình) từ file text
# để nạp vào não của Agent, giúp Agent không đi chệch hướng theo đúng ReAct format.
# ============================================================================
with open("system_prompt.txt", "r", encoding="utf-8") as f:
    SYSTEM_PROMPT = f.read()


# ============================================================================
# 2. Khai báo State (Trạng thái của Graph)
# LangGraph hoạt động dựa trên biểu đồ trạng thái (StateGraph).
# State ở đây chứa 'messages' đóng vai trò như bộ nhớ lịch sử hội thoại.
# Annotated kết hợp với add_messages (reducer) giúp Langchain hiểu rằng khi có 
# chuỗi tin nhắn mới thì hãy nối (append) vào đuôi mảng thay vì ghi đè mảng cũ.
# ============================================================================
class AgentState(TypedDict):
    messages: Annotated[list, add_messages]


# ============================================================================
# 3. Khởi tạo LLM và Tools
# Bọc 3 công cụ tự viết ở bài trước thành một mảng (List).
# Sau đó khởi tạo mô hình GPT-4o-mini và gắn chóp (bind) các công cụ này vào mỏ neo.
# Giờ đây mô hình `llm_with_tools` đã biết được chữ ký (chi tiết hàm) để chủ động xài.
# ============================================================================
tools_list = [search_flights, search_hotels, calculate_budget]
llm = ChatOpenAI(model="gpt-4o-mini")
llm_with_tools = llm.bind_tools(tools_list)


# ============================================================================
# 4. Agent Node (Nút AI Xử lý / Bộ Lập Luận)
# Đây là cục logic chính của Agent. Mỗi lần luồng chạy Graph điều hướng tới Nút này:
# - Nó bốc lịch sử chat ('messages') ra từ state hiện tại.
# - Nó kiểm tra xem ở vị trí số 0 đã có System Prompt chưa? Nếu chưa thì nhồi vào đầu chuỗi.
# - Gửi toàn bộ vào LLM để lấy phản hồi về (Là yêu cầu gọi Tool hay văn bản trực tiếp).
# ============================================================================
def agent_node(state: AgentState):
    messages = state["messages"]
    
    # Đảm bảo luồng hướng dẫn hệ thống luôn tồn tại trước tiên cho mỗi vòng lặp Chat
    if not isinstance(messages[0], SystemMessage):
        messages = [SystemMessage(content=SYSTEM_PROMPT)] + messages
        
    response = llm_with_tools.invoke(messages)
    
    # === THÊM LOGGING ĐỂ DỄ QUAN SÁT ===
    # In ra dòng thông báo để sinh viên trực quan biết Agent đang "nghĩ" ra hành động gì.
    if response.tool_calls:
        for tc in response.tool_calls:
            print(f" -> Gọi tool: {tc['name']}({tc['args']})")
    else:
        print(f" -> Trả lời trực tiếp")
        
    # Trả về kết quả sẽ được add_messages tự động nối vào mảng thay vì đè dữ liệu.
    return {"messages": [response]}


# ============================================================================
# 5. Xây dựng Graph (Luồng Thực thi / Sơ đồ kết nối)
# Khai báo biểu đồ StateGraph khởi tạo với cấu trúc AgentState vừa định nghĩa
# ============================================================================
builder = StateGraph(AgentState)

# === ĐỊNH NGHĨA CÁC NÚT (NODES) ===
# Thêm 2 Nút cơ bản của hệ thống: 1 nút là NÃO (agent), 1 nút là CHÂN TAY (tools)
builder.add_node("agent", agent_node)

tool_node = ToolNode(tools_list)
builder.add_node("tools", tool_node)

# === KHAI BÁO CÁC MŨI TÊN ĐIỀU HƯỚNG (EDGES) - PHẦN TODO CỦA SINH VIÊN ===

# Đường 1: Khi khởi động (START), Graph lập tức đổ dữ liệu thẳng vào 'agent' để AI xử lý trước
builder.add_edge(START, "agent")

# Đường 2: Dòng Logic Điều Kiện (Conditional Edge) - Bộ phận Phân Nhánh
# Khi Nút 'agent' làm xong việc, `tools_condition` sẽ kiểm tra Output từ Agent:
#   - Trường hợp A: Output chứa yêu cầu gọi Tool => Lái mũi tên sang Nút "tools".
#   - Trường hợp B: Output chỉ có chữ (không gọi hàm) => Lái mũi tên đi ra Cửa Cuốn (END) ngầm định.
builder.add_conditional_edges("agent", tools_condition)

# Đường 3: Mũi Nối Khép Vòng Lặp (The Reasoning Loop)
# Sau khi Nút 'tools' thức thi việc tra cứu (ví dụ ra giá vé),
# Cạnh này bắt buộc điều hướng dữ liệu quay ngược trở lại cái đầu 'agent'. 
# Nhờ thế Agent có số dư/giá phòng thực để đọc và tính toán nước đi kế tiếp.
builder.add_edge("tools", "agent")

# Đóng gói và build Graph ra bộ máy xử lý, kèm theo bộ nhớ (Memory)
memory = MemorySaver()
graph = builder.compile(checkpointer=memory)


# ============================================================================
# 6. Chat loop (Vòng lặp CMD tương tác người dùng)
# Giao diện REPL (Read-Eval-Print Loop) đơn giản trên terminal dùng để test Agent.
# ============================================================================
if __name__ == "__main__":
    print("=" * 60)
    print("TravelBuddy - Trợ lý Du lịch Thông minh")
    print("   Gõ 'quit' để thoát")
    print("=" * 60)
    
    while True:
        user_input = input("\nBạn: ").strip()
        if user_input.lower() in ("quit", "exit", "q"):
            break
            
        print("\nTravelBuddy đang suy nghĩ...")
        # Sử dụng thread_id để xác định "phiên" nhắn tin nào cần được nhớ
        config = {"configurable": {"thread_id": "phiên_nhắn_tin_số_1"}}
        
        # graph.invoke là chìa khóa khởi động cổ máy: 
        #   Gửi nội dung đầu vào dán nhãn "human" cùng với cấu hình nhớ
        result = graph.invoke({"messages": [("human", user_input)]}, config)
        
        # Lấy Item cuối cùng nằm trong list Message History làm phản hồi đẩy ra ngoài
        final = result["messages"][-1]
        print(f"\nTravelBuddy:\n{final.content}")
