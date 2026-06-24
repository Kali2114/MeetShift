# 🚀 MeetShift

![Checks](https://github.com/Kali2114/MeetShift/actions/workflows/checks.yml/badge.svg)
![Coverage](https://img.shields.io/badge/coverage-100%25-brightgreen)
![Python](https://img.shields.io/badge/Python-3.12-blue)
![Django](https://img.shields.io/badge/Django-5.x-green)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-blue)
![Docker](https://img.shields.io/badge/Docker-ready-blue)

MeetShift is a Django-based meeting management platform that helps users organize meetings, manage participants, handle invitations, and coordinate scheduling in a structured way.

The project was built to demonstrate backend development, testing practices, CI/CD automation, asynchronous task processing, and modern deployment workflows.

---

# ✨ Features

## 🔐 Authentication & Accounts

* User registration
* Login / Logout
* Password change
* Password reset via email
* Email confirmation after registration
* Account settings
* Account deletion

## 👤 User Profiles

* Public user profiles
* Profile editing
* Avatar uploads
* User bio

## 📅 Meeting Management

* Create meetings
* Edit meetings
* Delete meetings
* Meeting details view
* Meeting list view

## 👥 Participant Management

* Invite participants
* Accept invitations
* Decline invitations
* Invitation status tracking
* Organizer permissions

## 🔔 Notification System

* Meeting notifications
* Unread notification counter
* Mark notifications as read
* Notification history

## 📧 Email System

* Registration confirmation emails
* Asynchronous invitation emails
* Celery + Redis integration

## 🧪 Testing & Quality

* Test Driven Development (TDD)
* 100% test coverage
* Ruff linting
* Black formatting
* Pre-commit hooks

## ⚙️ CI/CD

* GitHub Actions
* Automated testing
* Automated linting
* Docker image build workflow

---

# 🏗️ Tech Stack

## Backend

* Python 3.12
* Django 5

## Database

* PostgreSQL

## Task Queue

* Celery
* Redis

## Frontend

* Django Templates
* HTML
* CSS
* JavaScript

## DevOps

* Docker
* Docker Compose
* GitHub Actions

---

# 📊 Project Architecture

```text
User
  │
  ▼
Django Application
  │
  ├── PostgreSQL
  │
  ├── Celery
  │
  └── Redis
```

CI/CD Pipeline:

```text
Git Push
   │
   ▼
GitHub Actions
   │
   ├── Ruff
   ├── Black
   ├── Tests
   └── Docker Build
```

---

# 🐳 Running the Project

## Clone Repository

```bash
git clone https://github.com/Kali2114/MeetShift.git
cd MeetShift
```

## Start Containers

```bash
docker compose up --build
```

## Run Tests

```bash
docker compose run --rm app sh -c "python manage.py test"
```

## Coverage

```bash
docker compose run --rm app sh -c "coverage run manage.py test"
docker compose run --rm app sh -c "coverage report"
```

---

# ⚙️ Environment Variables

Example:

```env
DEBUG=True
SECRET_KEY=your_secret_key

DB_HOST=db
DB_NAME=meetshift
DB_USER=postgres
DB_PASS=postgres
DB_PORT=5432

EMAIL_HOST=
EMAIL_PORT=
EMAIL_HOST_USER=
EMAIL_HOST_PASSWORD=
```

---

# 📌 Roadmap

## In Progress

* AWS Deployment
* Docker Hub Integration
* Automated Production Deployment
* Direct Messaging System
* Monitoring & Observability

## Planned

* Prometheus
* Grafana
* Google Calendar Integration
* REST API
* Mobile-Friendly UI

---

# 🎯 What This Project Demonstrates

* Django application architecture
* Authentication and authorization
* Relational database modeling
* Background task processing
* Email workflows
* Test Driven Development
* CI/CD pipelines
* Dockerized development workflow
* Production deployment preparation

---

# 👨‍💻 Author

**Kamil Kalicki**

Backend Developer focused on Python, Django, FastAPI, Docker, CI/CD and AWS.
