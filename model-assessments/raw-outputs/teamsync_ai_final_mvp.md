# TeamSync AI – Final Production MVP

## Project Overview

TeamSync AI is a complete multi-agent orchestration system with intelligent routing, continuous learning, and production-grade authentication. This final MVP integrates the full-stack architecture with the comprehensive auth system.

**Core Capabilities**:
- Intelligent task-to-agent routing with confidence scoring
- Dynamic capability learning (reputation, discovery, knowledge transfer)
- Role-based access control with 6 distinct roles
- Comprehensive audit logging for compliance
- Real-time WebSocket updates
- Strict one-output enforcement per task

---

## Architecture Diagram

```mermaid
graph TB
    subgraph Client["Frontend (Next.js)"]
        UI[React Dashboard]
        Auth[Auth Context]
        WS[WebSocket Client]
    end
    
    subgraph Gateway["API Gateway"]
        CORS[CORS]
        Rate[Rate Limiter]
        AuthM[Auth Middleware]
        RBAC[RBAC Checker]
        OneOut[One-Output Enforcement]
    end
    
    subgraph Backend["FastAPI Backend"]
        API[REST Endpoints]
        Router[Agent Router]
        Learning[Learning Systems]
        Auth[Auth Service]
        Audit[Audit Service]
    end
    
    subgraph Data["Data Layer"]
        PG[(PostgreSQL)]
        Redis[(Redis)]
        ES[Event Store]
    end
    
    Client --> Gateway
    Gateway --> Backend
    Backend --> Data
    Auth --> Redis
    Router --> Redis
```

### Authentication Flow

```mermaid
sequenceDiagram
    participant User
    participant Frontend
    participant Backend
    participant Redis
    participant Database
    
    User->>Frontend: Enter credentials
    Frontend->>Backend: POST /auth/login
    Backend->>Database: Verify Argon2id hash
    Backend->>Redis: Create session
    Backend->>Frontend: HttpOnly cookies
    Frontend->>Backend: Request with cookie
    Backend->>Redis: Check token blacklist
    Backend->>Database: Verify user + permissions
    Backend->>Frontend: Protected data
```

---

## Features Summary

### Backend Features
- **Agent Router**: Weighted multi-criteria matching with dynamic weights
- **Dynamic Weight Engine**: Context-aware routing
- **Reputation System**: Bayesian updating with confidence intervals
- **Capability Discovery**: Automatic implicit skill detection
- **Knowledge Transfer**: Pattern capture and suggestion
- **Team Optimizer**: Collaboration synergy calculation

### Authentication Features
- **Argon2id Password Hashing**: Industry-best password security
- **Redis Sessions**: Distributed session management with blacklisting
- **JWT Tokens**: Short-lived access (15min) + long-lived refresh (7days)
- **RBAC**: 6 roles with granular permissions
- **Audit Logging**: Full compliance trail

### Frontend Features
- **Dashboard**: Real-time metrics and agent status
- **Task Submission**: Full specification form
- **Agent Management**: CRUD with learning insights
- **Login/Logout**: Secure authentication flow

---

## Project Structure

```
team-sync-ai/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py              # FastAPI entry + lifespan
│   │   ├── config.py           # Settings + seed config
│   │   ├── models.py           # SQLAlchemy models
│   │   ├── schemas.py          # Pydantic schemas + RBAC
│   │   ├── db.py               # Database connection
│   │   ├── middleware.py       # One-output enforcement
│   │   ├── events.py           # Event sourcing
│   │   ├── api/
│   │   │   ├── __init__.py
│   │   │   ├── auth.py         # Login/logout/register
│   │   │   ├── agents.py       # Agent CRUD
│   │   │   ├── tasks.py        # Task submission
│   │   │   ├── metrics.py      # System metrics
│   │   │   └── seed.py         # Initial data seeding
│   │   └── services/
│   │       ├── __init__.py
│   │       ├── auth.py         # JWT + sessions
│   │       ├── audit.py        # Audit logging
│   │       ├── deps.py         # RBAC dependencies
│   │       ├── matching.py     # Routing engine
│   │       ├── reputation.py    # Bayesian reputation
│   │       ├── discovery.py    # Skill discovery
│   │       ├── knowledge.py     # Pattern transfer
│   │       └── team.py         # Collaboration optimizer
│   ├── tests/
│   ├── Dockerfile
│   ├── requirements.txt
│   └── .env.example
│
├── frontend/
│   ├── src/
│   │   ├── app/
│   │   │   ├── page.tsx
│   │   │   ├── layout.tsx
│   │   │   ├── login/
│   │   │   └── dashboard/
│   │   ├── components/
│   │   ├── lib/
│   │   │   ├── api.ts          # API client
│   │   │   ├── auth.ts         # Auth context
│   │   │   ├── websocket.ts    # WS client
│   │   │   └── store.ts        # Zustand store
│   │   └── types/
│   ├── public/
│   ├── package.json
│   ├── tailwind.config.ts
│   └── .env.example
│
├── docker-compose.yml
└── .env
```

---

## Backend Setup

### Requirements
- Python 3.11+
- PostgreSQL 15+
- Redis 7+

### Installation

```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
alembic upgrade head
uvicorn app.main:app --reload --port 8000
```

### Key Dependencies

```txt
fastapi==0.109.0
uvicorn[standard]==0.27.0
sqlalchemy==2.0.25
asyncpg==0.29.0
python-jose[cryptography]==3.3.0
pwdlib==0.2.0
redis==5.0.1
pydantic==2.5.3
pydantic-settings==2.1.0
python-multipart==0.0.6
websockets==12.0
```

---

## Frontend Setup

### Requirements
- Node.js 18+

### Installation

```bash
cd frontend
npm install
cp .env.example .env.local
npm run dev
```

Frontend available at `http://localhost:3000`.

---

## Full docker-compose.yml

```yaml
version: '3.8'

services:
  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    ports:
      - "3000:3000"
    environment:
      - NODE_ENV=production
      - NEXT_PUBLIC_API_URL=http://backend:8000
      - NEXT_PUBLIC_WS_URL=ws://backend:8000
    depends_on:
      - backend
    restart: unless-stopped
    networks:
      - teamsync-network

  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql+asyncpg://teamsync:teamsync@postgres:5432/teamsync
      - REDIS_URL=redis://redis:6379/0
      - SECRET_KEY=${SECRET_KEY:-teamsync-dev-secret-change-in-production}
      - ENVIRONMENT=production
      - DEBUG=false
      - CORS_ORIGINS=http://localhost:3000,http://frontend:3000
      - SEED_USERS=${SEED_USERS:-benjamin:admin:Benjamin@2025!,harper:agent_manager:Harper@2025!,lucas:task_submitter:Lucas@2025!,grok:model_internal:Grok@2025!,minimax:model_external:MiniMax@2025!,trinity:model_external:Trinity@2025!,codex:model_external:Codex@2025!,gemini:model_external:Gemini@2025!}
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
    volumes:
      - ./backend:/app
    restart: unless-stopped
    networks:
      - teamsync-network

  postgres:
    image: postgres:15-alpine
    environment:
      - POSTGRES_USER=teamsync
      - POSTGRES_PASSWORD=teamsync
      - POSTGRES_DB=teamsync
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U teamsync"]
      interval: 5s
      timeout: 5s
      retries: 5
    restart: unless-stopped
    networks:
      - teamsync-network

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 5s
      timeout: 3s
      retries: 5
    restart: unless-stopped
    networks:
      - teamsync-network

networks:
  teamsync-network:
    driver: bridge

volumes:
  postgres_data:
  redis_data:
```

### Backend Dockerfile

```dockerfile
FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY backend/ ./backend/

ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

EXPOSE 8000

CMD ["uvicorn", "backend.app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Frontend Dockerfile

```dockerfile
FROM node:18-alpine

WORKDIR /app

COPY frontend/package*.json ./
RUN npm ci

COPY frontend/ ./

ENV NODE_ENV=production

EXPOSE 3000

CMD ["npm", "start"]
```

---

## Environment Variables

### Backend .env

```bash
# Application
APP_NAME=TeamSync AI Router
DEBUG=false
ENVIRONMENT=production

# Database
DATABASE_URL=postgresql+asyncpg://teamsync:teamsync@localhost:5432/teamsync
DATABASE_POOL_SIZE=20

# Redis
REDIS_URL=redis://localhost:6379/0

# Security - CHANGE IN PRODUCTION
SECRET_KEY=your-secure-secret-key-min-32-chars
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=15
REFRESH_TOKEN_EXPIRE_DAYS=7

# CORS
CORS_ORIGINS=http://localhost:3000

# Session
MAX_SESSIONS_PER_USER=5

# Seed Users (format: username:role:password,...)
SEED_USERS=benjamin:admin:Benjamin@2025!,harper:agent_manager:Harper@2025!,lucas:task_submitter:Lucas@2025!,grok:model_internal:Grok@2025!,minimax:model_external:MiniMax@2025!,trinity:model_external:Trinity@2025!,codex:model_external:Codex@2025!,gemini:model_external:Gemini@2025!
```

### Frontend .env.local

```bash
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_WS_URL=ws://localhost:8000
```

---

## Seed Users & Login Credentials

### Team Members

| Username | Password | Role | Description |
|----------|----------|------|-------------|
| Benjamin | Benjamin@2025! | admin | System Administrator |
| Harper | Harper@2025! | agent_manager | Agent Management |
| Lucas | Lucas@2025! | task_submitter | Task Submission |

### AI Models

| Username | Password | Role | Description |
|----------|----------|------|-------------|
| Grok | Grok@2025! | model_internal | Internal AI Model |
| MiniMax | MiniMax@2025! | model_external | External AI Model |
| Trinity | Trinity@2025! | model_external | External AI Model |
| Codex | Codex@2025! | model_external | External AI Model |
| Gemini | Gemini@2025! | model_external | External AI Model |

### Permission Matrix

| Role | Tasks | Agents | Users | Audit | Learning |
|------|-------|--------|-------|-------|----------|
| admin | Full | Full | Full | Full | Full |
| agent_manager | Create/Read | Full | Read | - | Read |
| task_submitter | Create/Read | Read | - | - | Read |
| model_internal | Execute | Read | - | - | Transfer |
| model_external | Execute | - | - | - | - |
| viewer | Read | Read | - | - | Read |

---

## End-to-End Demo

### Quick Start

```bash
git clone https://github.com/yourorg/team-sync-ai.git
cd team-sync-ai
cp .env.example .env
docker-compose up -d --build
docker-compose ps
```

### Demo Flow

#### 1. Health Check

```bash
curl http://localhost:8000/health
# {"status":"healthy","service":"TeamSync AI Router"}
```

#### 2. Login as Benjamin (Admin)

```bash
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "benjamin", "password": "Benjamin@2025!"}' \
  -c cookies.txt -v
```

#### 3. Check Auth Status

```bash
curl http://localhost:8000/auth/me -b cookies.txt
# {"id": "...", "username": "benjamin", "roles": ["admin"], ...}
```

#### 4. List Agents

```bash
curl http://localhost:8000/api/agents -b cookies.txt
```

#### 5. Submit a Task

```bash
curl -X POST http://localhost:8000/api/tasks/submit \
  -H "Content-Type: application/json" \
  -b cookies.txt \
  -d '{
    "intent": "Create React login form",
    "description": "Build login component",
    "domains": ["frontend"],
    "task_types": ["implementation"],
    "tools": ["react", "typescript"],
    "output_file": "LoginForm.tsx",
    "complexity": "moderate",
    "priority": "high"
  }'
```

#### 6. Check Learning Status

```bash
curl http://localhost:8000/api/learning/status -b cookies.txt
```

#### 7. View Audit Logs (Admin)

```bash
curl http://localhost:8000/api/audit?action=login -b cookies.txt
```

#### 8. Logout

```bash
curl -X POST http://localhost:8000/auth/logout \
  -H "Content-Type: application/json" \
  -b cookies.txt \
  -d '{"all_sessions": false}'
```

### Frontend Demo

1. Open `http://localhost:3000`
2. Login with credentials above
3. View dashboard with agent status
4. Submit a task via form
5. Watch real-time execution updates
6. Explore learning insights

---

## Deployment Notes

### Production Checklist

- [ ] Change SECRET_KEY to secure random value
- [ ] Configure CORS_ORIGINS for production domain
- [ ] Enable HTTPS/TLS
- [ ] Set up monitoring (Prometheus, Grafana)
- [ ] Configure log aggregation
- [ ] Set up backup for PostgreSQL
- [ ] Configure Redis persistence

### Scaling

| Component | Single Server | Production |
|-----------|--------------|------------|
| Frontend | 1 instance | 3+ behind LB |
| Backend | 2-4 workers | 10+ K8s |
| PostgreSQL | Primary | Primary + Replicas |
| Redis | Single | Sentinel |

---

## Future Roadmap

### Phase 1: Core (Current)
- [x] Agent routing with learning
- [x] Authentication (Argon2id + RBAC)
- [x] Audit logging
- [x] Docker deployment

### Phase 2: Enhanced Features
- [ ] MFA enforcement
- [ ] SSO integration
- [ ] Advanced analytics
- [ ] Team collaboration graphs

### Phase 3: Production Hardening
- [ ] Rate limiting per user
- [ ] API versioning
- [ ] Comprehensive monitoring
- [ ] CI/CD pipelines

### Phase 4: Scale & Optimize
- [ ] Multi-region deployment
- [ ] Advanced caching
- [ ] ML-based optimization
- [ ] Custom integrations

---

## Quick Reference

### Commands

```bash
# Start stack
docker-compose up -d

# View logs
docker-compose logs -f

# Stop stack
docker-compose down

# Rebuild
docker-compose build --no-cache
```

### API Endpoints

| Endpoint | Method | Auth | Description |
|----------|--------|------|-------------|
| /auth/login | POST | No | Login |
| /auth/logout | POST | Yes | Logout |
| /auth/me | GET | Yes | Current user |
| /api/agents | GET | Yes | List agents |
| /api/tasks/submit | POST | Yes | Submit task |
| /api/metrics | GET | Yes | System metrics |
| /api/learning/status | GET | Yes | Learning config |
| /api/audit | GET | Admin | Audit logs |
| /ws | WS | Optional | Real-time events |

**TeamSync AI MVP Ready for Deployment**.
