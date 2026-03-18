from fastapi import FastAPI, Depends, HTTPException, Request, Form, Response, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from app import database, models
import uvicorn, requests, json, os
from datetime import datetime, timezone

# --- 🛰️ 1. CONFIGURATION (Security & Communications) ---
CHANNEL_ACCESS_TOKEN = os.getenv("CHANNEL_ACCESS_TOKEN", "t3oqxpj2T5iHob1wQc+dD4VdsBkEndvRL6Qw6LbYvCf1q8XCNxYDdBF8HV3Mmij96NyoZ6BwirfT7E7qz8c0gqL8mEv65WGV+bEFhu8+aUfVkZu9cZWbiGMbVBCb+S9yC96x0eWOAVADwGzYAJEmcwdB04t89/1O/w1cDnyilFU=")
USER_ID = os.getenv("USER_ID", "U2d0ca4bdeca0910361b01438c9f19e23")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "masgistics2024") 
LINE_OA_LINK = "https://line.me/ti/p/@839wctaq"

# --- 🚀 2. SYSTEM INITIALIZATION ---
database.init_db()
app = FastAPI(title="MASGISTICS") # สร้าง App ก่อนเรียกใช้ @app

# ตั้งค่า Static Files และ Templates
if not os.path.exists("static"): os.makedirs("static")
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

def get_db():
    db = database.SessionLocal()
    try: yield db
    finally: db.close()

# --- 🧠 3. MISSION HELPERS (Intelligence & Security) ---

def send_line_message(text):
    """ส่งสัญญาณแจ้งเตือนเข้าสู่ LINE OA"""
    url = "https://api.line.me/v2/bot/message/push"
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {CHANNEL_ACCESS_TOKEN}"}
    payload = {"to": USER_ID, "messages": [{"type": "text", "text": f"🛰️ MASGISTICS REPORT:\n{text}"}]}
    try: requests.post(url, headers=headers, data=json.dumps(payload))
    except Exception as e: print(f"LINE Error: {e}")

def log_event(db: Session, event_type: str, user_id: int = None, meta: dict = None):
    """Telemetry System: บันทึกข้อมูลเพื่อพัฒนาตัวเองอัตโนมัติ"""
    new_event = models.SystemEvent(
        event_type=event_type, 
        user_id=user_id, 
        metadata_json=json.dumps(meta) if meta else "{}"
    )
    db.add(new_event); db.commit()

def is_authenticated(request: Request):
    """ระบบตรวจตั๋วผ่านทางเข้าศูนย์บัญชาการ"""
    return request.cookies.get("mas_session") == "authenticated"

# --- 🛸 4. MISSION ROUTES (The Command Center) ---

@app.get("/")
def root(): return RedirectResponse(url="/profile")

@app.get("/profile", response_class=HTMLResponse)
def company_profile(request: Request, db: Session = Depends(get_db)):
    log_event(db, "view_profile")
    return templates.TemplateResponse("profile.html", {"request": request})

# [SECURITY]
@app.get("/login", response_class=HTMLResponse)
def login_page(request: Request):
    return HTMLResponse(content="""
        <html><body style='background:#050505;color:white;display:flex;justify-content:center;align-items:center;height:100vh;font-family:sans-serif;text-align:center;'>
            <form action='/login' method='post' style='background:rgba(255,255,255,0.05);padding:40px;border-radius:10px;border:1px solid rgba(255,255,255,0.1);'>
                <h1 style='letter-spacing:5px;font-style:italic;'>MISSION CONTROL LOGIN</h1>
                <input type='password' name='password' placeholder='Authorization Code' style='padding:12px;width:100%;margin-top:20px;background:black;color:white;border:1px solid white;outline:none;' required>
                <button type='submit' style='margin-top:20px;width:100%;padding:12px;background:white;color:black;font-weight:bold;cursor:pointer;border:none;'>ACCESS COMMAND</button>
            </form>
        </body></html>
    """)

@app.post("/login")
def process_login(response: Response, password: str = Form(...)):
    if password == ADMIN_PASSWORD:
        res = RedirectResponse(url="/admin", status_code=303)
        res.set_cookie(key="mas_session", value="authenticated", httponly=True)
        return res
    return HTMLResponse("<h1 style='color:red; text-align:center;'>ACCESS DENIED</h1>")

# [ADMIN ANALYTICS - UNIT 4]
@app.get("/admin", response_class=HTMLResponse)
def admin_dashboard(request: Request, db: Session = Depends(get_db)):
    if not is_authenticated(request): return RedirectResponse(url="/login")
    
    users = db.query(models.User).all()
    open_jobs = db.query(models.Job).filter(models.Job.status == "Open").all()
    matched_jobs = db.query(models.Job).filter(models.Job.status == "Matched").all()
    
    # Logic วิเคราะห์ Conversion Rate
    total_tx = db.query(models.Transaction).filter(models.Transaction.type == "Job-Deduction").count()
    view_events = db.query(models.SystemEvent).filter(models.SystemEvent.event_type == "view_payloads").count()
    conv_rate = (total_tx / view_events * 100) if view_events > 0 else 0
    
    return templates.TemplateResponse("admin.html", {
        "request": request, "users": users, 
        "jobs": open_jobs, "matched_jobs": matched_jobs,
        "jobs_count": len(open_jobs), 
        "total_value": sum(j.price for j in open_jobs), 
        "potential_revenue": total_tx * 50,
        "verified_carriers": [u for u in users if u.is_verified],
        "total_telemetry": db.query(models.SystemEvent).count(),
        "conv_rate": round(conv_rate, 2),
        "view_count": view_events
    })

# [PUBLIC VIEW]
@app.get("/payloads", response_class=HTMLResponse)
def public_jobs(request: Request, db: Session = Depends(get_db)):
    log_event(db, "view_payloads")
    jobs = db.query(models.Job).filter(models.Job.status == "Open").all()
    return templates.TemplateResponse("payloads.html", {"request": request, "jobs": jobs, "line_link": LINE_OA_LINK})

# [ONBOARDING]
@app.get("/join", response_class=HTMLResponse)
def join_page(request: Request, db: Session = Depends(get_db)):
    log_event(db, "view_join")
    return templates.TemplateResponse("register.html", {"request": request})

@app.post("/initiate-onboarding")
def initiate_onboarding(name: str = Form(...), phone: str = Form(...), user_role: str = Form(...), province: str = Form(...), db: Session = Depends(get_db)):
    new_user = models.User(full_name=name, phone=phone, role=user_role)
    db.add(new_user); db.commit()
    log_event(db, "user_registered", new_user.id, {"role": user_role})
    send_line_message(f"🆕 NEW PERSONNEL!\n👤 ชื่อ: {name}\n🏷️ {user_role}\n📍 {province}")
    return HTMLResponse(content=f"<html><body style='background:#050505;color:#00ff41;display:flex;justify-content:center;align-items:center;height:100vh;text-align:center;'><div><h1>TRANSMISSION RECEIVED</h1><a href='/join' style='color:white;'>RETURN</a></div></body></html>")

# [SYSTEM ACTIONS]
@app.post("/admin/assign-job")
def assign_job(job_id: int = Form(...), user_id: int = Form(...), db: Session = Depends(get_db)):
    user, job = db.query(models.User).get(user_id), db.query(models.Job).get(job_id)
    if user.wallet_balance >= 50:
        user.wallet_balance -= 50; job.status = "Matched"
        db.add(models.Transaction(user_id=user.id, amount=-50, type="Job-Deduction")); db.commit()
        log_event(db, "job_matched", user.id, {"job_id": job_id})
        send_line_message(f"✅ MISSION MATCHED!\n📦 {job.title}\n💸 ฿50 Deducted")
    return RedirectResponse(url="/admin", status_code=303)

@app.post("/admin/topup/{user_id}")
def topup_wallet(user_id: int, amount: float = Form(...), db: Session = Depends(get_db)):
    user = db.query(models.User).get(user_id)
    if user:
        user.wallet_balance += amount
        db.add(models.Transaction(user_id=user.id, amount=amount, type="Top-up")); db.commit()
        log_event(db, "wallet_topup", user_id, {"amount": amount})
        send_line_message(f"💰 TOP-UP: {user.full_name} +฿{amount:,.0f}")
    return RedirectResponse(url="/admin", status_code=303)

@app.post("/admin/verify/{user_id}")
def verify_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(models.User).get(user_id)
    if user: user.is_verified = True; db.commit(); log_event(db, "user_verified", user_id)
    return RedirectResponse(url="/admin", status_code=303)

@app.post("/admin/add-job")
def add_job(title: str = Form(...), origin: str = Form(...), destination: str = Form(...), price: float = Form(...), truck_type: str = Form(...), db: Session = Depends(get_db)):
    db.add(models.Job(title=title, origin=origin, destination=destination, price=price, truck_type_required=truck_type, status="Open"))
    db.commit(); log_event(db, "payload_deployed"); send_line_message(f"📦 NEW JOB: {title}")
    return RedirectResponse(url="/admin", status_code=303)

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)