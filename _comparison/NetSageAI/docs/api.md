# NetSage AI REST API Documentation

Base URL: `http://127.0.0.1:8000`

Interactive OpenAPI Swagger docs available at: `http://127.0.0.1:8000/docs`

## Endpoints Summary

### Health
- `GET /health` -> Returns API operational status, active database engine, and LLM provider mode.

### Cases
- `GET /api/cases` -> List all Cisco troubleshooting cases (supports `concept` and `severity` query filters).
- `GET /api/cases/{case_id}` -> Get detailed case object by `case_id` (e.g. CASE-001).
- `POST /api/cases` -> Ingest a new troubleshooting case.

### Diagnosis
- `POST /api/diagnose` -> Executes deterministic rules + AI diagnosis engine. Returns structured diagnosis & evidence.
- `GET /api/diagnoses` -> List all historical diagnosis runs.
- `GET /api/diagnoses/{id}` -> Get specific diagnosis run by integer database ID.

### Reviews & Governance
- `POST /api/reviews` -> Submit mandatory human review (`Accepted`, `Edited`, `Rejected`).
- `GET /api/reviews` -> Get all human review history.
- `GET /api/analytics` -> Get system metrics, issue distribution, severity counts, and agreement rate.
- `GET /api/responsible-ai` -> Get audit log of human corrections and AI failure lessons.
