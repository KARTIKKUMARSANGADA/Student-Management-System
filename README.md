# Student Management System (FastAPI)

FastAPI backend for managing students, courses, enrollments, grades, and authentication.

## Features

- JWT authentication (`/auth`)
- Student CRUD (`/students`)
- Course CRUD (`/courses`)
- Enrollment management (`/enrollments`)
- Grade management (`/grades`)
- SQLAlchemy + Alembic migrations

## Tech Stack

- FastAPI
- Uvicorn
- SQLAlchemy
- PostgreSQL (`psycopg2-binary`)
- Alembic
- Pydantic Settings

## Project Structure

```text
SMS/
  app/
    main.py
    config.py
    database.py
    models/
    routers/
    schemas/
    utils/
  alembic/
  alembic.ini
  requirements.txt
```

## Setup

1. Create and activate virtual environment:

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

2. Install dependencies:

```powershell
pip install -r requirements.txt
```

3. Create `.env` in project root:

```env
DATABASE_URL=postgresql://username:password@localhost:5432/sms_db
OTP_EXPIRE_MINUTES=10
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7
RESET_TOKEN_EXPIRE_MINUTES=15
JWT_SECRET_KEY=your_secret_key
ALGORITHM=HS256
EMAIL_ADDRESS=your_email@example.com
EMAIL_PASSWORD=your_email_password
```

4. Run migrations:

```powershell
alembic upgrade head
```

5. Start server:

```powershell
uvicorn app.main:app --reload
```

## API Docs

- Swagger UI: `http://127.0.0.1:8000/docs`
- ReDoc: `http://127.0.0.1:8000/redoc`
