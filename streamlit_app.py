import streamlit as st
from openai import OpenAI
import os

# Hàm đọc nội dung từ tất cả file trong thư mục
def rfiles_from_folder(folder_path):
    """ Đọc tất cả nội dung từ các file trong thư mục và nối chúng lại. """
    content = []
    try:
        for filename in sorted(os.listdir(folder_path)):  # Sắp xếp để đọc theo thứ tự
            file_path = os.path.join(folder_path, filename)
            if os.path.isfile(file_path):  # Chỉ đọc file, bỏ qua thư mục con
                with open(file_path, "r", encoding="utf-8") as file:
                    content.append(file.read())
    except Exception as e:
        print(f"Lỗi khi đọc folder {folder_path}: {e}")
    return "\n\n".join(content)  # Ghép nội dung với khoảng cách giữa các file

# Hàm đọc nội dung từ một file cụ thể
def rfile(name_file):
    try:
        with open(name_file, "r", encoding="utf-8") as file:
            return file.read()
    except FileNotFoundError:
        return ""

# Hiển thị logo trên giao diện
try:
    col1, col2, col3 = st.columns([3, 2, 3])
    with col2:
        st.image("logo.png", use_container_width=True)  
except:
    pass

# **Hiển thị nội dung từ `02.assistant.txt` với font nhỏ hơn**
assistant_content = rfile("02.assistant.txt")
st.markdown(f"""
    <h5 style="text-align: center;">{assistant_content}</h5>
    """, unsafe_allow_html=True)

# **Hộp chọn chủ đề**
selected_topic = st.selectbox(
    "🔍 Chọn lĩnh vực bạn quan tâm:",
    ["Y tế", "Môi trường", "AI", "Quản trị, kinh doanh"]
)

# **Mapping chủ đề với thư mục dữ liệu**
topic_folder_mapping = {
    
    "Y tế": "training_data/healthcare",
    "Môi trường": "training_data/environment",
    "AI": "training_data/ai",
    "Quản trị, kinh doanh": "training_data/qtkd",
}

# **Chọn thư mục huấn luyện tương ứng**
selected_folder = topic_folder_mapping.get(selected_topic, "training_data/misc")

# **Lấy OpenAI API key**
openai_api_key = st.secrets.get("OPENAI_API_KEY")

# **Tạo OpenAI client**
client = OpenAI(api_key=openai_api_key)

# **Tạo tin nhắn hệ thống dựa trên chủ đề đã chọn**
INITIAL_SYSTEM_MESSAGE = {
    "role": "system",
    "content": rfiles_from_folder(selected_folder)
}

# **Lưu tin nhắn vào session nếu chưa có**
if "messages" not in st.session_state:
    st.session_state.messages = [INITIAL_SYSTEM_MESSAGE]
else:
    # Cập nhật dữ liệu huấn luyện nếu người dùng đổi chủ đề
    st.session_state.messages[0] = INITIAL_SYSTEM_MESSAGE

# **Hiển thị lịch sử chat (bỏ qua system message)**
for message in st.session_state.messages:
    if message["role"] != "system":
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

# **Ô nhập liệu cho người dùng**
if prompt := st.chat_input("💬 Nhập nội dung cần trao đổi tại đây..."):

    # **Lưu trữ và hiển thị tin nhắn người dùng**
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # **Gọi OpenAI API để lấy phản hồi**
    response_content = ""
    with st.chat_message("assistant"):
        message_placeholder = st.empty()  # Tạo placeholder để cập nhật nội dung dần
        try:
            stream = client.chat.completions.create(
                model=rfile("module_chatgpt.txt").strip(),
                messages=[{"role": m["role"], "content": m["content"]} for m in st.session_state.messages]
            )
            
            # Lấy nội dung phản hồi
            response_content = stream.choices[0].message.content
            message_placeholder.markdown(response_content)

        except Exception as e:
            response_content = "❌ Đã xảy ra lỗi khi kết nối API!"
            message_placeholder.markdown(response_content)

    # **Lưu phản hồi vào session**
    st.session_state.messages.append({"role": "assistant", "content": response_content})
