from fastapi import FastAPI, Depends, HTTPException, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from app import database, models
import uvicorn

# 1. เริ่มระบบฐานข้อมูล (Launch Sequence)
database.init_db()

# 2. สร้าง App Object (ศูนย์กลางการควบคุม)
app = FastAPI(title="Master Logistic - Mission Control")

# 3. ตั้งค่าระบบแสดงผลหน้าเว็บ
templates = Jinja2Templates(directory="templates")

# 4. ฟังก์ชันเชื่อมต่อฐานข้อมูล
def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- 🚀 MISSION CONTROL (หน้า Dashboard หลัก) ---
@app.get("/admin", response_class=HTMLResponse)
def admin_dashboard(request: Request, db: Session = Depends(get_db)):
    users = db.query(models.User).all()
    jobs = db.query(models.Job).all()
    
    # --- CEO Intelligence Logic (ระบบคำนวณมูลค่าธุรกิจ) ---
    total_payload_value = sum(job.price for job in jobs) if jobs else 0
    # สมมติรายได้คือ 50 บาท ต่อหนึ่งการจองงาน
    potential_revenue = len(jobs) * 50 
    
    return templates.TemplateResponse("admin.html", {
        "request": request, 
        "users": users, 
        "jobs": jobs,
        "jobs_count": len(jobs),
        "total_value": total_payload_value,
        "potential_revenue": potential_revenue
    })

# --- 🛰️ PERSONNEL COMMAND (ระบบอนุมัติคนขับ) ---
@app.post("/admin/verify/{user_id}")
def verify_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if user:
        user.is_verified = True
        db.commit()
    return RedirectResponse(url="/admin", status_code=303)

# --- 📦 PAYLOAD DEPLOYMENT (ระบบลงประกาศงาน) ---
@app.post("/admin/add-job")
def add_job(
    title: str = Form(...), 
    origin: str = Form(...), 
    destination: str = Form(...), 
    price: float = Form(...), 
    truck_type: str = Form(...),
    db: Session = Depends(get_db)
):
    new_job = models.Job(
        title=title,
        origin=origin,
        destination=destination,
        price=price,
        truck_type_required=truck_type,
        status="Open"
    )
    db.add(new_job)
    db.commit()
    return RedirectResponse(url="/admin", status_code=303)

# --- 🧪 SYSTEM TEST (ปุ่มทดสอบเพิ่มข้อมูล) ---
@app.get("/test-add")
def test_add(db: Session = Depends(get_db)):
    # สร้างคนขับรถจำลอง
    new_user = models.User(full_name="Teerapong Rocket", phone="0812345678", role="contractor")
    db.add(new_user)
    db.commit()
    return RedirectResponse(url="/admin")

# 5. สั่งเริ่มเดินเครื่องยนต์ (Ignition)
if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)

# --- ระบบเพิ่มคนขับรถแบบระบุตำแหน่ง (Intelligence Registration) ---
@app.post("/admin/add-driver")
def add_driver(
    name: str = Form(...), 
    phone: str = Form(...), 
    location: str = Form(...), # จังหวัดปัจจุบันของรถ
    db: Session = Depends(get_db)
):
    new_user = models.User(
        full_name=name, 
        phone=phone, 
        role="contractor",
        # เราจะจำลองการเก็บตำแหน่งไว้ในชื่อหรือฟิลด์ที่เกี่ยวข้อง
    )
    # หมายเหตุ: ในอนาคตเราจะเพิ่มฟิลด์ location ในฐานข้อมูลจริง
    db.add(new_user)
    db.commit()
    return RedirectResponse(url="/admin", status_code=303)