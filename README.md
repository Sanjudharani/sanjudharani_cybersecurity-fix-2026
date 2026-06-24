# Vulnerable Notes API - Starter Code

This is a deliberately vulnerable FastAPI app for a defensive cybersecurity take-home.

## Run locally

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m app.seed
uvicorn app.main:app --reload
```

API docs:

```text
http://localhost:8000/docs
```

## Seed users

```text
admin@example.com / admin123
alice@example.com / alice123
bob@example.com / bob123
```

## Main endpoints

```text
POST /auth/register
POST /auth/login
GET  /auth/me

GET  /users/{user_id}
POST /notes
GET  /notes
GET  /notes/{note_id}

GET  /files/{file_name}
GET  /admin/audit-logs
```

## Candidate task

Audit this app, find vulnerabilities, fix them, and add tests. 



# Cybersecurity Fix Assignment

## Vulnerabilities Fixed

1. SQL Injection
2. Plain Text Password Storage
3. Hardcoded JWT Secret
4. Missing JWT Expiration
5. Sensitive Data Exposure
6. User IDOR
7. Notes IDOR
8. Path Traversal

## Installation

pip install -r requirements.txt

## Run

python -m uvicorn app.main:app --reload

## Tests

pytest

## Security Improvements

* Parameterized SQL Queries
* bcrypt Password Hashing
* JWT Expiration
* Environment Secrets
* Authorization Checks
* Path Validation
