from fastapi import FastAPI, Depends, HTTPException, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from app import database, models
import uvicorn
import requests
import json

# --- 🛰️ 1. LINE CONFIGURATION (ใส่รหัสของคุณที่นี่) ---
CHANNEL_ACCESS_TOKEN = "t3oqxpj2T5iHob1wQc+dD4VdsBkEndvRL6Qw6LbYvCf1q8XCNxYDdBF8HV3Mmij96NyoZ6BwirfT7E7qz8c0gqL8mEv65WGV+bEFhu8+aUfVkZu9cZWbiGMbVBCb+S9yC96x0eWOAVADwGzYAJEmcwdB04t89/1O/w1cDnyilFU="
USER_ID = "U2d0ca4bdeca0910361b01438c9f19e23"

# --- 🧠 2. HELPER FUNCTIONS ---
def send_line_message(text):
    url = "https://api.line.me/v2/bot/message/push"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {CHANNEL_ACCESS_TOKEN}"
    }
    payload = {
        "to": USER_ID,
        "messages": [{"type": "text", "text": f"🛰️ MASGISTICS REPORT:\n{text}"}]
    }
    try:
        response = requests.post(url, headers=headers, data=json.dumps(payload))
        print(f"LINE Status: {response.status_code}")
    except Exception as e:
        print(f"LINE Error: {e}")

# --- 🚀 3. SYSTEM INITIALIZATION ---
database.init_db()
app = FastAPI(title="MASGISTICS - Mission Control")
templates = Jinja2Templates(directory="templates")

def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- 🛸 4. ROUTES (จุดควบคุมระบบ) ---

@app.get("/")
def root():
    return RedirectResponse(url="/admin")

@app.get("/admin", response_class=HTMLResponse)
def admin_dashboard(request: Request, db: Session = Depends(get_db)):
    users = db.query(models.User).all()
    jobs = db.query(models.Job).all()
    total_payload_value = sum(job.price for job in jobs) if jobs else 0
    potential_revenue = len(jobs) * 50 
    return templates.TemplateResponse("admin.html", {
        "request": request, "users": users, "jobs": jobs,
        "jobs_count": len(jobs), "total_value": total_payload_value,
        "potential_revenue": potential_revenue
    })

@app.post("/admin/add-job")
def add_job(
    title: str = Form(...), origin: str = Form(...), 
    destination: str = Form(...), price: float = Form(...), 
    truck_type: str = Form(...), db: Session = Depends(get_db)
):
    new_job = models.Job(title=title, origin=origin, destination=destination,
                         price=price, truck_type_required=truck_type, status="Open")
    db.add(new_job)
    db.commit()
    # แจ้งเตือนผ่าน LINE เมื่อมีการลงงานใหม่
    send_line_message(f"📦 Payload ใหม่: {title}\nเส้นทาง: {origin} -> {destination}\nราคา: ฿{price:,.0f}")
    return RedirectResponse(url="/admin", status_code=303)

@app.get("/join", response_class=HTMLResponse)
def join_page(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})

@app.post("/initiate-onboarding")
def initiate_onboarding(
    name: str = Form(...), phone: str = Form(...), 
    truck_type: str = Form(...), province: str = Form(...),
    db: Session = Depends(get_db)
):
    new_user = models.User(full_name=name, phone=phone, role="contractor")
    db.add(new_user)
    db.commit()
    # แจ้งเตือนผ่าน LINE เมื่อมีคนขับสมัครใหม่
    send_line_message(f"👩‍🚀 นักบินใหม่สมัครเข้าประจำการ!\nชื่อ: {name}\nรถ: {truck_type}\nจังหวัด: {province}")
    return HTMLResponse(content=f"<html><body style='background:#050505;color:#00ff41;display:flex;justify-content:center;align-items:center;height:100vh;text-align:center;'><div><h1>TRANSMISSION RECEIVED</h1><p>ข้อมูลของ {name} ถูกส่งเข้าศูนย์ควบคุมแล้ว</p><a href='/join' style='color:white;'>กลับ</a></div></body></html>")

@app.post("/admin/verify/{user_id}")
def verify_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if user:
        user.is_verified = True
        db.commit()
    return RedirectResponse(url="/admin", status_code=303)

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)