from fastapi import FastAPI, Depends, HTTPException, Request, Form, Response
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from app import database, models
import uvicorn, requests, json, os

# --- 🛰️ 1. CONFIGURATION ---
CHANNEL_ACCESS_TOKEN = os.getenv("CHANNEL_ACCESS_TOKEN", "t3oqxpj2T5iHob1wQc+dD4VdsBkEndvRL6Qw6LbYvCf1q8XCNxYDdBF8HV3Mmij96NyoZ6BwirfT7E7qz8c0gqL8mEv65WGV+bEFhu8+aUfVkZu9cZWbiGMbVBCb+S9yC96x0eWOAVADwGzYAJEmcwdB04t89/1O/w1cDnyilFU=")
USER_ID = os.getenv("USER_ID", "U2d0ca4bdeca0910361b01438c9f19e23")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "masgistics2024") 
LINE_OA_LINK = "https://line.me/ti/p/@839wctaq"

# --- 🧠 2. MISSION HELPERS ---
def send_line_message(text):
    url = "https://api.line.me/v2/bot/message/push"
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {CHANNEL_ACCESS_TOKEN}"}
    payload = {"to": USER_ID, "messages": [{"type": "text", "text": f"🛰️ MASGISTICS REPORT:\n{text}"}]}
    try: requests.post(url, headers=headers, data=json.dumps(payload))
    except Exception as e: print(f"LINE Error: {e}")

def is_authenticated(request: Request):
    return request.cookies.get("mas_session") == "authenticated"

# --- 🚀 3. INITIALIZATION ---
database.init_db()
app = FastAPI(title="MASGISTICS")
if not os.path.exists("static"): os.makedirs("static")
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

def get_db():
    db = database.SessionLocal()
    try: yield db
    finally: db.close()

# --- 🛸 4. MISSION ROUTES ---

# [ROOT & PROFILE]
@app.get("/")
def root(): return RedirectResponse(url="/profile")

@app.get("/profile", response_class=HTMLResponse)
def company_profile(request: Request):
    return templates.TemplateResponse("profile.html", {"request": request})

# [SECURITY & LOGIN]
@app.get("/login", response_class=HTMLResponse)
def login_page(request: Request):
    return HTMLResponse(content=f"""
        <html><body style='background:#050505;color:white;display:flex;justify-content:center;align-items:center;height:100vh;font-family:sans-serif;'>
            <form action='/login' method='post' style='background:rgba(255,255,255,0.05);padding:40px;border-radius:10px;border:1px solid rgba(255,255,255,0.1);text-align:center;'>
                <h1 style='letter-spacing:5px;font-style:italic;'>MISSION CONTROL LOGIN</h1>
                <input type='password' name='password' placeholder='Authorization Code' style='padding:12px;width:100%;margin-top:20px;background:black;color:white;border:1px solid white;outline:none;' required>
                <button type='submit' style='margin-top:20px;width:100%;padding:12px;background:white;color:black;font-weight:bold;cursor:pointer;border:none;'>ACCESS COMMAND CENTER</button>
            </form>
        </body></html>
    """)

@app.post("/login")
def process_login(response: Response, password: str = Form(...)):
    if password == ADMIN_PASSWORD:
        response = RedirectResponse(url="/admin", status_code=303)
        response.set_cookie(key="mas_session", value="authenticated")
        return response
    return HTMLResponse("<body style='background:black;color:red;display:flex;justify-content:center;align-items:center;height:100vh;'><h1>ACCESS DENIED</h1></body>")

# [ADMIN DASHBOARD]
@app.get("/admin", response_class=HTMLResponse)
def admin_dashboard(request: Request, db: Session = Depends(get_db)):
    if not is_authenticated(request): return RedirectResponse(url="/login")
    users = db.query(models.User).all()
    jobs = db.query(models.Job).filter(models.Job.status == "Open").all()
    total_val = sum(j.price for j in jobs) if jobs else 0
    actual_rev = db.query(models.Transaction).filter(models.Transaction.type == "Job-Deduction").count() * 50
    verified_carriers = [u for u in users if u.is_verified]
    return templates.TemplateResponse("admin.html", {
        "request": request, "users": users, "jobs": jobs,
        "jobs_count": len(jobs), "total_value": total_val, 
        "potential_revenue": actual_rev, "verified_carriers": verified_carriers
    })

# [PUBLIC PAYLOADS]
@app.get("/payloads", response_class=HTMLResponse)
def public_jobs(request: Request, db: Session = Depends(get_db)):
    try: open_jobs = db.query(models.Job).filter(models.Job.status == "Open").all()
    except Exception: open_jobs = db.query(models.Job).all()
    return templates.TemplateResponse("payloads.html", {"request": request, "jobs": open_jobs, "line_link": LINE_OA_LINK})

# [TRANSACTIONS & ACTIONS]
@app.post("/admin/assign-job")
def assign_job(job_id: int = Form(...), user_id: int = Form(...), db: Session = Depends(get_db)):
    user, job = db.query(models.User).get(user_id), db.query(models.Job).get(job_id)
    if user.wallet_balance >= 50:
        user.wallet_balance -= 50
        job.status = "Matched"
        db.add(models.Transaction(user_id=user.id, amount=-50, type="Job-Deduction"))
        db.commit()
        send_line_message(f"✅ MISSION MATCHED!\n📦 {job.title}\n👩‍🚀 {user.full_name}\n💸 ฿50 Deducted")
    return RedirectResponse(url="/admin", status_code=303)

@app.post("/admin/topup/{user_id}")
def topup_wallet(user_id: int, amount: float = Form(...), db: Session = Depends(get_db)):
    user = db.query(models.User).get(user_id)
    if user:
        user.wallet_balance += amount
        db.add(models.Transaction(user_id=user.id, amount=amount, type="Top-up"))
        db.commit()
        send_line_message(f"💰 TOP-UP SUCCESS!\n👤 {user.full_name}\n➕ ฿{amount:,.0f}")
    return RedirectResponse(url="/admin", status_code=303)

@app.post("/admin/add-job")
def add_job(title: str = Form(...), origin: str = Form(...), destination: str = Form(...), 
            price: float = Form(...), truck_type: str = Form(...), db: Session = Depends(get_db)):
    db.add(models.Job(title=title, origin=origin, destination=destination, price=price, truck_type_required=truck_type, status="Open"))
    db.commit()
    send_line_message(f"📦 NEW PAYLOAD!\n📍 {origin} -> {destination}\n💰 ฿{price:,.0f}")
    return RedirectResponse(url="/admin", status_code=303)

@app.get("/join", response_class=HTMLResponse)
def join_page(request: Request): return templates.TemplateResponse("register.html", {"request": request})

@app.post("/initiate-onboarding")
def initiate_onboarding(name: str = Form(...), phone: str = Form(...), user_role: str = Form(...), 
                        province: str = Form(...), db: Session = Depends(get_db)):
    db.add(models.User(full_name=name, phone=phone, role=user_role, wallet_balance=0.0))
    db.commit()
    role_th = {"shipper": "เจ้าของวัสดุ", "fleet": "เจ้าของกลุ่มรถ", "individual": "รถรายย่อย", "agency": "นายหน้า"}
    send_line_message(f"🆕 NEW PERSONNEL!\n👤 {name}\n🏷️ {role_th.get(user_role)}\n📍 {province}")
    return HTMLResponse(content=f"<html><body style='background:#050505;color:#00ff41;display:flex;justify-content:center;align-items:center;height:100vh;text-align:center;font-family:sans-serif;'><div><h1>TRANSMISSION RECEIVED</h1><p style='color:white;'>ข้อมูลของ ({name}) ถูกส่งเข้าสู่ศูนย์ควบคุม MASGISTICS แล้ว</p><a href='/join' style='color:#00ff41;text-decoration:none;border:1px solid #00ff41;padding:10px 20px;margin-top:20px;display:inline-block;'>RETURN</a></div></body></html>")

@app.post("/admin/verify/{user_id}")
def verify_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(models.User).get(user_id)
    if user: user.is_verified = True; db.commit()
    return RedirectResponse(url="/admin", status_code=303)

if __name__ == "__main__": uvicorn.run("main:app", host="127.0.0.1", port=8000)