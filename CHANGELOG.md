# Changelog

## [Unreleased]

### Added
- Imported existing AWS EC2, Security Group and Elastic IP into Terraform.
- Added initial Terraform configuration for MeetShift infrastructure.
- Added Testinfra checks for local and production infrastructure.
- Added CodeQL security analysis for Python and GitHub Actions.
- Added Trivy vulnerability scanning for Docker images and Terraform configuration.
- Added branch protection rules for `main`.
- Added separate production and development dependency files.

### Changed
- Updated Pillow and development tooling dependencies.
- Required IMDSv2 for the production EC2 instance.
- Limited GitHub Actions checks to pushes and pull requests targeting `main`.
- Reduced production image dependencies by excluding development tools.

### Security
- Added Docker image vulnerability scanning.
- Added Terraform misconfiguration scanning.
- Documented accepted outbound network access requirements.
- Documented planned migration to an encrypted EC2 root volume.

### Planned
- Dependabot and dependency review.
- Database backup restore verification.
- Production rollback workflow.
- Grafana alerting.
- README screenshots.
- UI polishing and meeting detail improvements.
- WebSocket-based notifications.

---

## v1.0.0 - Production Release

### Added
- Production deployment on AWS EC2.
- Custom domain: https://meetshift.org.
- HTTPS with Cloudflare.
- Nginx reverse proxy.
- Gunicorn application server.
- PostgreSQL database.
- Redis and Celery background worker.
- Prometheus monitoring.
- Grafana dashboard.
- GitHub Actions CI pipeline.
- User authentication.
- Meeting management.
- Invitations.
- Notifications.
- User profiles with avatar upload.
- Email integration.

### Infrastructure
- Docker Compose production setup.
- Cloudflare DNS configuration.
- Application metrics endpoint.
- Production monitoring stack.
