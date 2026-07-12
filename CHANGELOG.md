# Changelog

## [Unreleased]

### Planned
- Terraform infrastructure as code
- Testinfra server configuration checks
- CodeQL security analysis
- Trivy vulnerability scanning
- Dependabot and dependency review
- Database backup restore verification
- Production rollback workflow
- Grafana alerting
- README screenshots
- UI polishing and meeting detail improvements
- WebSocket-based notifications

---

### Added
- Imported existing AWS EC2, Security Group and Elastic IP into Terraform.
- Added initial Terraform configuration for MeetShift infrastructure.

## v1.0.0 - Production Release

### Added
- Production deployment on AWS EC2
- Custom domain: https://meetshift.org
- HTTPS with Cloudflare
- Nginx reverse proxy
- Gunicorn application server
- PostgreSQL database
- Redis and Celery background worker
- Prometheus monitoring
- Grafana dashboard
- GitHub Actions CI pipeline
- User authentication
- Meeting management
- Invitations
- Notifications
- User profiles with avatar upload
- Email integration

### Infrastructure
- Docker Compose production setup
- Cloudflare DNS configuration
- Application metrics endpoint
- Production monitoring stack
