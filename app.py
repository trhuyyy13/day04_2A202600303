import streamlit as st
import uuid
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage

# Phải import graph từ file agent.py của bạn
from agent import graph

# ================================
# THIẾT LẬP GIAO DIỆN (UI CONFIG)
# ================================
st.set_page_config(
    page_title="TravelBuddy AI | Lab 4",
    page_icon="✈️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS để làm mượt giao diện (Dùng Vanilla CSS nhúng vào Streamlit)
st.markdown("""
<style>
    .main-header {
        font-size: 2.8rem;
        font-weight: 800;
        background: -webkit-linear-gradient(45deg, #1E3A8A, #3B82F6);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0px;
    }
    .sub-header {
        font-size: 1.1rem;
        color: #6B7280;
        margin-bottom: 2rem;
    }
    .tool-badge {
        background-color: #f3f4f6;
        color: #1f2937;
        font-family: monospace;
        padding: 2px 6px;
        border-radius: 4px;
        font-size: 0.85em;
    }
</style>
""", unsafe_allow_html=True)

# Khởi tạo ID phiên để lưu trí nhớ (Memory)
if "thread_id" not in st.session_state:
    st.session_state.thread_id = str(uuid.uuid4())

# Khởi tạo mảng lưu lịch sử hiển thị giao diện. Mỗi phần tử là dict chứa role và nội dung
if "messages" not in st.session_state:
    st.session_state.messages = []
    # Lời chào mặc định thiết kế sang trọng
    st.session_state.messages.append({
        "role": "assistant", 
        "content": "Xin chào! 👋 Mình là **TravelBuddy**. Mình được trang bị khả năng trực tiếp tra cứu chuyến bay và phòng khách sạn để thiết kế cho bạn một chuyến đi lý tưởng. Bạn muốn đi đâu hôm nay?",
        "avatar": "✈️"
    })

# ================================
# SIDEBAR: BẢNG ĐIỀU KHIỂN & CHẤM ĐIỂM
# ================================
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/2000/2000885.png", width=100) # Logo minh họa
    st.header("⚙️ Bảng Điều Khiển")
    
    # Hiển thị trạng thái ảo dạng component
    col1, col2 = st.columns(2)
    with col1:
        st.success("🟢 Online")
    with col2:
        st.info("🧠 GPT-4o-Mini")
        
    st.caption(f"Trạng thái ID Phiên: `{st.session_state.thread_id[:8]}...`")
    
    st.divider()
    
    # Danh sách Test Case biến thành Bộ Nút sang trọng
    st.subheader("🧪 Bộ Chọn Test Cases")
    st.caption("Dành cho ban giám khảo chấm điểm Lab:")
    
    TEST_CASES = {
        "1️⃣ General Inquiry": "Xin chào! Tôi đang muốn đi du lịch nhưng chưa biết đi đâu.",
        "2️⃣ Single Tool Call": "Tìm giúp tôi chuyến bay từ Hà Nội đi Đà Nẵng",
        "3️⃣ Multi-Step Chaining": "Tôi ở Hà Nội, muốn đi Phú Quốc 2 đêm, budget 5 triệu. Tư vấn giúp!",
        "4️⃣ Missing Information": "Tôi muốn đặt khách sạn",
        "5️⃣ Guardrail Defense": "Giải giúp tôi bài tập lập trình Python về linked list"
    }

    selected_test = None
    for test_name, test_query in TEST_CASES.items():
        if st.button(test_name, use_container_width=True):
            selected_test = test_query

    st.divider()
    # Nút Xóa có style màu đỏ nổi bật
    if st.button("🗑️ Xóa Cuộc Trò Chuyện (Reset Memory)", type="primary", use_container_width=True):
        st.session_state.messages = []
        st.session_state.thread_id = str(uuid.uuid4())
        st.rerun()

# ================================
# MAIN CHAT KHU VỰC CHÍNH
# ================================
st.markdown('<div class="main-header">✈️ TravelBuddy Agent</div>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">Hệ thống ReAct Agent đa bước tự động lên lịch trình du lịch cá nhân hóa.</p>', unsafe_allow_html=True)

# 1. Render lại lịch sử chat trước đó của UI
for msg in st.session_state.messages:
    if msg.get("is_tool"):
        # Nếu dòng đó là lịch sử Tool thì vẽ Expander
        with st.expander(f"🛠️ Agent đã truy cập CSDL: **{msg['tool_name']}**", expanded=False):
            st.json(msg["content"])
    else:
        # Chat thông thường
        with st.chat_message(msg["role"], avatar=msg.get("avatar")):
            st.markdown(msg["content"])

# 2. Xử lý logic gõ tay HOẶC bấm nút
prompt = st.chat_input("Nhập yêu cầu tư vấn du lịch tại đây...")

# Cập nhật giá trị nếu người dùng gõ tay hoặc bấm Test Case bên sidebar
active_prompt = selected_test if selected_test else prompt

if active_prompt:
    # --- UI Phần User ---
    with st.chat_message("user", avatar="🧑‍💻"):
        st.markdown(active_prompt)
    st.session_state.messages.append({"role": "user", "content": active_prompt, "avatar": "🧑‍💻"})
    
    # --- UI Phần AI ---
    with st.chat_message("assistant", avatar="✈️"):
        with st.spinner("🤖 TravelBuddy đang phân tích ngôn ngữ tự nhiên và hệ thống..."):
            
            # Khởi động Graph với ID Memory
            config = {"configurable": {"thread_id": st.session_state.thread_id}}
            result = graph.invoke({"messages": [("human", active_prompt)]}, config)
            
            # --- ĐÓN NHẬN DỮ LIỆU ĐỂ RENDER CHUỖI TOOl LÊN UI CHUYÊN NGHIỆP ---
            messages_list = result["messages"]
            
            # Cắt lấy đoạn hội thoại chỉ thuộc về tin nhắn mới nhất
            latest_human_idx = 0
            for i in range(len(messages_list)-1, -1, -1):
                if isinstance(messages_list[i], HumanMessage):
                    latest_human_idx = i
                    break
            
            new_messages = messages_list[latest_human_idx+1:]
            
            # Lặp qua tất cả bước suy nghĩ của hộp đen langgraph để in ra UI
            for n_msg in new_messages:
                
                # Nếu Langgraph đòi Tool -> Hiển thị trên UI thành Dropdown Expander
                if isinstance(n_msg, AIMessage) and n_msg.tool_calls:
                    for tc in n_msg.tool_calls:
                        with st.expander(f"🛠️ Suy nghĩ: Trích xuất **{tc['name']}**...", expanded=True):
                            st.json(tc['args']) # In ra thông số bóc tách dạng JSON mượt mắt
                            
                        # Lưu vào History để ko biến mất khi load page
                        st.session_state.messages.append({
                            "role": "assistant",
                            "is_tool": True,
                            "tool_name": tc['name'],
                            "content": tc['args']
                        })
                
                # Nếu là nội dung text chat thường
                elif isinstance(n_msg, AIMessage) and n_msg.content:
                    final_text = n_msg.content
                    st.markdown(final_text)
                    st.session_state.messages.append({
                        "role": "assistant", 
                        "content": final_text,
                        "avatar": "✈️"
                    })
