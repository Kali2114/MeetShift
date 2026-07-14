# 🚀 MeetShift

![Checks](https://github.com/Kali2114/MeetShift/actions/workflows/checks.yml/badge.svg)
[![codecov](https://codecov.io/github/Kali2114/MeetShift/graph/badge.svg?token=UZ4HIOYQY7)](https://codecov.io/github/Kali2114/MeetShift)
![Python](https://img.shields.io/badge/Python-3.12-blue?logo=python)
![Django](https://img.shields.io/badge/Django-5.x-092E20?logo=django)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16%20%7C%2017-336791?logo=postgresql)
![Docker](https://img.shields.io/badge/Docker-ready-2496ED?logo=docker)
![AWS](https://img.shields.io/badge/AWS-EC2-FF9900?logo=amazonaws)
![CI/CD](https://img.shields.io/badge/CI%2FCD-GitHub%20Actions-2088FF?logo=githubactions)
![Prometheus](https://img.shields.io/badge/Prometheus-Monitoring-E6522C?logo=prometheus)
![Grafana](https://img.shields.io/badge/Grafana-Dashboards-F46800?logo=grafana)
![Loki](https://img.shields.io/badge/Loki-Logging-F46800?logo=grafana)
![License](https://img.shields.io/github/license/Kali2114/MeetShift)

> **Production meeting scheduling application built with Django, Docker, AWS and a complete CI/CD and observability stack.**

MeetShift is a meeting scheduling application that allows users to create meetings, invite participants, manage invitation responses and receive notifications.

The project was created to simulate a real-world backend system. Its scope includes not only application features, but also automated testing, containerization, production deployment, CI/CD, monitoring, centralized logging and secure infrastructure management.

🌍 **Live application:** [https://meetshift.org](https://meetshift.org)

---

## 📸 Screenshots

> Coming soon

Planned screenshots:

- meeting list,
- meeting details,
- calendar,
- user profile,
- notifications,
- Grafana dashboards,
- Loki logs,
- GitHub Actions deployment pipeline.

---

## ✨ Features

- 🔐 User registration, login and authorization
- 👤 User profiles with avatar uploads
- ⚙️ Account and password management
- 📅 Meeting creation, editing and deletion
- 🗓 Calendar interface
- 👥 Participant invitations
- ✅ Accepting and declining invitations
- 🔔 In-app notification system
- 📧 Email notifications
- ⚡ Background task processing with Celery
- 📂 Persistent media and static files
- 🔒 HTTPS and Cloudflare proxy
- 📊 Application metrics and dashboards
- 🧾 Centralized container logging
- 🚀 Automated deployment to AWS

---

## 🏗 Architecture

```text
                             Internet
                                 │
                                 ▼
                       Cloudflare DNS / HTTPS
                                 │
                                 ▼
                         AWS EC2 — Ubuntu
                                 │
                                 ▼
                              Nginx
                                 │
                                 ▼
                             Gunicorn
                                 │
                                 ▼
                              Django
                    ┌────────────┴────────────┐
                    ▼                         ▼
               PostgreSQL                  Redis
                                               │
                                               ▼
                                            Celery


        Prometheus ───────────────► Grafana dashboards

        Docker containers ─► Promtail ─► Loki ─► Grafana logs
```

### Deployment flow

```text
git push to main
        │
        ▼
GitHub Actions
        │
        ├── Black
        ├── Ruff
        ├── Django checks
        ├── Migration validation
        ├── Tests and coverage
        └── PostgreSQL 16 / 17 matrix
        │
        ▼
Docker image build
        │
        ▼
Docker Hub
        │
        ▼
GitHub OpenID Connect
        │
        ▼
AWS Systems Manager
        │
        ▼
EC2 deployment
        │
        ├── Pull new application image
        ├── Recreate Django and Celery containers
        ├── Run migrations
        ├── Collect static files
        ├── Restart Nginx
        └── Production health check
```

---

## 🛠 Tech Stack

### Backend

- Python 3.12
- Django 5
- Gunicorn
- Celery

### Database and messaging

- PostgreSQL
- Redis

### Infrastructure

- Docker
- Docker Compose
- AWS EC2
- AWS Systems Manager
- AWS IAM
- GitHub OpenID Connect
- Nginx
- Cloudflare

### Monitoring and logging

- Prometheus
- Grafana
- Loki
- Promtail
- Django logging

### Testing and quality

- Django Test Framework
- Coverage.py
- Codecov
- Ruff
- Black
- pre-commit

### CI/CD

- GitHub Actions
- Docker Buildx
- GitHub Actions cache
- Docker Hub
- AWS Systems Manager Run Command

---

## 🚀 Production Infrastructure

MeetShift runs on an AWS EC2 instance using Docker Compose.

The production environment contains:

- Django application served by Gunicorn
- Nginx reverse proxy
- PostgreSQL database
- Redis message broker
- Celery worker
- Prometheus
- Grafana
- Loki
- Promtail
- persistent Docker volumes
- Cloudflare DNS and HTTPS
- automated deployment through GitHub Actions

The application and Celery worker use the same versioned Docker image published to Docker Hub.

The EC2 server does not build the application image locally. It pulls an image that has already passed the complete CI pipeline.

---

## 🔐 Secure AWS Deployment

Production deployment does not require an SSH connection from GitHub Actions.

GitHub Actions authenticates with AWS through **OpenID Connect**, which provides temporary AWS credentials without storing permanent AWS access keys.

Deployment commands are sent to the EC2 instance using **AWS Systems Manager Run Command**.

```text
GitHub Actions
      │
      ▼
GitHub OIDC token
      │
      ▼
AWS IAM deployment role
      │
      ▼
AWS Systems Manager
      │
      ▼
MeetShift EC2 instance
```

Security benefits:

- no private EC2 key stored in GitHub,
- no permanent AWS access keys,
- SSH does not need to be open to GitHub runners,
- the IAM role is restricted to this repository,
- the role can only be assumed from the `main` branch,
- deployment permissions are limited to the selected EC2 instance.

---

## 🔄 Continuous Integration and Deployment

The GitHub Actions workflow runs automatically on pushes and pull requests.

### Continuous Integration

The pipeline performs:

- Docker container build
- Black formatting validation
- Ruff linting
- Django system checks
- missing migration detection
- automated tests
- coverage report generation
- Codecov upload
- PostgreSQL compatibility tests

Tests are executed against:

```text
PostgreSQL 16.2
PostgreSQL 17
```

### Continuous Deployment

Deployment runs only after all CI jobs complete successfully and only for pushes to the `main` branch.

```text
test-lint
    │
    ▼
build-image
    │
    ▼
deploy
```

The deployment job:

1. authenticates with AWS through OIDC,
2. sends a command through AWS Systems Manager,
3. pulls the latest application image,
4. recreates the Django and Celery containers,
5. runs migrations and `collectstatic`,
6. restarts Nginx,
7. performs a production health check.

A failed test or build prevents production deployment.

---

## 📊 Monitoring

Application metrics are collected by Prometheus and visualized in Grafana.

Available metrics include:

- HTTP request count
- response status codes
- request duration
- request throughput
- server error rate
- application health
- endpoint performance

The monitoring stack helps detect application failures, increased latency and abnormal traffic patterns.

---

## 🧾 Centralized Logging

MeetShift uses Loki and Promtail for centralized container logs.

```text
Docker containers
        │
        ▼
     Promtail
        │
        ▼
       Loki
        │
        ▼
     Grafana
```

Logs can be filtered by service, including:

- Django application
- Gunicorn
- Nginx
- Celery
- PostgreSQL
- Redis
- Prometheus
- Grafana

This makes it possible to inspect production errors without connecting directly to every container.

---

## 🐳 Docker

### Development

```bash
docker compose up --build
```

### Production

```bash
docker compose -f docker-compose.prod.yml up -d
```

### Production status

```bash
docker compose -f docker-compose.prod.yml ps
```

### Application logs

```bash
docker compose -f docker-compose.prod.yml logs --tail=100 app
```

### Celery logs

```bash
docker compose -f docker-compose.prod.yml logs --tail=100 celery
```

---

## ⚙️ Local Installation

### 1. Clone the repository

```bash
git clone https://github.com/Kali2114/MeetShift.git
cd MeetShift
```

### 2. Create the environment file

```bash
cp .env.example .env
```

Fill in the required environment variables.

### 3. Start the application

```bash
docker compose up --build
```

### 4. Open the application

```text
http://localhost:8000
```

---

## 🧪 Testing

Tests should be executed inside the application container.

```bash
docker compose run --rm app sh -c \
  "python manage.py wait_for_db && python manage.py test"
```

Run tests with coverage:

```bash
docker compose run --rm app sh -c \
  "coverage run manage.py test && coverage report"
```

Generate an HTML coverage report:

```bash
docker compose run --rm app sh -c \
  "coverage run manage.py test && coverage html"
```

The project maintains test coverage close to **100%**.

---

## ✅ Code Quality

Run Black:

```bash
docker compose run --rm app sh -c "black --check ."
```

Run Ruff:

```bash
docker compose run --rm app sh -c "ruff check ."
```

Run pre-commit hooks:

```bash
pre-commit run --all-files
```

---

## 📁 Project Structure

```text
MeetShift/
│
├── config/                         # Django configuration
├── core/                           # Core models, utilities and tasks
├── meeting/                        # Meeting management
├── user/                           # Authentication, profiles and notifications
├── monitoring/
│   ├── grafana/
│   │   ├── dashboards/
│   │   └── provisioning/
│   ├── loki/
│   ├── promtail/
│   └── prometheus.yml
├── nginx/
│   ├── nginx.conf
│   └── certs/
├── scripts/
├── backups/
├── .github/
│   └── workflows/
│       └── checks.yml
├── docker-compose.yml
├── docker-compose.prod.yml
├── Dockerfile
├── manage.py
├── pyproject.toml
└── README.md
```

---

## 🛣 Roadmap

### ✅ Completed

- User authentication and authorization
- User profiles and avatar uploads
- Account and password management
- Meeting management
- Participant invitations
- Invitation responses
- Notification system
- Email integration
- Calendar interface
- Celery background tasks
- Docker and Docker Compose
- Gunicorn and Nginx
- AWS EC2 deployment
- Cloudflare and HTTPS
- Prometheus monitoring
- Grafana dashboards
- Loki centralized logging
- Promtail log collection
- PostgreSQL 16 and 17 CI matrix
- Coverage and Codecov
- Docker image publishing
- Automated CI/CD deployment
- GitHub OpenID Connect authentication
- AWS Systems Manager deployment
- Production health check

### 🚧 Planned

- Grafana alerting
- Application availability alerts
- HTTP 500 error alerts
- Resource usage alerts
- Improved Loki dashboards
- User interface polishing
- Additional performance optimization
- Production deployment rollback
- Release `v1.0.0`

---

## 👨‍💻 Author

**Kamil Kalicki**

- GitHub: [Kali2114](https://github.com/Kali2114)
- LinkedIn: [Kamil Kalicki](https://www.linkedin.com/in/kamil-kalicki-047968245/)

---

## ⭐ Support

If you find this project interesting, consider giving it a star on GitHub.

Feedback and suggestions are welcome.
