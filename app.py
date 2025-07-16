import os
import io
from datetime import datetime

from flask import Flask, request, abort
from dotenv import load_dotenv

# --- LINE SDK ---
from linebot.v3 import WebhookHandler
from linebot.v3.exceptions import InvalidSignatureError
from linebot.v3.messaging import Configuration, ApiClient, MessagingApi, ReplyMessageRequest, TextMessage
from linebot.v3.webhooks import MessageEvent, ImageMessageContent, VideoMessageContent, AudioMessageContent, FileMessageContent

# --- Google Drive API ---
import google.auth # <<< อัปเดต: ใช้ Library ใหม่
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload

# --- โหลด Environment Variables จากไฟล์ .env ---
load_dotenv()

# --- ตั้งค่า Configuration ---
app = Flask(__name__)

# ตั้งค่า LINE
configuration = Configuration(access_token=os.getenv('LINE_CHANNEL_ACCESS_TOKEN'))
handler = WebhookHandler(os.getenv('LINE_CHANNEL_SECRET'))

# ตั้งค่า Google Drive
SCOPES = ['https://www.googleapis.com/auth/drive']
PARENT_FOLDER_ID = os.getenv('GOOGLE_DRIVE_PARENT_FOLDER_ID')

# --- ฟังก์ชันสำหรับ Google Drive (อัปเดต) ---

def get_gdrive_service():
    """
    สร้าง Service object สำหรับเชื่อมต่อ Google Drive API
    โดยใช้ Default Credentials ที่ได้รับจาก Environment (เช่น Cloud Run)
    """
    # <<< อัปเดต: ส่วนนี้เปลี่ยนไปทั้งหมด ไม่มีการอ่านไฟล์ credentials.json
    creds, project = google.auth.default(scopes=SCOPES)
    return build('drive', 'v3', credentials=creds)

def find_or_create_folder(service, folder_name, parent_id):
    """ค้นหาโฟลเดอร์ด้วยชื่อ ถ้าไม่เจอก็สร้างใหม่ และคืนค่า Folder ID กลับไป"""
    query = f"name='{folder_name}' and mimeType='application/vnd.google-apps.folder' and '{parent_id}' in parents and trashed=false"
    results = service.files().list(q=query, spaces='drive', fields='files(id, name)').execute()
    items = results.get('files', [])

    if not items:
        # ไม่เจอโฟลเดอร์ สร้างใหม่
        file_metadata = {
            'name': folder_name,
            'mimeType': 'application/vnd.google-apps.folder',
            'parents': [parent_id]
        }
        folder = service.files().create(body=file_metadata, fields='id').execute()
        print(f"Created folder: {folder_name} with ID: {folder.get('id')}")
        return folder.get('id')
    else:
        # เจอโฟลเดอร์แล้ว
        print(f"Found existing folder: {items[0]['name']} with ID: {items[0]['id']}")
        return items[0]['id']

def upload_file_to_folder(service, file_data, file_name, folder_id):
    """อัปโหลดไฟล์ไปยังโฟลเดอร์ที่ระบุใน Google Drive"""
    file_metadata = {'name': file_name, 'parents': [folder_id]}
    media = MediaIoBaseUpload(io.BytesIO(file_data), mimetype='application/octet-stream', resumable=True)
    file = service.files().create(body=file_metadata, media_body=media, fields='id, name').execute()
    print(f"Uploaded file '{file.get('name')}' with ID: {file.get('id')}")
    return file

# --- ส่วนของ Webhook สำหรับ LINE ---

@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        app.logger.info("Invalid signature. Please check your channel access token/channel secret.")
        abort(400)
    return 'OK'

# --- จัดการข้อความที่เป็น รูปภาพ, วิดีโอ, เสียง, และไฟล์ ---
@handler.add(MessageEvent, message=(ImageMessageContent, VideoMessageContent, AudioMessageContent, FileMessageContent))
def handle_content_message(event):
    # ดึงข้อมูล Message Content จาก LINE
    with ApiClient(configuration) as api_client:
        line_bot_api = MessagingApi(api_client)
        message_content = line_bot_api.get_message_content(message_id=event.message.id)

        # กำหนดชื่อไฟล์และโฟลเดอร์
        source_id = event.source.user_id if event.source.type == 'user' else event.source.group_id if event.source.type == 'group' else 'unknown'
        
        # สร้างชื่อไฟล์ที่ไม่ซ้ำกัน
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_name_prefix = f"{timestamp}"

        if isinstance(event.message, FileMessageContent):
            file_name = f"{file_name_prefix}_{event.message.file_name}"
        elif isinstance(event.message, ImageMessageContent):
            file_name = f"{file_name_prefix}_image.jpg"
        elif isinstance(event.message, VideoMessageContent):
            file_name = f"{file_name_prefix}_video.mp4"
        elif isinstance(event.message, AudioMessageContent):
            file_name = f"{file_name_prefix}_audio.m4a"
        else:
            file_name = f"{file_name_prefix}_unknown_file"

        try:
            # เชื่อมต่อ Google Drive และอัปโหลด
            service = get_gdrive_service()
            target_folder_id = find_or_create_folder(service, source_id, PARENT_FOLDER_ID)
            upload_file_to_folder(service, message_content, file_name, target_folder_id)

            # ตอบกลับหาผู้ใช้ว่าสำเร็จ
            reply_text = f"บันทึกไฟล์ '{file_name}' สำเร็จ!"
            line_bot_api.reply_message_with_http_info(
                ReplyMessageRequest(
                    reply_token=event.reply_token,
                    messages=[TextMessage(text=reply_text)]
                )
            )
        except Exception as e:
            print(f"An error occurred: {e}")
            # ตอบกลับหาผู้ใช้ว่ามีปัญหา
            line_bot_api.reply_message_with_http_info(
                ReplyMessageRequest(
                    reply_token=event.reply_token,
                    messages=[TextMessage(text=f"เกิดข้อผิดพลาดในการบันทึกไฟล์: {e}")]
                )
            )


if __name__ == "__main__":
    app.run(port=int(os.environ.get("PORT", 8080)))