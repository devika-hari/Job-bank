# Job Bank

A Fast API App to track job applications, interview rounds, and questions—with a minimal **Bootstrap + Jinja** UI and full **Swagger** API docs.


## Project overview

Looking for a job involves more than saving links. Job hunting is chaotic.
- Applied to 50+ jobs across LinkedIn, Indeed, StepStone — no single platform
- A recruiter calls 2 months later — you can't find the JD, can't remember the role
- Interview questions noted in books, Google Docs, random apps — scattered everywhere
- When preparing for a similar role — you can't find what you learned last time

This App will help you track applications and interview questions in one place and retrieve them whenever necessary.


| Folder | Why it exists |
|--------|----------------|
| `app/main.py` | FastAPI app, router registration, startup table creation |
| `app/database.py` | Engine, sessions, `get_db()` dependency |
| `app/models/` | SQLAlchemy tables (Python classes = rows) |
| `app/schemas/` | Pydantic models validate JSON in/out |
| `app/services/` | Business logic |
| `app/routers/` | HTTP endpoints (API + HTML) |
| `app/templates/` | Bootstrap HTML pages (used AI) |
| `tests/` | API integration tests |


## Database design


### Tables


1. **users** — who owns applications (demo user seeded on startup)
2. **jobs_applied** — each job application 
3. **interviews** — multiple rounds per job
4. **interview_questions** — multiple questions per interview
5. **tags** — skill labels (Python, Snowflake, …)
6. **question_tags** — many-to-many link table 


### Relationships (SQLAlchemy)


```
User 1 ── * JobApplied 1 ── * Interview 1 ── * InterviewQuestion * ── * Tag
                                             (via question_tags)
```


- `User.jobs` ↔ `JobApplied.user` (`back_populates`)
- `JobApplied.interviews` ↔ `Interview.job`
- `Interview.questions` ↔ `InterviewQuestion.interview`
- `InterviewQuestion.tags` ↔ `Tag.questions` (`secondary=question_tags`)




## Prerequisites


- Python 3.11+ 
- PostgreSQL 14+ installed locally
- `pip` and a virtual environment


---


## Environment variables (`.env`)

| Variable | Required | Description | Where you get the value |
|----------|----------|-------------|-------------------------|
| `POSTGRES_USER` | Yes | PostgreSQL login role | From `CREATE USER` in `setup/postgresql_setup.sql`, or default superuser `postgres` for local dev |
| `POSTGRES_PASSWORD` | Yes | Password for that role | The password you set in `CREATE USER ... WITH PASSWORD '...'` |
| `POSTGRES_HOST` | Yes | Server hostname | Usually `localhost` for local install |
| `POSTGRES_PORT` | Yes | Server port | Run `psql -U postgres -c "SHOW port;"` or check `postgresql.conf` (default `5432`) |
| `POSTGRES_DB` | Yes | Database name | From `CREATE DATABASE job_bank` → use `job_bank` |
| `DATABASE_URL` |  No | Full connection URL | **Optional.** If set, overrides all `POSTGRES_*` variables (used in testing) |
| `APP_TITLE `  | Yes | App Title name to appear on page | 'Job Bank'

`app/config.py` loads `.env` with `python-dotenv`, builds `DATABASE_URL`, and `app/database.py` uses it for SQLAlchemy.




Test credentials **before** starting FastAPI:


```bash
python scripts/check_db_connection.py
```


Expected output: `Connection OK.`


---


## PostgreSQL setup (one-time)


1. Start PostgreSQL 


2. Create database with:


```bash
python scripts/create_database.py
```


3. Create your local `.env` with below variable names. Ensure it matches what you created in SQL:


```env
POSTGRES_USER=job_bank_user
POSTGRES_PASSWORD=the_same_password_as_in_setup_sql
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=job_bank
# DATABASE_URL - used for testing
APP_TITLE="Job Bank"
```

Tables are created automatically on first API start (`init_db()` in `app/main.py`).


---


## Install and run


```bash
cd my-job-bank-app
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
# Ensure .env with your PostgreSQL user, password, port, database


python scripts/create_database.py   # if job_bank does not exist yet
python scripts/check_db_connection.py
uvicorn app.main:app --reload
```


Confirm the app is running: open http://127.0.0.1:8000/health — you should see `{"status":"ok",...}`.


### URLs


| URL | Purpose |
|-----|---------|
| http://127.0.0.1:8000/jobs | List jobs (HTML) |
| http://127.0.0.1:8000/jobs/add | Add job form |
| http://127.0.0.1:8000/questions/search | Search questions by tags |
| http://127.0.0.1:8000/docs | **Swagger / OpenAPI** |
| http://127.0.0.1:8000/redoc | ReDoc API docs |
| http://127.0.0.1:8000/health | Health check |


## Testing


Tests use **SQLite in memory** so you can run pytest without PostgreSQL. Production still uses PostgreSQL.


```bash
cd my-job-bank-app
pip install -r requirements.txt
pytest -v
```


Included:


- **Integration tests** (`tests/test_api_integration.py`) — full HTTP CRUD + search flows


## Project structure


```
my-job-bank-app/
├── app/
│   ├── main.py
│   ├── config.py
│   ├── database.py
│   ├── exceptions.py
│   ├── utils.py
│   ├── models/
│   ├── schemas/
│   ├── routers/
│   ├── services/
│   └── templates/
├── tests/
├── scripts/
├── setup/
├── requirements.txt
└── README.md
```

---


## Future enhancements


- **LinkedIn API integration** — import applied jobs automatically
- **Auto-fetch applied jobs** — browser extension or email parsing
- **AI interview analysis** — summarize questions, suggest study plan
- User accounts and login (OAuth)
- Alembic database migrations

Happy Job Searching!
