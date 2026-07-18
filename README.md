# 🚀 MeetShift

![Checks](https://github.com/Kali2114/MeetShift/actions/workflows/checks.yml/badge.svg)
![CodeQL](https://github.com/Kali2114/MeetShift/actions/workflows/codeql.yml/badge.svg)
![Trivy](https://github.com/Kali2114/MeetShift/actions/workflows/trivy.yml/badge.svg)
[![codecov](https://codecov.io/github/Kali2114/MeetShift/graph/badge.svg?token=UZ4HIOYQY7)](https://codecov.io/github/Kali2114/MeetShift)

![Python](https://img.shields.io/badge/Python-3.12-blue?logo=python)
![Django](https://img.shields.io/badge/Django-5.x-092E20?logo=django)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16%20%7C%2017-336791?logo=postgresql)
![Docker](https://img.shields.io/badge/Docker-ready-2496ED?logo=docker)
![AWS](https://img.shields.io/badge/AWS-EC2-FF9900?logo=amazonaws)
![Terraform](https://img.shields.io/badge/Terraform-IaC-844FBA?logo=terraform)
![Prometheus](https://img.shields.io/badge/Prometheus-Monitoring-E6522C?logo=prometheus)
![Grafana](https://img.shields.io/badge/Grafana-Alerting-F46800?logo=grafana)
![Loki](https://img.shields.io/badge/Loki-Logging-F46800?logo=grafana)

> **Production meeting scheduling application built with Django, Docker, AWS, Terraform and a complete CI/CD, security and observability stack.**

MeetShift allows users to create meetings, invite participants, manage invitation responses and receive real-time notifications.

The project demonstrates the complete lifecycle of a production backend application: development, automated testing, containerization, infrastructure as code, deployment, monitoring, security scanning, backup verification and rollback.

🌍 **Live application:** [https://meetshift.org](https://meetshift.org)

---

## ✨ Features

- User registration, login and authorization
- User profiles with avatar uploads
- Account and password management
- Meeting creation, editing and deletion
- Calendar interface
- Participant invitations
- Accepting and declining invitations
- E-mail notifications
- Background tasks with Celery
- Real-time WebSocket notifications
- Live notification badge updates
- Persistent media and static files
- HTTPS through Cloudflare
- Automated AWS deployment
- Monitoring, alerting and centralized logging
- Database backup and restore verification
- Manual production rollback

---

## ⚡ Real-time Notifications

MeetShift uses WebSockets to deliver notifications without requiring a page refresh.

```text
Application event
      │
      ▼
Django creates notification
      │
      ▼
Django Channels
      │
      ▼
Redis channel layer
      │
      ▼
WebSocket connection
      │
      ▼
Browser notification
```

Real-time updates include:

- new notification messages,
- notification toast messages,
- live navbar badge updates,
- immediate delivery without refreshing the page.

Redis is shared by Celery and the Django Channels layer.

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
                   ┌─────────┴─────────┐
                   ▼                   ▼
              Gunicorn              WebSocket
                   │                   │
                   ▼                   ▼
                Django          Django Channels
                   │                   │
          ┌────────┴────────┐          │
          ▼                 ▼          ▼
     PostgreSQL           Redis ◄──────┘
                             │
                             ▼
                          Celery


Django metrics ─► Prometheus ─► Grafana dashboards and alerts

Docker logs ─► Promtail ─► Loki ─► Grafana
```

---

## 🛠 Tech Stack

### Backend

- Python 3.12
- Django 5
- Django Channels
- Gunicorn
- Celery

### Database and messaging

- PostgreSQL
- Redis

### Infrastructure

- Docker
- Docker Compose
- Terraform
- AWS EC2
- AWS Systems Manager
- AWS IAM
- GitHub OpenID Connect
- Nginx
- Cloudflare

### Monitoring and logging

- Prometheus
- Grafana
- Grafana Alerting
- Loki
- Promtail

### Testing and security

- Django Test Framework
- Testinfra
- Coverage.py
- Codecov
- Black
- Ruff
- pre-commit
- CodeQL
- Trivy
- Dependabot
- Dependency Review

---

## 🚀 CI/CD and Deployment

GitHub Actions runs for pull requests targeting `main` and pushes to `main`.

```text
Pull request
     │
     ▼
Black / Ruff / Django checks
     │
     ▼
PostgreSQL 16 and 17 tests
     │
     ▼
Coverage / CodeQL / Trivy
     │
     ▼
Dependency Review
     │
     ▼
Merge to main
     │
     ▼
Docker image build
     │
     ▼
Docker Hub
     │
     ▼
AWS OIDC
     │
     ▼
AWS Systems Manager
     │
     ▼
EC2 deployment
     │
     ▼
Production health check
```

Production images are tagged as:

```text
kali2114/meetshift:latest
kali2114/meetshift:<commit-sha>
```

The EC2 instance pulls images that have already passed the CI and security pipelines.

---

## ↩️ Production Rollback

A manually triggered GitHub Actions workflow can roll production back to a previous Docker image.

The workflow:

1. accepts a Docker image tag or full commit SHA,
2. authenticates with AWS through OIDC,
3. sends commands through AWS Systems Manager,
4. pulls the selected image,
5. recreates Django and Celery containers,
6. restarts Nginx,
7. performs a production health check.

Rollback changes the running application image. It does not automatically restore the database.

---

## 🏗 Infrastructure as Code

Existing AWS resources were imported into Terraform.

Terraform configuration covers:

- EC2 instance
- Security Group
- Elastic IP
- provider configuration
- variables and outputs

```text
terraform/
├── main.tf
├── providers.tf
├── variables.tf
├── outputs.tf
└── terraform.tfvars.example
```

Before applying infrastructure changes:

```bash
cd terraform
terraform fmt -check
terraform validate
terraform plan
```

Infrastructure changes are applied only after reviewing the plan.

---

## 🔐 Security

MeetShift includes:

- GitHub OIDC authentication for AWS
- no permanent AWS access keys in GitHub
- deployment through AWS Systems Manager
- CodeQL analysis for Python and GitHub Actions
- Trivy Docker image scanning
- Trivy Terraform scanning
- Dependency Review
- Dependabot updates
- branch protection for `main`
- required IMDSv2 on EC2
- authentication event logging

Passwords, tokens and complete login credentials are never written to application logs.

---

## 📊 Monitoring and Alerting

Prometheus collects Django application metrics and Grafana displays dashboards.

Configured alerts include:

### Application unavailable

```text
up{job="django", instance="app:8000"} < 1
for 2 minutes
```

### HTTP 5xx errors

```promql
sum(
  increase(
    django_http_responses_total_by_status_total{
      job="django",
      instance="app:8000",
      status=~"5.."
    }[5m]
  )
) or vector(0)
```

The HTTP error alert fires when more than two server errors occur within five minutes.

Alert rules and the e-mail contact point are provisioned from YAML files stored in the repository.

---

## 🧾 Centralized Logging

Promtail collects Docker container logs and sends them to Loki.

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

- Django
- Gunicorn
- Nginx
- Celery
- PostgreSQL
- Redis
- Prometheus
- Grafana

Authentication events include:

- successful login,
- failed login attempt,
- logout.

---

## 💾 Database Backup and Restore

MeetShift includes scripts for creating, restoring and verifying PostgreSQL backups.

```text
scripts/
├── backup_db.sh
├── restore_db.sh
└── verify_backup.sh
```

Create a backup:

```bash
./scripts/backup_db.sh
```

Restore a backup:

```bash
./scripts/restore_db.sh \
  backups/meetshift_<timestamp>.sql.gz \
  target_database
```

Verify the latest backup:

```bash
./scripts/verify_backup.sh
```

The verification script restores the backup into a temporary database, checks required tables and data, and removes the temporary database afterward.

Off-site S3 storage is intentionally not enabled to minimize infrastructure costs.

---

## 🧪 Testing

Run all application tests:

```bash
docker compose run --rm app sh -c \
  "python manage.py wait_for_db && python manage.py test"
```

Run tests with coverage:

```bash
docker compose run --rm app sh -c \
  "python manage.py wait_for_db &&
   coverage run manage.py test &&
   coverage report"
```

Run infrastructure tests:

```bash
pytest --connection=local tests_infra/local/
```

The project contains more than 130 automated tests and maintains coverage close to 100%.

---

## 🐳 Local Development

Clone the repository:

```bash
git clone https://github.com/Kali2114/MeetShift.git
cd MeetShift
```

Create the environment file:

```bash
cp .env.example .env
```

Start the application:

```bash
docker compose up --build
```

Open:

```text
http://localhost:8000
```

---

## ✅ Code Quality

```bash
docker compose run --rm app sh -c "black --check ."
docker compose run --rm app sh -c "ruff check . --no-cache"
pre-commit run --all-files
```

---

## 📁 Project Structure

```text
MeetShift/
├── app/
│   ├── config/
│   ├── core/
│   ├── meeting/
│   ├── user/
│   └── manage.py
├── monitoring/
│   ├── grafana/
│   ├── loki/
│   ├── promtail/
│   └── prometheus.yml
├── nginx/
├── scripts/
├── terraform/
├── tests_infra/
├── .github/
│   ├── dependabot.yml
│   └── workflows/
├── docker-compose.yml
├── docker-compose.prod.yml
├── Dockerfile
├── requirements.txt
├── requirements-dev.txt
├── CHANGELOG.md
└── README.md
```

---

## 🛣 Roadmap

### ✅ v1.1.0

- Terraform infrastructure configuration
- Testinfra infrastructure tests
- CodeQL security analysis
- Trivy vulnerability scanning
- Dependabot and Dependency Review
- Branch protection
- Database backup restore verification
- Production rollback workflow
- Grafana e-mail alerting
- Authentication event logging
- Real-time WebSocket notifications

### 🔮 v2.0

- Chat
- Meeting rooms
- User interface redesign and polishing

---

## 👨‍💻 Author

**Kamil Kalicki**

- GitHub: [Kali2114](https://github.com/Kali2114)
- LinkedIn: [Kamil Kalicki](https://www.linkedin.com/in/kamil-kalicki-047968245/)

---

## ⭐ Support

If you find this project interesting, consider giving it a star on GitHub.

Feedback and suggestions are welcome.
