# 🚀 MeetShift

![Checks](https://github.com/Kali2114/MeetShift/actions/workflows/checks.yml/badge.svg)
[![codecov](https://codecov.io/github/Kali2114/MeetShift/graph/badge.svg?token=UZ4HIOYQY7)](https://codecov.io/github/Kali2114/MeetShift)
![Python](https://img.shields.io/badge/Python-3.12-blue?logo=python)
![Django](https://img.shields.io/badge/Django-5.x-092E20?logo=django)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16%20%7C%2017-336791?logo=postgresql)
![Docker](https://img.shields.io/badge/Docker-ready-2496ED?logo=docker)
![License](https://img.shields.io/github/license/Kali2114/MeetShift)
![Matrix](https://img.shields.io/badge/CI%20matrix-PostgreSQL%2016%20%7C%2017-blue)

A production-oriented Django application demonstrating modern backend development practices including Docker, CI/CD, automated testing, Celery, Redis, Codecov, and cloud deployment preparation.

---

# ✨ Features

## 🔐 Authentication & Accounts

- User registration
- Login / Logout
- Password change
- Password reset via email
- Email confirmation after registration
- Account settings
- Account deletion

## 👤 User Profiles

- Public user profiles
- Profile editing
- Avatar uploads
- User bio

## 📅 Meeting Management

- Create meetings
- Edit meetings
- Delete meetings
- Meeting details
- Meeting list

## 👥 Participant Management

- Invite participants
- Accept invitations
- Decline invitations
- Invitation status tracking
- Organizer permissions

## 🔔 Notification System

- Meeting notifications
- Unread notification counter
- Mark notifications as read
- Notification history

## 📧 Email System

- Registration confirmation emails
- Asynchronous invitation emails
- Celery + Redis integration

## 🧪 Testing & Quality

- Test Driven Development (TDD)
- 100% test coverage
- Ruff linting
- Black formatting
- Pre-commit hooks
- Codecov integration

## ⚙️ CI/CD

- GitHub Actions
- Black formatting checks
- Ruff linting
- Django system checks
- Migration validation
- Automated test suite
- Coverage XML generation
- Coverage HTML artifacts
- Codecov reporting
- Docker Buildx cache
- Docker image build
- Docker Hub publishing

## 📊 Monitoring

- Prometheus metrics endpoint
- Grafana dashboard provisioning
- Django request monitoring
- HTTP status monitoring
- Response time tracking
- CPU and memory usage metrics

---

# 🏗️ Tech Stack

## Backend

- Python 3.12
- Django 5

## Database

- PostgreSQL

## Background Tasks

- Celery
- Redis

## Frontend

- Django Templates
- HTML
- CSS
- JavaScript

## DevOps

- Docker
- Docker Compose
- GitHub Actions
- Docker Buildx
- Codecov
- Prometheus
- Graphana
- Provisioned monitoring dashboard

---

# 📊 Project Architecture

```text
                User
                  │
                  ▼
          Django Application
                  │
     ┌────────────┼────────────┐
     │            │            │
     ▼            ▼            ▼
 PostgreSQL     Redis       Celery
                  │
                  ▼
        Background Tasks
```

## CI/CD Pipeline

```text
Git Push
    │
    ▼
GitHub Actions
    │
    ├── Black
    ├── Ruff
    ├── Django Check
    ├── Migration Check
    ├── Tests
    ├── Coverage
    ├── Upload HTML Artifact
    ├── Codecov
    └── Docker Build & Push
```

---

# 🐳 Running the Project

## Clone repository

```bash
git clone https://github.com/Kali2114/MeetShift.git
cd MeetShift
```

## Build containers

```bash
docker compose up --build
```

## Run tests

```bash
docker compose run --rm app sh -c "python manage.py test"
```

## Coverage

```bash
docker compose run --rm app sh -c "coverage run manage.py test"
docker compose run --rm app sh -c "coverage report"
docker compose run --rm app sh -c "coverage html"
```

---

# ⚙️ Environment Variables

```env
DEBUG=True

SECRET_KEY=

DB_HOST=db
DB_NAME=
DB_USER=
DB_PASS=
DB_PORT=5432

EMAIL_HOST=
EMAIL_PORT=
EMAIL_HOST_USER=
EMAIL_HOST_PASSWORD=
EMAIL_USE_TLS=True
DEFAULT_FROM_EMAIL=
```

---

# 📌 Roadmap

## 🚧 In Progress

- AWS EC2 deployment
- Nginx reverse proxy
- Prometheus monitoring
- Grafana dashboards
- Production logging

## 📋 Planned

- Google Calendar integration
- Direct messaging
- REST API
- Mobile-friendly UI

---

# 🎯 What This Project Demonstrates

- Django application architecture
- Authentication & authorization
- Relational database modeling
- Background task processing
- Email workflows
- Docker containerization
- Docker image publishing
- Test Driven Development
- Continuous Integration
- Code coverage reporting
- Production-ready project structure
- Cloud deployment preparation

---

# 👨‍💻 Author

**Kamil Kalicki**

Backend Developer focused on Python, Django, FastAPI, Docker, CI/CD and AWS.
