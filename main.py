from fastapi import FastAPI, Depends, HTTPException, Request, Form, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from sqlalchemy.orm import Session
from app import database, models
import uvicorn
import secrets

# สั่ง Launch ฐานข้อมูล
database.init_db()

app = FastAPI(title="Master Logistic - Mission Control")
templates = Jinja2Templates(directory="templates")
security = HTTPBasic()

# จุดบอด: ความปลอดภัยหน้า Admin
# ตั้งชื่อ Username/Password สำหรับเข้าศูนย์ควบคุม (เปลี่ยนตรงนี้ได้ครับ)
ADMIN_USER = "admin"
ADMIN_PASS = "spacex123"

def get_current_user(credentials: HTTPBasicCredentials = Depends(security)):
    is_correct_username = secrets.compare_digest(credentials.username, ADMIN_USER)
    is_correct_password = secrets.compare_digest(credentials.password, ADMIN_PASS)
    if not (is_correct_username and is_correct_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Access Denied: Mission Control Unauthorized",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username

def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- MISSION CONTROL (Admin Dashboard) ---
@app.get("/admin", response_class=HTMLResponse)
def mission_control(request: Request, db: Session = Depends(get_db), _ = Depends(get_current_user)):
    # เปลี่ยนชื่อเรียกในโค้ด: Users -> Carriers, Jobs -> Payloads
    carriers = db.query(models.User).all()
    payloads_count = db.query(models.Job).count()
    return templates.TemplateResponse("admin.html", {
        "request": request, 
        "carriers": carriers, 
        "payloads_count": payloads_count
    })

# --- AUTHORIZE PERSONNEL ---
@app.post("/admin/authorize/{user_id}")
def authorize_personnel(user_id: int, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if user:
        user.is_verified = True
        db.commit()
    return RedirectResponse(url="/admin", status_code=303)

@app.get("/test-launch")
def test_launch(db: Session = Depends(get_db)):
    # จำลองการสร้าง Carrier ใหม่
    new_carrier = models.User(full_name="Starship Carrier 01", phone="0991234567", role="Carrier")
    db.add(new_carrier)
    db.commit()
    return RedirectResponse(url="/admin")

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)