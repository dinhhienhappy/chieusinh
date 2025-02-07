import streamlit as st
from openai import OpenAI
import os

# Hàm đọc dữ liệu từ folder theo chủ đề
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

# Hàm đọc file đơn lẻ
def rfile(name_file):
    try:
        with open(name_file, "r", encoding="utf-8") as file:
            return file.read()
    except FileNotFoundError:
        return ""

# Hiển thị logo
try:
    col1, col2, col3 = st.columns([3, 2, 3])
    with col2:
        st.image("logo.png", use_container_width=True)
except:
    pass

# Tiêu đề chào mừng
title_content = rfile("00.xinchao.txt")
st.markdown(f"<h1 style='text-align: center; font-size: 24px;'>{title_content}</h1>", unsafe_allow_html=True)

# Lấy OpenAI API key từ `st.secrets`
openai_api_key = st.secrets.get("OPENAI_API_KEY")

# Tạo OpenAI client
client = OpenAI(api_key=openai_api_key)



# Tin nhắn khởi tạo cho assistant
INITIAL_ASSISTANT_MESSAGE = {
    "role": "assistant",
    "content": rfile("02.assistant.txt"),
}

# 📌 **Thêm menu chọn chủ đề**
topics = {
    "Tổng quan": "training_data/general",
    "Công nghệ AI": "training_data/ai",
    "Môi trường": "training_data/environment",
    "Y tế": "training_data/healthcare",
    "Quản trị, kinh doanh": "training_data/qtkd"
}

selected_topic = st.selectbox("📌 Chọn lĩnh vực mà bạn quan tâm:", list(topics.keys()))
selected_folder = topics[selected_topic]

# 🏋️ **Tải dữ liệu huấn luyện theo chủ đề**
INITIAL_SYSTEM_MESSAGE = {
    "role": "system",
    "content": rfiles_from_folder(selected_folder)  # Chỉ dùng dữ liệu của chủ đề đã chọn
}


# Khởi tạo session lưu tin nhắn
if "messages" not in st.session_state or st.session_state.get("last_selected_topic") != selected_topic:
    st.session_state.messages = [INITIAL_SYSTEM_MESSAGE, INITIAL_ASSISTANT_MESSAGE]
    st.session_state.last_selected_topic = selected_topic  # Lưu chủ đề đã chọn

# Hiển thị các tin nhắn cũ
for message in st.session_state.messages:
    if message["role"] != "system":
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

# Ô nhập liệu người dùng
if prompt := st.chat_input("Bạn nhập nội dung cần trao đổi ở đây nhé?"):

    # Lưu tin nhắn của người dùng
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Gọi OpenAI API
    response_content = ""
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        response = client.chat.completions.create(
            model=rfile("module_chatgpt.txt").strip(),
            messages=[{"role": m["role"], "content": m["content"]} for m in st.session_state.messages]
        )
        response_content = response.choices[0].message.content
        message_placeholder.markdown(response_content)

    # Lưu phản hồi vào session
    st.session_state.messages.append({"role": "assistant", "content": response_content})
