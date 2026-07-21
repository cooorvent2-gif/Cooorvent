from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional, List
import datetime

app = FastAPI(title="Mobile Report API")

class Report(BaseModel):
    user_id: int
    category: str
    hours_spent: float
    description: str
    project_name: Optional[str] = None

# Временная память в облаке
reports_db = []
@app.get("/api/reports")
def get_reports():
    # Здесь ты возвращаешь список отчетов из своей базы данных (например, из SQLAlchemy или списка)
    # Пример возврата тестовых или реальных данных:
    return [
        {
            "id": 1,
            "user_id": 1,
            "category": "Администрирование",
            "hours_spent": 1.5,
            "description": "Настройка сервера",
            "project_name": "Naumen SD / Внеплановая работа",
            "created_at": "21.07.2026 12:00"
        }
    ]
@app.post("/api/reports")
def add_report(report: Report):
    data = report.dict()
    data["created_at"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    reports_db.append(data)
    return {"status": "success", "message": "Отчет сохранен в облаке!", "data": data}

@app.get("/api/reports")
def get_reports():
    return reports_db
