import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models import Base

# 1. ดึงค่า DATABASE_URL จาก Environment (Render) หรือใช้ SQLite (ในคอม)
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./master_logistic.db")

# 2. แก้ไขหัวอ่าน Postgres สำหรับ SQLAlchemy (Render มักให้ postgres:// มา)
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

# 3. สร้าง Engine (เครื่องยนต์) ตามประเภทฐานข้อมูล
if "postgresql" in DATABASE_URL:
    # สำหรับ PostgreSQL (บน Cloud)
    engine = create_engine(DATABASE_URL)
else:
    # สำหรับ SQLite (ในคอม) - ต้องมี check_same_thread: False
    engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

# 4. สร้าง Session สำหรับคุยกับ DB
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 5. ฟังก์ชันสร้างตาราง
def init_db():
    Base.metadata.create_all(bind=engine)