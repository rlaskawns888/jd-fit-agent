# jd-fit-agent
AI Agent for JD analysis, resume matching, fit scoring, and application strategy.

## Project Structure

```text
jd-fit-agent/
├─ app/
│  ├─ main.py
│  ├─ core/
│  │  ├─ config.py
│  │  └─ exceptions.py
│  ├─ api/
│  │  ├─ health_router.py
│  │  └─ analysis_router.py
│  ├─ schemas/
│  │  ├─ common_schema.py
│  │  └─ analysis_schema.py
│  └─ services/
│     └─ analysis_service.py
├─ .env.example
├─ requirements.txt
├─ Dockerfile
├─ docker-compose.yml
├─ tests/
└─ sample_data/
```

## Run

```bash
pip install -r requirements.txt
uvicorn app.main:app --reload
```
