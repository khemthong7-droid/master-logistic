from fastapi import FastAPI, Depends, HTTPException, Request, Form, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from app import database, models
import uvicorn, requests, json, os

# --- 🛰️ 1. CONFIGURATION ---
CHANNEL_ACCESS_TOKEN = os.getenv("CHANNEL_ACCESS_TOKEN", "t3oqxpj2T5iHob1wQc+dD4VdsBkEndvRL6Qw6LbYvCf1q8XCNxYDdBF8HV3Mmij96NyoZ6BwirfT7E7qz8c0gqL8mEv65WGV+bEFhu8+aUfVkZu9cZWbiGMbVBCb+S9yC96x0eWOAVADwGzYAJEmcwdB04t89/1O/w1cDnyilFU=")
USER_ID = os.getenv("USER_ID", "U2d0ca4bdeca0910361b01438c9f19e23")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "masgistics2024") # รหัสผ่านเข้าศูนย์บัญชาการ

def send_line_message(text):
    url = "https://api.line.me/v2/bot/message/push"
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {CHANNEL_ACCESS_TOKEN}"}
    payload = {"to": USER_ID, "messages": [{"type": "text", "text": f"🛰️ MASGISTICS REPORT:\n{text}"}]}
    try: requests.post(url, headers=headers, data=json.dumps(payload))
    except Exception as e: print(f"LINE Error: {e}")

# --- 🚀 2. INITIALIZATION ---
database.init_db()
app = FastAPI(title="MASGISTICS")
if not os.path.exists("static"): os.makedirs("static")
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

def get_db():
    db = database.SessionLocal()
    try: yield db
    finally: db.close()

# --- 🛸 3. SMART OPERATIONS (LOGIC) ---

@app.get("/")
def root(): return RedirectResponse(url="/profile")

@app.get("/profile", response_class=HTMLResponse)
def company_profile(request: Request):
    return templates.TemplateResponse("profile.html", {"request": request})

@app.get("/admin", response_class=HTMLResponse)
def admin_dashboard(request: Request, db: Session = Depends(get_db)):
    users = db.query(models.User).all()
    jobs = db.query(models.Job).all()
    
    # Smart Matching: จับคู่งานกับคนขับที่มีจังหวัดตรงกัน (Simulated Match)
    matches = []
    for job in jobs:
        suitable_users = [u for u in users if u.role == "individual" and u.is_verified]
        if suitable_users:
            matches.append({"job": job, "suggested": suitable_users})

    total_val = sum(j.price for j in jobs) if jobs else 0
    # รายได้จริง: นับจากการจองงานสำเร็จ (Transaction Type: Job-Deduction)
    actual_rev = db.query(models.Transaction).filter(models.Transaction.type == "Job-Deduction").count() * 50
    
    return templates.TemplateResponse("admin.html", {
        "request": request, "users": users, "jobs": jobs,
        "jobs_count": len(jobs), "total_value": total_val, 
        "potential_revenue": actual_rev, "matches": matches
    })

@app.post("/admin/add-job")
def add_job(title: str = Form(...), origin: str = Form(...), destination: str = Form(...), 
            price: float = Form(...), truck_type: str = Form(...), db: Session = Depends(get_db)):
    new_job = models.Job(title=title, origin=origin, destination=destination, price=price, truck_type_required=truck_type)
    db.add(new_job); db.commit()
    send_line_message(f"📦 Payload ใหม่: {title}\n📍 {origin} -> {destination}\n💰 ฿{price:,.0f}")
    return RedirectResponse(url="/admin", status_code=303)

@app.post("/admin/assign-job")
def assign_job(job_id: int = Form(...), user_id: int = Form(...), db: Session = Depends(get_db)):
    """ระบบจองงานและตัดเงินเครดิต (The Money Maker)"""
    user = db.query(models.User).filter(models.User.id == user_id).first()
    job = db.query(models.Job).filter(models.Job.id == job_id).first()
    
    fee = 50.0 # ค่าธรรมเนียมจองงาน
    if user.wallet_balance >= fee:
        user.wallet_balance -= fee
        job.status = "Matched"
        new_tx = models.Transaction(user_id=user.id, amount=-fee, type="Job-Deduction")
        db.add(new_tx); db.commit()
        send_line_message(f"✅ ภารกิจถูกจองแล้ว!\n👤 {user.full_name}\n📦 งาน: {job.title}\n💸 หักเครดิต: ฿{fee}")
        return RedirectResponse(url="/admin", status_code=303)
    else:
        return HTMLResponse("เครดิตไม่เพียงพอ")

@app.get("/join", response_class=HTMLResponse)
def join_page(request: Request): return templates.TemplateResponse("register.html", {"request": request})

@app.post("/initiate-onboarding")
def initiate_onboarding(name: str = Form(...), phone: str = Form(...), user_role: str = Form(...), 
                        province: str = Form(...), db: Session = Depends(get_db)):
    new_user = models.User(full_name=name, phone=phone, role=user_role, wallet_balance=0.0)
    db.add(new_user); db.commit()
    role_th = {"shipper": "เจ้าของวัสดุ", "fleet": "เจ้าของกลุ่มรถ", "individual": "รถรายย่อย", "agency": "นายหน้า"}
    send_line_message(f"🆕 สมาชิกลงทะเบียนใหม่!\n👤 {name}\n🏷️ {role_th.get(user_role)}\n📍 {province}")
    return HTMLResponse(content=f"<html><body style='background:#050505;color:#00ff41;display:flex;justify-content:center;align-items:center;height:100vh;text-align:center;'><div><h1>TRANSMISSION RECEIVED</h1><a href='/join' style='color:white;'>RETURN</a></div></body></html>")

@app.post("/admin/topup/{user_id}")
def topup_wallet(user_id: int, amount: float = Form(...), db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if user:
        user.wallet_balance += amount
        new_tx = models.Transaction(user_id=user.id, amount=amount, type="Top-up")
        db.add(new_tx); db.commit()
        send_line_message(f"💰 เติมเครดิตสำเร็จ!\n👤 {user.full_name}\n➕ ฿{amount:,.0f}")
    return RedirectResponse(url="/admin", status_code=303)

@app.post("/admin/verify/{user_id}")
def verify_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if user: user.is_verified = True; db.commit()
    return RedirectResponse(url="/admin", status_code=303)

if __name__ == "__main__": uvicorn.run("main:app", host="127.0.0.1", port=8000)