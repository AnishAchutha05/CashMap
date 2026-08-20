# CashMap (SplitEase)

A Splitwise-style shared expense tracker — log group expenses, split them fairly, and settle up with the **minimum number of transactions** needed to clear everyone's debts.

Built to demonstrate broad, hands-on backend and cloud engineering — not to reinvent the wheel. Every layer (auth, data modeling, caching, async messaging, containerization, CI/CD, cloud deployment) is implemented cleanly and intentionally, without hiding behind full microservices complexity.

---

## What it does

- **Log shared expenses** — equal, percentage, or exact splits, with deterministic rounding so amounts always reconcile to the cent.
- **See who owes whom** — real-time net balance per group member.
- **Settle up efficiently** — a greedy debt-simplification algorithm collapses messy multi-party debts into the minimum number of payments.
- **Track history** — filterable expense and settlement logs per group, person, or date.

---

## Architecture

```
                 ┌─────────────┐
   Client ─────▶ │  Core API   │──────▶ PostgreSQL (Cloud SQL)
 (Swagger/curl)  │  (FastAPI)  │──────▶ Redis (cache + pub/sub)
                 └─────┬───────┘
                       │ publishes events
                       ▼
                 ┌─────────────┐
                 │ Notification │
                 │   Worker     │──────▶ logs a structured event
                 │ (subscriber) │        (simulates a notification)
                 └─────────────┘
```

Two independently deployable services sharing one Postgres instance and one Redis instance:

- **core-api** — all REST endpoints, owns all writes to Postgres.
- **notification-worker** — a standalone subscriber process that reacts to events (new expense, settlement made) published over Redis Pub/Sub. Fully decoupled from core-api — no direct calls between them.

---

## Tech stack

| Layer | Choice |
|---|---|
| API framework | FastAPI |
| Database | PostgreSQL |
| Caching / messaging | Redis (cache-aside + Pub/Sub) |
| ORM | SQLAlchemy |
| Auth | JWT access tokens + rotating refresh tokens, bcrypt password hashing |
| Frontend | React |
| Containerization | Docker, docker-compose |
| Cloud | Google Cloud Platform — Cloud Run, Cloud SQL, Memorystore, Secret Manager |
| CI/CD | GitHub Actions |

---

## Backend concepts covered

- Relational data modeling with proper constraints and foreign keys
- REST API design — status codes, pagination, Pydantic validation
- Concurrency handling — DB transactions + optimistic locking on expense edits
- Redis caching of computed balances (cache-aside, invalidated on writes)
- Async messaging via Redis Pub/Sub, decoupling the notification worker from the core API
- Unit + integration testing

## Cloud / DevOps scope

- Per-service Dockerfiles, single docker-compose for local dev
- Deployment to Cloud Run (serverless containers) for both services
- Cloud SQL for Postgres, Memorystore for Redis
- CI/CD via GitHub Actions — test → build → deploy on merge to `main`
- Structured logging, health checks, and basic request metrics
- Secrets managed via GCP Secret Manager — never hardcoded or committed

---

## The interesting part: debt simplification

Given a group's net balances, the app collapses an arbitrary tangle of who-owes-whom into the minimum number of settle-up transactions using a greedy largest-creditor / largest-debtor matching algorithm (max-heaps, `O(n log n)`). This mirrors the approach real-world tools like Splitwise use — not a claim of provable optimality for every possible case (that variant is NP-hard), but the practical, industry-standard answer.

---

## Project structure

```
CashMap/
├── backend/
│   ├── app/
│   │   ├── authentication/   # JWT issuing, password hashing, auth dependency
│   │   ├── database/         # DB engine/session, Redis client, ORM models
│   │   ├── exceptions/       # custom exception handlers
│   │   ├── middleware/       # request middleware
│   │   └── routes/           # auth, groups, expenses, settlements, schemas
│   ├── Dockerfile
│   ├── main.py
│   └── requirements.txt
├── frontend/
│   └── Dockerfile
├── sql/
│   ├── init.sql               # schema DDL
│   └── Dockerfile
├── docker-compose.yml
└── README.md
```

---

## Running locally

```bash
git clone https://github.com/AnishAchutha05/CashMap.git
cd CashMap
cp backend/.env.example backend/.env   # fill in your own values
docker-compose up --build
```

API docs (Swagger UI) available at `http://localhost:8000/docs` once the core-api container is up.

---

## API overview

All routes are prefixed `/api/v1`. Full endpoint list, request/response shapes, and status code conventions are documented via the auto-generated Swagger UI at `/docs`.

| Area | Endpoints |
|---|---|
| Auth | register, login, refresh, logout |
| Groups | create, list, detail, join via invite code, balances, simplify-debts |
| Expenses | create, list (filterable + paginated), detail, edit (optimistic locking), delete |
| Settlements | create, list |
| Ops | `/health`, `/metrics` |

---

## Non-goals (v1)

Deliberately out of scope, to keep this buildable solo without derailing focus: real payment gateway integration, recurring expenses, multi-currency support, full microservices/service mesh, a mobile app, and group chat/trip planning.

---

## Status

Actively in development — backend built by hand (no AI-generated code) using trial and error against Swagger UI and browser devtools, as a deliberate learning exercise in backend and cloud engineering fundamentals.