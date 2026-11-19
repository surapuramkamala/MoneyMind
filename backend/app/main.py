
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from app.api.reports import router as reports_router

from app.api.investments import router as investments_router
from app.core.database import engine
from app.api.auth import router as auth_router
from app.api.income import router as income_router
from app.api.expenses import router as expenses_router

from app.api.advisor import router as advisor_router
from app.api.savings_goals import router as savings_goals_router
from app.api.budgets import router as budgets_router

app = FastAPI(
    title="MoneyMind AI",
    description="AI-powered Personal Finance and Investment Management",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(income_router)
app.include_router(expenses_router)
app.include_router(investments_router)
app.include_router(reports_router)
app.include_router(advisor_router)
app.include_router(savings_goals_router)
app.include_router(budgets_router)


@app.get("/")
def home():
    return {
        "application": "MoneyMind AI",
        "message": "Welcome to MoneyMind AI",
        "currency": "INR",
        "status": "running"
    }


@app.get("/api/health")
def health_check():
    return {
        "status": "healthy",
        "backend": "FastAPI",
        "currency": "INR"
    }


@app.get("/api/database-check")
def database_check():
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))

        return {
            "status": "success",
            "database": "PostgreSQL",
            "database_name": "moneymind_db"
        }
    except Exception:
        return {
            "status": "error",
            "message": "Database connection failed"
        }
