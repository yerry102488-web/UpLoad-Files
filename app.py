import streamlit as st
import os
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload
import io

# ===============================
# ✅ 基本設定
# ===============================
st.set_page_config(page_title="☁️ 雲端檔案系統", layout="wide")

SCOPES = ['https://www.googleapis.com/auth/drive']
FOLDER_ID = "1I0GLgtYVR4uedDLss6qkT8RWy-451Mg1"   # 🔥 一定要改

# ===============================
# ✅ Google Drive 連線
# ===============================
@st.cache_resource
def get_drive_service():
    credentials = service_account.Credentials.from_service_account_file(
        "credentials.json", scopes=SCOPES
    )
    service = build('drive', 'v3', credentials=credentials)
    return service


# ===============================
# ✅ 上傳檔案
# ===============================
def upload_to_drive(uploaded_file):
    service = get_drive_service()

    file_metadata = {
        'name': uploaded_file.name,
        'parents': [FOLDER_ID]
    }

    # 使用記憶體（不用寫 temp 檔更安全）
    file_stream = io.BytesIO(uploaded_file.getbuffer())

    media = MediaIoBaseUpload(file_stream, resumable=True)

    file = service.files().create(
        body=file_metadata,
        media_body=media,
        fields='id'
    ).execute()

    return file.get("id")


# ===============================
# ✅ 取得檔案列表
# ===============================
def list_files():
    service = get_drive_service()

    query = f"'{FOLDER_ID}' in parents and trashed=false"

    results = service.files().list(
        q=query,
        fields="files(id, name, mimeType, size)"
    ).execute()

    return results.get("files", [])


# ===============================
# ✅ 刪除檔案
# ===============================
def delete_file(file_id):
    service = get_drive_service()
    service.files().delete(fileId=file_id).execute()


# ===============================
# ✅ UI
# ===============================
st.title("☁️ Google Drive 檔案系統")
st.caption("檔案會儲存在雲端（永久）✅")

# ===============================
# 📤 上傳
# ===============================
st.subheader("📤 上傳檔案")

uploaded_files = st.file_uploader(
    "選擇檔案（可多選）",
    accept_multiple_files=True
)

if uploaded_files:
    for file in uploaded_files:
        with st.spinner(f"上傳中：{file.name}..."):
            file_id = upload_to_drive(file)

        st.success(f"✅ 上傳成功：{file.name}")

        link = f"https://drive.google.com/file/d/{file_id}/view"
        st.write(f"🔗 {link}")

# ===============================
# 📁 檔案列表
# ===============================
st.divider()
st.subheader("📁 雲端檔案")

files = list_files()

if not files:
    st.info("目前沒有檔案")
else:
    for f in files:
        col1, col2, col3 = st.columns([4, 2, 1])

        file_name = f['name']
        file_id = f['id']
        file_size = int(f.get('size', 0)) / 1024 if f.get('size') else 0

        # ✅ 檔名
        with col1:
            st.write(f"📄 {file_name}")

        # ✅ 大小
        with col2:
            st.write(f"{file_size:.1f} KB")

        # ✅ 下載 + 刪除
        with col3:
            download_url = f"https://drive.google.com/uc?id={file_id}&export=download"
            st.link_button("⬇️", download_url)

            if st.button("🗑", key=file_id):
                delete_file(file_id)
                st.warning(f"已刪除 {file_name}")
                st.rerun()

# ===============================
# 🖼 圖片預覽
# ===============================
st.divider()
st.subheader("🖼 圖片預覽")

image_files = [
    f for f in files
    if "image" in f.get("mimeType", "")
]

if image_files:
    selected = st.selectbox(
        "選擇圖片",
        options=image_files,
        format_func=lambda x: x["name"]
    )

    img_url = f"https://drive.google.com/uc?id={selected['id']}"
    st.image(img_url)

else:
    st.write("沒有圖片可預覽")
