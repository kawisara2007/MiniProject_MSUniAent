from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import json
import os

app = FastAPI(title="Uni-Agent MSU High-Stability Backend")

# ปลดล็อกระบบรักษาความปลอดภัยเพื่อให้ Frontend HTML คุยกับ Backend ได้
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==============================================================================
# [ส่วนดึงข้อมูล: ดึงข้อมูลจากไฟล์ JSON ได้จริง ๆ และอัปเดตได้เรียลไทม์]
# ==============================================================================
def load_mock_data():
    try:
        # วิ่งไปอ่านไฟล์ในโฟลเดอร์ mock_data สดๆ ทุกครั้งที่มีนิสิตพิมพ์ข้อความถาม
        with open(os.path.join("mock_data", "student_profiles.json"), "r", encoding="utf-8") as f:
            students = json.load(f)
        with open(os.path.join("mock_data", "msu_knowledge.json"), "r", encoding="utf-8") as f:
            knowledge = json.load(f)
        return students, knowledge
    except Exception:
        return {}, {}

# ==============================================================================
# [ส่วนควบคุมการตัดสินใจประมวลผลคำตอบ]
# ==============================================================================
@app.get("/api/chat")
def chat_with_agent(student_id: str, question: str):
    student_db, knowledge_db = load_mock_data()
    q_clean = question.lower().strip()
    
    # 🛡️ เลเยอร์ความปลอดภัยขาเข้า (Input Guardrail)
    dangerous_keywords = ["ลบข้อมูลมหาลัย", "แฮก", "drop table", "shutdown"]
    if any(keyword in q_clean for keyword in dangerous_keywords):
        return {"answer": "🛡️ [ระบบความปลอดภัย]: พฤติกรรมเสี่ยงต่อการโจมตีระบบฐานข้อมูลกลาง การทำงานถูกระงับ!"}

    # ค้นหาประวัตินิสิตตามรหัสที่ส่งมาจากหน้าบ้านล่าสุด
    current_student = student_db.get(student_id)

    # 🧠 สมองกล Agent ดึงข้อมูลแบบตรงเงื่อนไขและชาญฉลาด
    
    # สายคำถามที่ 1: ค้นหาเรื่องเกรด / GPA / ประวัติการเรียนส่วนตัว
    if "เกรด" in q_clean or "gpa" in q_clean or "คะแนน" in q_clean or "ประวัติ" in q_clean or "คะแนนสะสม" in q_clean:
        if current_student:
            return {
                "answer": f"MSU : สวัสดีครับคุณ **{current_student['name']}** คณะ **{current_student['faculty']}** คับ จากการตรวจสอบข้อมูลทะเบียนล่าสุด เกรดเฉลี่ยสะสม (GPAX) ปัจจุบันของคุณคือ **{current_student['gpa']}** (สถานภาพนิสิต: {current_student['status']}) ครับ!"
            }
        else:
            return {"answer": f"MSU : ปัจจุบันคุณล็อกอินด้วยรหัสนิสิต `{student_id}` ซึ่งไม่พบในระบบฐานข้อมูลทะเบียนจำลองครับ (แนะนำให้ทดลองกดเข้าสู่ระบบด้วยรหัส: `69102345` หรือ `69109999` ดูนะครับ)"}

    # สายคำถามที่ 2: ดึงข้อมูลระเบียบการจากไฟล์ msu_knowledge.json ตาม Keyword
    elif "ห้องสมุด" in q_clean or "วิทยบริการ" in q_clean or "สมุด" in q_clean:
        info = knowledge_db.get("ห้องสมุด", "ไม่มีข้อมูลในระบบ")
        return {"answer": f"MSU : ตรวจสอบข้อมูลสำนักวิทยบริการ มมส ให้เรียบร้อยแล้วครับ: {info}"}

    elif "ทุน" in q_clean or "กยศ" in q_clean or "เงินกู้" in q_clean:
        info = knowledge_db.get("ทุนการศึกษา", "ไม่มีข้อมูลในระบบ")
        return {"answer": f"MSU : ข้อมูลเรื่องทุนการศึกษาของทางมหาวิทยาลัยคับ: {info}"}

    elif "รถราง" in q_clean or "รถเหลือง" in q_clean or "รถม่วง" in q_clean:
        info = knowledge_db.get("รถราง", "ไม่มีข้อมูลในระบบ")
        return {"answer": f"MSU: แผนเส้นทางบริการเดินรถรางภายใน มมส คับ: {info}"}

    # สายคำถามที่ 3: หากถามนอกเหนือเรื่องที่กำหนดไว้
    else:
        return {
            "answer": " MSU : ขออภัยครับ ปัจจุบันยังไม่มีข้อมูลเรื่องนี้ในคลังความรู้ต้นแบบ มมส ท่านสามารถเพิ่มหัวข้อข่าวสารนี้เข้าไปในไฟล์คลังข้อมูล `mock_data/msu_knowledge.json` ได้ตลอดเวลาเลยครับ คับ"
        }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend:app", host="127.0.0.1", port=8000, reload=True)