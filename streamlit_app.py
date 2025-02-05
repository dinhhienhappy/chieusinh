import streamlit as st
from openai import OpenAI
import os

# Đọc tất cả nội dung từ các file trong thư mục và nối chúng lại.
def rfiles_from_folder(folder_path):
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

# Đọc nội dung từ một file cụ thể
def rfile(name_file):
    try:
        with open(name_file, "r", encoding="utf-8") as file:
            return file.read()
    except FileNotFoundError:
        return ""

# Hiển thị logo và tiêu đề
try:
    col1, col2, col3 = st.columns([3, 2, 3])
    with col2:
        st.image("logo.png", use_container_width=True)  # Thay use_column_width bằng use_container_width
except:
    pass

# Tùy chỉnh nội dung tiêu đề
title_content = rfile("00.xinchao.txt")

# Hiển thị tiêu đề với nội dung tùy chỉnh
st.markdown(
    f"""
    <h1 style="text-align: center; font-size: 24px;">{title_content}</h1>
    """,
    unsafe_allow_html=True
)

# Lấy OpenAI API key từ `st.secrets`
openai_api_key = st.secrets.get("OPENAI_API_KEY")

# Tạo OpenAI client
client = OpenAI(api_key=openai_api_key)

# Khởi tạo lời nhắn "system" để định hình hành vi mô hình

INITIAL_SYSTEM_MESSAGE = {
    "role": "system",
    "content": f"""
    Bạn là một trợ lý AI chuyên cung cấp thông tin về các khóa học và tài liệu trong lĩnh vực [Tên lĩnh vực của bạn]. 
    Dưới đây là thông tin chi tiết về các chủ đề trong lĩnh vực này:
    
    {rfiles_from_folder("training_data")}  # Đọc tất cả dữ liệu từ thư mục training_data
    """
}


# Khởi tạo lời nhắn ví dụ từ vai trò "assistant"
INITIAL_ASSISTANT_MESSAGE = {
    "role": "assistant",
    "content": rfile("02.assistant.txt"),
}

# Tạo một biến trạng thái session để lưu trữ các tin nhắn nếu chưa tồn tại
if "messages" not in st.session_state:
    st.session_state.messages = [INITIAL_SYSTEM_MESSAGE, INITIAL_ASSISTANT_MESSAGE]

# Loại bỏ INITIAL_SYSTEM_MESSAGE khỏi giao diện hiển thị
for message in st.session_state.messages:
    if message["role"] != "system":
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

# Tạo ô nhập liệu cho người dùng
if prompt := st.chat_input("Bạn nhập nội dung cần trao đổi ở đây nhé?"):

    # Lưu trữ và hiển thị tin nhắn của người dùng
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Gọi API OpenAI để tạo phản hồi
    response = client.chat.completions.create(
        model=rfile("module_chatgpt.txt").strip(),
        messages=[{"role": m["role"], "content": m["content"]} for m in st.session_state.messages]
    )

    # Lấy nội dung phản hồi từ API
    response_content = response.choices[0].message.content  # Nội dung phản hồi

    # Hiển thị phản hồi từ trợ lý
    with st.chat_message("assistant"):
        st.markdown(response_content)

    # Lưu phản hồi vào session
    st.session_state.messages.append({"role": "assistant", "content": response_content})
