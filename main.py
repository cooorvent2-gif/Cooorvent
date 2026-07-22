from fastapi import FastAPI, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional
from sqlalchemy import create_engine, Column, Integer, String, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from datetime import datetime

# Настройка базы данных SQLite
SQLALCHEMY_DATABASE_URL = "sqlite:///./reports.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Модель экрана / устройства SmartPlayer в базе данных
class ScreenStatusModel(Base):
    __tablename__ = "screen_statuses"

    id = Column(Integer, primary_key=True, index=True)
    region = Column(String, index=True)          # Регион (например, "Самарская область")
    screen_name = Column(String, index=True)     # Название или номер экрана / аптеки
    status = Column(String)                      # "online" или "offline" / "error"
    last_ping = Column(String)                   # Время последней связи
    error_message = Column(String, nullable=True)  # Ошибка, если не работает

Base.metadata.create_all(bind=engine)

app = FastAPI()

class ScreenStatusCreate(BaseModel):
    region: str
    screen_name: str
    status: str  # "online" или "offline"
    error_message: Optional[str] = None

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# 1. Эндпоинт для обновления статуса экрана (сюда стучит SmartPlayer.py)
@app.post("/api/screens/status")
def update_screen_status(data: ScreenStatusCreate, db: Session = Depends(get_db)):
    current_time = datetime.now().strftime("%d.%m.%Y %H:%M")
    
    screen = db.query(ScreenStatusModel).filter(
        ScreenStatusModel.region == data.region,
        ScreenStatusModel.screen_name == data.screen_name
    ).first()

    if screen:
        screen.status = data.status
        screen.last_ping = current_time
        screen.error_message = data.error_message
    else:
        screen = ScreenStatusModel(
            region=data.region,
            screen_name=data.screen_name,
            status=data.status,
            last_ping=current_time,
            error_message=data.error_message
        )
        db.add(screen)
    
    db.commit()
    return {"status": "success", "message": "Статус экрана обновлен"}

# 2. Эндпоинт для получения списка всех уникальных регионов
@app.get("/api/regions")
def get_all_regions(db: Session = Depends(get_db)):
    regions = db.query(ScreenStatusModel.region).distinct().all()
    return [r[0] for r in regions]

# 3. Эндпоинт для дашборда (поддерживает конкретный регион или "ALL" для всех 43 регионов)
@app.get("/api/dashboard/{region_name}")
def get_region_dashboard(region_name: str, db: Session = Depends(get_db)):
    if region_name == "ALL":
        screens = db.query(ScreenStatusModel).all()
    else:
        screens = db.query(ScreenStatusModel).filter(ScreenStatusModel.region == region_name).all()
    
    total_screens = len(screens)
    online_screens = [s for s in screens if s.status == "online"]
    offline_screens = [s for s in screens if s.status != "online"]

    return {
        "region": region_name,
        "total": total_screens,
        "online_count": len(online_screens),
        "offline_count": len(offline_screens),
        "problem_screens": [
            {
                "region": s.region,
                "screen_name": s.screen_name,
                "status": s.status,
                "last_ping": s.last_ping,
                "error": s.error_message or "Нет связи"
            } for s in offline_screens
        ]
    }
