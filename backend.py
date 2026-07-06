from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import json
import os

app = FastAPI(title="Uni-Agent MSU High-Stability Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def load_mock_data():
    try:
        with open(os.path.join("mock_data", "student_profiles.json"), "r", encoding="utf-8") as f:
            students = json.load(f)
        with open(os.path.join("mock_data", "msu_knowledge.json"), "r", encoding="utf-8") as f:
            knowledge = json.load(f)
        return students, knowledge
    except Exception:
        return {}, {}

@app.get("/api/chat")
def chat_with_agent(student_id: str, question: str):
    student_db, knowledge_db = load_mock_data()
    q_clean = question.lower().strip()
    
    # 🛡️ Guardrail 1: คำสั่งอันตราย
    dangerous_keywords = ["ลบข้อมูลมหาลัย", "แฮก", "drop table", "shutdown"]
    if any(keyword in q_clean for keyword in dangerous_keywords):
        return {"answer": "ระบบความปลอดภัย: ตรวจพบพฤติกรรมเสี่ยง การทำงานถูกระงับครับ"}

    # 🛡️ Guardrail 2: ตรวจสอบการล็อกอินก่อนให้ข้อมูลส่วนตัว
    is_personal_query = any(k in q_clean for k in ["เกรด", "gpa", "คะแนน", "ประวัติ", "สะสม"])
    if is_personal_query:
        if not student_id or student_id == "GUEST":
            return {"answer": "แจ้งเตือน: คุณยังไม่ได้เข้าสู่ระบบครับ รบกวนกดปุ่ม 'เข้าสู่ระบบทะเบียน มมส' ด้านบนก่อน เพื่อให้ผมดึงข้อมูลส่วนตัวมาแสดงได้อย่างปลอดภัยครับ"}
        
        current_student = student_db.get(student_id)
        if current_student:
            return {
                "answer": f"สวัสดีครับคุณ {current_student['name']} คณะ{current_student['faculty']} จากการตรวจสอบข้อมูลทะเบียนล่าสุด เกรดเฉลี่ยสะสมปัจจุบันของคุณคือ {current_student['gpa']} (สถานภาพ: {current_student['status']}) ครับ"
            }
        else:
            return {"answer": f"ไม่พบรหัสนิสิต {student_id} ในระบบฐานข้อมูลครับ"}

    # 🧠 สายคำถามที่ 2: ข้อมูลทั่วไป (ตอบได้แม้ไม่ล็อกอิน)
    if "ห้องสมุด" in q_clean or "วิทยบริการ" in q_clean or "สมุด" in q_clean:
        info = knowledge_db.get("ห้องสมุด", "ไม่มีข้อมูลในระบบ")
        return {"answer": f"ข้อมูลสำนักวิทยบริการ มมส: {info}"}

    elif "ทุน" in q_clean or "กยศ" in q_clean or "เงินกู้" in q_clean:
        info = knowledge_db.get("ทุนการศึกษา", "ไม่มีข้อมูลในระบบ")
        return {"answer": f"ข้อมูลเรื่องทุนการศึกษา: {info}"}

    elif "รถราง" in q_clean or "รถเหลือง" in q_clean or "รถม่วง" in q_clean:
        info = knowledge_db.get("รถราง", "ไม่มีข้อมูลในระบบ")
        return {"answer": f"เส้นทางบริการเดินรถภายใน มมส: {info}"}

    else:
        return {
            "answer": "ขออภัยครับ ปัจจุบันยังไม่มีข้อมูลเรื่องนี้ในคลังความรู้ต้นแบบครับ"
        }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend:app", host="127.0.0.1", port=8000, reload=True)