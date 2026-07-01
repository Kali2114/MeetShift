# 🚀 MeetShift

![Checks](https://github.com/Kali2114/MeetShift/actions/workflows/checks.yml/badge.svg)
[![codecov](https://codecov.io/github/Kali2114/MeetShift/graph/badge.svg?token=UZ4HIOYQY7)](https://codecov.io/github/Kali2114/MeetShift)
![Python](https://img.shields.io/badge/Python-3.12-blue?logo=python)
![Django](https://img.shields.io/badge/Django-5.x-092E20?logo=django)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16%20%7C%2017-336791?logo=postgresql)
![Docker](https://img.shields.io/badge/Docker-ready-2496ED?logo=docker)
![AWS](https://img.shields.io/badge/AWS-EC2-FF9900?logo=amazonaws)
![Prometheus](https://img.shields.io/badge/Prometheus-Monitoring-E6522C?logo=prometheus)
![Grafana](https://img.shields.io/badge/Grafana-Dashboard-F46800?logo=grafana)
![License](https://img.shields.io/github/license/Kali2114/MeetShift)
![Matrix](https://img.shields.io/badge/CI%20matrix-PostgreSQL%2016%20%7C%2017-blue)

> **Production-ready meeting scheduling application built with Django, Docker, AWS, and modern DevOps practices.**

MeetShift is a production-ready meeting scheduling application that allows users to create meetings, invite participants, manage responses, and receive notifications.

The project was built to simulate a real-world backend application, focusing not only on features but also on deployment, infrastructure, monitoring, testing, and DevOps practices.

🌍 **Live Demo:** https://meetshift.org

---

# 📸 Screenshots

> *(Coming soon)*

- Home page
- Meeting details
- User profile
- Notifications
- Grafana dashboard
- Production infrastructure

---

# ✨ Features

- 🔐 Authentication & authorization
- 👤 User profiles with avatar uploads
- 📅 Meeting scheduling
- 👥 Participant invitations
- 🔔 Notification system
- 📧 Email integration
- 📂 Media uploads
- 🗓 Calendar interface
- ⚡ Background task processing with Celery
- 🔒 HTTPS with Cloudflare
- 📊 Production monitoring
- 🐳 Dockerized deployment

---

# 🏗 Architecture

```text
                         Internet
                              │
                              ▼
                      Cloudflare (HTTPS)
                              │
                              ▼
                     AWS EC2 (Ubuntu)
                              │
                              ▼
                           Nginx
                              │
                              ▼
                         Gunicorn
                              │
                              ▼
                            Django
                     ┌────────┴────────┐
                     ▼                 ▼
               PostgreSQL          Redis
                                        │
                                        ▼
                                     Celery

                   Prometheus ─────► Grafana
```

---

# 🛠 Tech Stack

## Backend

- Python 3.12
- Django
- Gunicorn
- Celery

## Database

- PostgreSQL

## Cache & Background Tasks

- Redis
- Celery

## Infrastructure

- Docker
- Docker Compose
- AWS EC2
- Nginx
- Cloudflare

## Monitoring

- Prometheus
- Grafana

## Testing

- Django Test Framework
- Coverage.py

## Code Quality

- Ruff
- Black
- pre-commit

## Continuous Integration

- GitHub Actions

---

# 🚀 Production Infrastructure

MeetShift is deployed on AWS using a production-ready Docker environment.

Infrastructure includes:

- AWS EC2
- Docker Compose
- Gunicorn WSGI server
- Nginx reverse proxy
- PostgreSQL
- Redis
- Celery workers
- Cloudflare DNS
- HTTPS (SSL)
- Prometheus
- Grafana

---

# 📊 Monitoring

Application monitoring is powered by **Prometheus** and **Grafana**.

Collected metrics include:

- HTTP requests
- Response status codes
- Request throughput
- Response time
- Error rates
- Application health

Monitoring provides real-time insights into application performance and infrastructure.

---

# 🐳 Docker

## Development

```bash
docker compose up --build
```

## Production

```bash
docker compose -f docker-compose.prod.yml up -d
```

---

# ⚙️ Local Installation

Clone the repository

```bash
git clone https://github.com/Kali2114/MeetShift.git
```

Go to the project

```bash
cd MeetShift
```

Create environment file

```bash
cp .env.example .env
```

Start the application

```bash
docker compose up --build
```

---

# 🧪 Testing

Run tests

```bash
python manage.py test
```

Run coverage

```bash
coverage run manage.py test
coverage report
```

Current test coverage is close to **100%**.

---

# 🔄 Continuous Integration

GitHub Actions automatically performs:

- Ruff linting
- Black formatting check
- Django tests
- Coverage
- Docker build validation
- PostgreSQL matrix builds

---

# 📁 Project Structure

```text
MeetShift
│
├── app/
├── monitoring/
│   ├── grafana/
│   └── prometheus.yml
├── nginx/
├── docker-compose.yml
├── docker-compose.prod.yml
├── requirements.txt
└── README.md
```

---

# 🛣 Roadmap

## ✅ Completed

- User authentication
- User profiles
- Avatar uploads
- Meeting management
- Invitations
- Notifications
- Docker
- AWS deployment
- HTTPS
- Prometheus
- Grafana
- GitHub Actions
- Production monitoring

## 🚧 Planned

- Automated CI/CD deployment
- Database backups
- Centralized logging
- Sentry integration
- Performance optimization
- Infrastructure improvements
- API versioning
- Release **v1.0.0**

---

# 👨‍💻 Author

**Kamil Kalicki**

GitHub

https://github.com/Kali2114

LinkedIn

*(coming soon)*

---

# ⭐ Support

If you found this project interesting, consider giving it a ⭐ on GitHub!

Feedback, suggestions, and contributions are always welcome.
