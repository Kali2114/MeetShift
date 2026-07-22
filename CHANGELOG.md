# Changelog

All notable changes to this project will be documented in this file.

---

## [Unreleased]

### Planned for v2.0.0 — Real-Time Communication & Meeting Rooms

#### Messaging
- Direct messages between users.
- Real-time private chat using WebSockets.
- Conversation list.
- Unread message counters.
- Message notifications.
- Message read status.
- Conversation history.

#### Meeting rooms
- Dedicated rooms connected to meetings.
- Real-time room chat.
- Presence tracking for meeting participants.
- Online and offline participant status.
- Room access limited to meeting participants.
- Unread room message counters.
- Notifications for new room activity.

#### Video meetings
- Possible integration with Google Meet.
- Automatic generation of video meeting links.
- Video meeting links connected to MeetShift meetings.
- Improved collaboration features for online meetings.

#### Frontend
- Improved messaging interface.
- Conversation sidebar.
- Meeting room interface.
- Better real-time state handling.
- Improved notification and unread state synchronization.

#### Infrastructure
- WebSocket scaling improvements.
- Improved Redis channel layer configuration.
- Additional monitoring for chat and room connections.
- Additional tests for real-time communication.
- Performance and reliability improvements for long-lived WebSocket connections.

---

### Planned for v3.0.0 — AI Meeting Assistant

#### AI assistant
- AI assistant connected to meetings.
- Automatic meeting agenda generation.
- Suggested discussion topics.
- Suggested questions based on the meeting description.
- Meeting preparation assistance.
- Intelligent follow-up suggestions.

#### Meeting summaries
- AI-generated meeting summaries.
- Extraction of key decisions.
- Automatic action item generation.
- Assignment of action items to participants.
- Summary history connected to meetings.

#### Scheduling intelligence
- Suggested meeting times based on participant availability.
- Detection of scheduling conflicts.
- Intelligent reminders for participants who have not responded.
- Suggested rescheduling options.

#### Chat and room intelligence
- Summaries of long meeting room conversations.
- Important message detection.
- Extraction of decisions from room chat.
- AI-generated answers based on meeting context.
- Context-aware assistance for meeting participants.

#### Agent architecture
- Single-agent meeting assistant.
- Possible multi-agent architecture for planning, summarization and follow-up.
- Specialized agents for:
  - scheduling,
  - agenda generation,
  - conversation summarization,
  - action item extraction,
  - reminders and follow-ups.
- Agent memory connected to meeting history.
- Controlled access to meeting, participant and conversation data.

#### Security and reliability
- Validation of AI-generated content.
- Protection against prompt injection.
- Permission-aware access to meeting data.
- Audit logging for AI actions.
- Rate limiting and usage monitoring.
- Fallback behavior when AI services are unavailable.

---

## [v1.1.0] — Real-Time Notifications & Infrastructure Hardening

### Released
2026-07-19

### Added

#### Real-time notifications
- WebSocket-based real-time notifications using Django Channels.
- Redis channel layer using `channels-redis`.
- Daphne ASGI application server.
- Live unread notification badge updates.
- Real-time notification toast messages.
- Navigation from notification toast to the related meeting.
- Duplicate notification protection on the frontend.
- Browser back and forward navigation handling for notification state.
- Nginx WebSocket proxy configuration for `/ws/`.

#### Infrastructure
- Terraform configuration for existing AWS infrastructure.
- Imported the existing AWS EC2 instance into Terraform state.
- Imported the existing Security Group into Terraform state.
- Imported the existing Elastic IP into Terraform state.
- Testinfra checks for local and production infrastructure.
- Production deployment synchronization with the `main` branch.
- Automated production health checks.
- Database backup restore verification.
- Production rollback workflow.
- Swap space on the production server.
- Grafana alerts for application availability.
- Grafana alerts for HTTP 5xx responses.

#### Security
- CodeQL analysis for Python.
- CodeQL analysis for GitHub Actions.
- Trivy Docker image vulnerability scanning.
- Trivy Terraform misconfiguration scanning.
- Dependabot configuration.
- Dependency review workflow.
- Branch protection rules for `main`.
- Authentication event logging and monitoring.

### Changed
- Replaced Gunicorn with Daphne in production.
- Updated the production Docker Compose configuration for ASGI.
- Updated Nginx to support WebSocket connections.
- Updated the deployment workflow to synchronize repository files before deployment.
- Recreated application, Celery and Nginx containers during deployment.
- Required IMDSv2 for the production EC2 instance.
- Upgraded the production EC2 instance to `t3.small`.
- Limited GitHub Actions checks to pushes and pull requests targeting `main`.
- Separated production and development dependency files.
- Reduced production image dependencies.
- Updated Pillow and development tooling dependencies.
- Improved browser navigation handling for notification badge state.

### Security
- Removed permanent SSH credentials from the deployment process.
- Continued deployment through AWS OIDC and Systems Manager.
- Added automated dependency monitoring.
- Added static security analysis.
- Added infrastructure security scanning.
- Documented accepted outbound network access.
- Documented the planned migration to an encrypted EC2 root volume.
- Ignored a confirmed Trivy false positive originating from an Autobahn example key.

---

## [v1.0.0] — Production Release

### Added

#### Application
- User registration and authentication.
- User profiles with avatar upload.
- Meeting creation, editing and deletion.
- Meeting invitations.
- Invitation acceptance and rejection.
- Meeting participant management.
- Notifications.
- Email integration.
- Asynchronous email processing.
- Meeting calendar dashboard.

#### Backend
- Django application.
- PostgreSQL database.
- Redis.
- Celery background worker.
- Automated tests.
- Coverage reporting.
- PostgreSQL version matrix in CI.

#### Production
- Production deployment on AWS EC2.
- Custom domain: `https://meetshift.org`.
- HTTPS with Cloudflare.
- Nginx reverse proxy.
- Gunicorn WSGI application server.
- Docker Compose production stack.
- GitHub Actions CI/CD pipeline.
- Docker Hub image publishing.
- Deployment through AWS OIDC and Systems Manager.

#### Monitoring
- Prometheus monitoring.
- Grafana dashboards.
- Loki log aggregation.
- Promtail log collection.
- Application metrics endpoint.
- Production health endpoint.

---

## Version roadmap

### v1.0.0
Production-ready meeting scheduling application.

### v1.1.0
Real-time notifications, infrastructure as code, security scanning, monitoring and deployment hardening.

### v2.0.0
Direct messages, real-time chat, meeting rooms, presence and possible Google Meet integration.

### v3.0.0
AI meeting assistant, agenda generation, summaries, action items, intelligent scheduling and agent-based workflows.
