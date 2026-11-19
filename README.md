<<<<<<< HEAD
Backend:- python -m uvicorn app.main:app --reload --port 
frontend:- npm run dev
=======
# MoneyMind
>>>>>>> eacd9f130f2724f05949965ecd939a04a8ddc32a

# MoneyMind AI

An AI-powered personal finance management application built to help users track income, expenses, budgets, savings goals, investments, and financial performance.

## Features

- Income and expense tracking
- Monthly budget planner
- Savings goals and contributions
- Investment and portfolio tracking
- Monthly and yearly financial reports
- Expense category breakdown
- AI-powered financial insights using NVIDIA NIM

## Technology Stack

**Backend:** Python, FastAPI, SQLAlchemy

**Frontend:** React, Vite, JavaScript

**Database:** PostgreSQL

**AI:** NVIDIA NIM API

## Local Development

### Backend

```bash
cd backend
..\.venv\Scripts\activate
python -m uvicorn app.main:app --reload --port 8000
```

Backend API documentation: http://127.0.0.1:8000/docs

### Frontend

Open another terminal:

```bash
cd frontend
npm install
npm run dev
```

Frontend: http://localhost:5173

## Environment Variables

Configure your backend `.env` file with your database credentials, JWT secret, and NVIDIA API settings.

Never commit `.env` files or API keys to GitHub.

## Project Status

Under development.
