🤖 LINE Bot to Google Drive
โปรเจกต์นี้คือ LINE Bot ที่ทำหน้าที่เป็นผู้ช่วยส่วนตัวในการจัดเก็บไฟล์ โดยจะบันทึกรูปภาพ, วิดีโอ, เสียง, และไฟล์ต่างๆ ที่ถูกส่งเข้ามาในแชท ไปยัง Google Drive ของคุณโดยอัตโนมัติ พร้อมทั้งสร้างโฟลเดอร์แยกตามแชท (ทั้งแชทส่วนตัวและแชทกลุ่ม) เพื่อความเป็นระเบียบและง่ายต่อการค้นหา

✨ คุณสมบัติ (Features)
บันทึกไฟล์อัตโนมัติ: จัดเก็บ รูปภาพ (.jpg), วิดีโอ (.mp4), เสียง (.m4a), และไฟล์ทั่วไปที่ส่งผ่าน LINE

จัดระเบียบอัตโนมัติ: สร้างโฟลเดอร์ใน Google Drive แยกตาม ID ของผู้ใช้ (userId) หรือ ID ของกลุ่ม (groupId) ไฟล์จากต่างแชทจะไม่ปะปนกัน

ตอบกลับการทำงาน: บอทจะส่งข้อความยืนยันกลับไปยังแชทเมื่อบันทึกไฟล์สำเร็จ

ติดตั้งและใช้งานง่าย: พัฒนาด้วย Python (Flask) และสามารถนำไป deploy ใช้งานจริงบนแพลตฟอร์มอย่าง Render ได้

🛠️ สิ่งที่ต้องเตรียมก่อนติดตั้ง (Prerequisites)
ก่อนจะเริ่ม คุณต้องเตรียมข้อมูลสำคัญ 4 อย่างนี้ให้พร้อม:

LINE Channel Access Token: จาก LINE Developers Console

LINE Channel Secret: จาก LINE Developers Console

Google Drive Parent Folder ID: ID ของโฟลเดอร์หลักใน Google Drive ที่คุณต้องการให้บอทเก็บไฟล์ (ดูวิธีหาจาก URL ของโฟลเดอร์)

ไฟล์ credentials.json: ไฟล์ Service Account Key จาก Google Cloud Console ที่ได้เปิดใช้งาน Google Drive API แล้ว

สำคัญ: ต้องนำอีเมลของ Service Account (อยู่ในไฟล์ credentials.json) ไปกด "Share" และให้สิทธิ์ Editor ในโฟลเดอร์หลักบน Google Drive ด้วย

⚙️ การติดตั้งและตั้งค่า (Setup)
Clone Repository (ถ้ามี):

Bash
git clone <your-repository-url>
cd line-gdrive-bot
สร้างไฟล์ credentials.json:
นำไฟล์ credentials.json ที่ดาวน์โหลดจาก Google Cloud มาวางไว้ในโฟลเดอร์โปรเจกต์

สร้างไฟล์ .env:
สร้างไฟล์ชื่อ .env ในโฟลเดอร์หลัก แล้วใส่ข้อมูลของคุณลงไป:

Ini, TOML
LINE_CHANNEL_ACCESS_TOKEN=YOUR_CHANNEL_ACCESS_TOKEN
LINE_CHANNEL_SECRET=YOUR_CHANNEL_SECRET
GOOGLE_DRIVE_PARENT_FOLDER_ID=YOUR_PARENT_FOLDER_ID
ติดตั้ง Dependencies:
แนะนำให้สร้าง Virtual Environment ก่อน จากนั้นรันคำสั่ง:

Bash
pip install -r requirements.txt
🚀 การทดสอบในเครื่อง (Local Testing)
เนื่องจาก LINE ต้องส่งข้อมูลมายัง URL ที่เป็นสาธารณะ (Public URL) เราจึงต้องใช้ ngrok เพื่อทดสอบจากเครื่องของเรา

รันแอป Flask:

Bash
flask run
แอปจะรันที่ http://127.0.0.1:5000

รัน ngrok:
เปิด Terminal อีกหน้าต่าง แล้วรันคำสั่ง:

Bash
ngrok http 5000
ngrok จะแสดง Forwarding URL ขึ้นมา (เช่น https://xxxxxxxx.ngrok-free.app)

ตั้งค่า Webhook URL:
คัดลอก URL จาก ngrok แล้วนำไปต่อท้ายด้วย /callback จากนั้นนำไปใส่ในช่อง Webhook URL บนหน้าตั้งค่าของ LINE Developers Console

ตัวอย่าง: https://xxxxxxxx.ngrok-free.app/callback

อย่าลืมกด Verify และเปิดใช้งาน Use webhook

ทดสอบ: ลองเชิญบอทเข้ากลุ่มหรือส่งไฟล์ในแชทส่วนตัว แล้วดูผลลัพธ์ใน Google Drive

☁️ การนำขึ้นใช้งานจริง (Deployment)
เมื่อทดสอบเรียบร้อยแล้ว ให้นำแอปพลิเคชันขึ้นไปรันบน Hosting Service เช่น Render.com เพื่อให้บอททำงานตลอด 24 ชั่วโมง

เชื่อมต่อ Repository: นำโค้ดของคุณขึ้น GitHub และเชื่อมต่อกับ Render

ตั้งค่าบน Render:

Build Command: pip install -r requirements.txt

Start Command: gunicorn app:app

Environment Variables: ไปที่หน้า Environment แล้วตั้งค่า LINE_CHANNEL_ACCESS_TOKEN, LINE_CHANNEL_SECRET, GOOGLE_DRIVE_PARENT_FOLDER_ID และเพิ่ม credentials.json เป็น Secret File

อัปเดต Webhook: นำ URL จริงที่ได้จาก Render (เช่น https://your-bot.onrender.com) ไปใส่ใน LINE Developers Console แทนที่ URL ของ ngrok

📁 โครงสร้างไฟล์ (File Structure)
/line-gdrive-bot
├── app.py             # โค้ดหลักของ Flask Application และ Logic ของบอท
├── requirements.txt   # รายการ Python libraries ที่ต้องใช้
├── credentials.json   # (ต้องสร้างเอง) Key สำหรับเชื่อมต่อ Google Drive API
├── .env               # (ต้องสร้างเอง) ไฟล์เก็บข้อมูลลับ เช่น Access Tokens
└── .gitignore  