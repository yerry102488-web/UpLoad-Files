import streamlit as st
import os

st.set_page_config(page_title="📂 檔案上傳系統", layout="wide")

st.title("📂 檔案上傳系統")
st.caption("上傳、管理、下載你的檔案 ✅")

UPLOAD_FOLDER = "uploads"

# ✅ 建立資料夾
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# =========================
# 📤 上傳檔案
# =========================
st.subheader("📤 上傳檔案")

uploaded_files = st.file_uploader(
    "選擇檔案（可多選）",
    accept_multiple_files=True
)

if uploaded_files:
    for uploaded_file in uploaded_files:
        file_path = os.path.join(UPLOAD_FOLDER, uploaded_file.name)

        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())

        st.success(f"✅ 已上傳：{uploaded_file.name}")

# =========================
# 📁 檔案列表
# =========================
st.divider()
st.subheader("📁 已上傳檔案")

files = os.listdir(UPLOAD_FOLDER)

if len(files) == 0:
    st.info("目前沒有檔案")
else:
    for file in files:
        file_path = os.path.join(UPLOAD_FOLDER, file)
        file_size = os.path.getsize(file_path) / 1024  # KB

        col1, col2, col3 = st.columns([4, 2, 1])

        # ✅ 檔名
        with col1:
            st.write(f"📄 {file}")

        # ✅ 檔案大小
        with col2:
            st.write(f"{file_size:.1f} KB")

        # ✅ 下載 + 刪除
        with col3:
            with open(file_path, "rb") as f:
                st.download_button(
                    label="⬇️",
                    data=f,
                    file_name=file,
                    key=f"download_{file}"
                )

            if st.button("🗑", key=f"delete_{file}"):
                os.remove(file_path)
                st.warning(f"已刪除 {file}")
                st.rerun()

# =========================
# 🖼 圖片預覽
# =========================
st.divider()
st.subheader("🖼 圖片預覽")

image_files = [
    f for f in files if f.lower().endswith(("png", "jpg", "jpeg"))
]

if image_files:
    selected_image = st.selectbox("選擇圖片", image_files)

    if selected_image:
        st.image(os.path.join(UPLOAD_FOLDER, selected_image))
else:
    st.write("沒有可預覽的圖片")