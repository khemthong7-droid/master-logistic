from fastapi import FastAPI, Depends, HTTPException, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from app import database, models
import uvicorn

# 1. เริ่มระบบฐานข้อมูล
database.init_db()

# 2. สร้าง App Object (ต้องอยู่ตรงนี้!)
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

# --- 🚀 ROUTES (ลำดับการทำงาน) ---

# หน้าแรกสุด: ให้ Redirect ไปที่หน้า Admin ทันที (แก้ปัญหา 404)
@app.get("/")
def root():
    return RedirectResponse(url="/admin")

# หน้า Mission Control
@app.get("/admin", response_class=HTMLResponse)
def admin_dashboard(request: Request, db: Session = Depends(get_db)):
    users = db.query(models.User).all()
    jobs = db.query(models.Job).all()
    total_payload_value = sum(job.price for job in jobs) if jobs else 0
    potential_revenue = len(jobs) * 50 
    
    return templates.TemplateResponse("admin.html", {
        "request": request, 
        "users": users, 
        "jobs": jobs,
        "jobs_count": len(jobs),
        "total_value": total_payload_value,
        "potential_revenue": potential_revenue
    })

# ระบบอนุมัติคนขับ
@app.post("/admin/verify/{user_id}")
def verify_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if user:
        user.is_verified = True
        db.commit()
    return RedirectResponse(url="/admin", status_code=303)

# ระบบลงประกาศงาน
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
        title=title, origin=origin, destination=destination,
        price=price, truck_type_required=truck_type, status="Open"
    )
    db.add(new_job)
    db.commit()
    return RedirectResponse(url="/admin", status_code=303)

# ระบบทดสอบ
@app.get("/test-add")
def test_add(db: Session = Depends(get_db)):
    new_user = models.User(full_name="Teerapong Rocket", phone="0812345678", role="contractor")
    db.add(new_user)
    db.commit()
    return RedirectResponse(url="/admin")

# 5. สั่งเริ่มเดินเครื่องยนต์
if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)