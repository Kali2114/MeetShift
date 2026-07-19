# Changelog

## [Unreleased]

### Planned for v2.0.0
- Direct messages between users.
- Real-time chat using WebSockets.
- Conversation list and unread message counters.
- Message notifications.
- Meeting rooms for participants.
- Real-time room presence.
- Room-based chat connected to meetings.
- Possible integration with the Google Meet API.
- Automatic creation of video meeting links.
- Improved meeting collaboration features.


---

## v1.1.0 - Real-Time Notifications & Infrastructure Hardening
### 2026-07-19

### Added
- WebSocket-based real-time notifications using Django Channels.
- Redis channel layer using `channels-redis`.
- Daphne ASGI application server for production.
- Live unread notification badge updates without page refresh.
- Real-time notification toast messages.
- Notification toast navigation to the related meeting.
- Duplicate WebSocket notification protection on the frontend.
- Browser back and forward navigation handling for notification state.
- Nginx WebSocket proxy configuration for `/ws/`.
- Terraform configuration for the existing MeetShift infrastructure.
- Imported the existing AWS EC2 instance, Security Group and Elastic IP into Terraform state.
- Testinfra checks for local and production infrastructure.
- CodeQL security analysis for Python and GitHub Actions.
- Trivy vulnerability scanning for Docker images.
- Trivy misconfiguration scanning for Terraform.
- Dependabot configuration.
- Dependency review workflow.
- Database backup restore verification.
- Production rollback workflow.
- Grafana alerts for application availability and HTTP 5xx responses.
- Authentication event logging and monitoring.
- Branch protection rules for `main`.
- Separate development and production dependency files.
- Production deployment synchronization with the `main` branch.
- Automated production health check after deployment.

### Changed
- Replaced Gunicorn with Daphne to support ASGI and WebSocket connections.
- Updated the production deployment workflow to synchronize configuration files from the repository.
- Updated the production Docker Compose configuration for Daphne.
- Updated Nginx configuration to support WebSocket connections.
- Recreated the application and Nginx containers during production deployment.
- Updated Pillow and development tooling dependencies.
- Required IMDSv2 for the production EC2 instance.
- Limited GitHub Actions checks to pushes and pull requests targeting `main`.
- Reduced production image dependencies by excluding development tools.
- Updated notification badge state after browser back and forward navigation.
- Increased the production EC2 instance type to `t3.small`.
- Added swap space to the production server.

### Security
- Added automated Docker image vulnerability scanning.
- Added automated Terraform misconfiguration scanning.
- Added CodeQL static security analysis.
- Added automated dependency update checks.
- Added dependency review for pull requests.
- Removed permanent SSH credentials from the deployment process.
- Continued using AWS OIDC and Systems Manager for production deployment.
- Documented accepted outbound network access requirements.
- Documented planned migration to an encrypted EC2 root volume.
- Configured Trivy to ignore a confirmed false positive originating from an Autobahn package example key.


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
