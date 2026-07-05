from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import json
import os

app = FastAPI(title="Uni-Agent MSU Backend")

# 🔗 ปลดล็อกระบบรักษาความปลอดภัยของบราวเซอร์ (CORS) เพื่อให้หน้าบ้าน HTML เชื่อมต่อมายังหลังบ้านได้
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==============================================================================
# [ฟังก์ชัน BACKEND: โหลดข้อมูลจำลองสำเร็จรูปจากโฟลเดอร์ mock_data]
# ==============================================================================
def load_mock_data():
    try:
        with open(os.path.join("mock_data", "student_profiles.json"), "r", encoding="utf-8") as f:
            students = json.load(f)
        with open(os.path.join("mock_data", "msu_knowledge.json"), "r", encoding="utf-8") as f:
            knowledge = json.load(f)
        return students, knowledge
    except Exception:
        return {}, {}

STUDENT_DB, KNOWLEDGE_DB = load_mock_data()

# ==============================================================================
# [เส้นทาง API (Endpoint): จุดเชื่อมต่อรับคำถามจากหน้าบ้าน แล้วคิดคำตอบส่งกลับ]
# ==============================================================================
@app.get("/api/chat")
def chat_with_agent(student_id: str, question: str):
    q_clean = question.lower().strip()
    
    # 🛡️ เลเยอร์ความปลอดภัยขาเข้า (Input Guardrail) - บล็อกคำสั่งแฮก AI หรือทำลายระบบ
    dangerous_keywords = ["ลบข้อมูล", "แฮก", "drop table", "shutdown"]
    if any(keyword in q_clean for keyword in dangerous_keywords):
        return {"answer": "🛡️ [ระบบความปลอดภัยระงับคำสั่ง]: ตรวจพบคำสั่งไม่ปลอดภัยเพื่อพยายามโจมตีระบบฐานข้อมูลกลางของมหาวิทยาลัย!"}

    # 🧠 AI Agent Routing Logic (สมองกลแยกสายงานดึงข้อมูล)
    
    # สายงานที่ 1: ดึงข้อมูลส่วนตัวนิสิต (เกรด/ประวัติการเรียน)
    if "เกรด" in q_clean or "gpa" in q_clean or "เรียน" in q_clean:
        student = STUDENT_DB.get(student_id)
        if student:
            return {"answer": f"จากการตรวจสอบระบบทะเบียนอย่างปลอดภัย คุณคือ {student['name']} ปัจจุบันมีเกรดเฉลี่ยสะสมอยู่ที่ **{student['gpa']}** คณะ: {student['faculty']} (สถานะภาพนิสิต: {student['status']}) ครับ"}
        else:
            return {"answer": "ไม่พบรหัสนิสิตคนนี้ในระบบทะเบียนจำลองครับ (กรุณาทดลองใช้รหัส: 69102345)"}
            
    # สายงานที่ 2: ดึงข้อมูลความรู้ทั่วไป มมส (จำลองระเบียบการ / คลังความรู้ RAG)
    elif "ห้องสมุด" in q_clean or "วิทยบริการ" in q_clean:
        return {"answer": KNOWLEDGE_DB.get("ห้องสมุด", "ไม่พบข้อมูล")}
    elif "ทุน" in q_clean or "กยศ" in q_clean:
        return {"answer": KNOWLEDGE_DB.get("ทุนการศึกษา", "ไม่พบข้อมูล")}
    elif "รถราง" in q_clean or "รถเหลือง" in q_clean:
        return {"answer": KNOWLEDGE_DB.get("รถราง", "ไม่พบข้อมูล")}
        
    # สายงานที่ 3: กรณีถามเรื่องอื่นที่ AI ต้นแบบยังไม่รู้จัก
    else:
        return {"answer": "ขออภัยครับ คำถามนี้ไม่มีอยู่ในฐานข้อมูลทดสอบของ มมส ในปัจจุบัน นิสิตสามารถเพิ่มความรู้ใหม่ลงในไฟล์ json ฝั่งหลังบ้านได้ครับ"}

# คำสั่งรันระบบอัตโนมัติ (พิมพ์รันในคอมฯ)
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend:app", host="127.0.0.1", port=8000, reload=True)