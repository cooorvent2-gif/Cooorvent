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

@app.post("/api/reports")
def add_report(report: Report):
    data = report.dict()
    data["created_at"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    reports_db.append(data)
    return {"status": "success", "message": "Отчет сохранен в облаке!", "data": data}

@app.get("/api/reports")
def get_reports():
    return reports_db
