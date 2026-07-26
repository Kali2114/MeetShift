# Changelog

All notable changes to this project will be documented in this file.

---

## [Unreleased]

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

## [v2.0.0] — Real-Time Communication & Meeting Rooms (2026-07-26)

### Added

#### Messaging
- Direct messages between users.
- Conversation model.
- Message model.
- Conversation manager for safe conversation creation.
- Conversation list.
- Conversation detail page.
- New conversation page with live name search/filter.
- Facebook Messenger-inspired two-column layout.
- Real-time private messaging using Django Channels.
- WebSocket conversation updates.
- Live message delivery.
- Enter to send messages, Shift+Enter for multiline messages.
- Conversation history.
- Unread message counters, including a dedicated live-updating badge on the
  Messages nav link.
- Message notifications integrated with the notification system, with their
  own toast title ("New message") and redirect to the conversation thread.
- Message read status.
- Conversation previews with last message.
- Conversation ordering by latest activity.
- Sidebar avatars for conversation participants.
- Responsive two-column layout: on narrow screens the conversation list and
  an open thread each take the full width, with a back link to return to
  the list.
- Conversation header shows the other participant's avatar, not just the
  sidebar.

#### Meeting rooms
- Dedicated room per meeting, auto-created alongside the meeting.
- Room activates automatically 10 minutes before the meeting's start time
  and closes 10 minutes after its end time; the organizer can also end it
  early at any point.
- Real-time room chat over its own WebSocket connection, separate from the
  personal notification socket.
- Room access limited to the organizer and accepted participants only,
  enforced consistently across the page, the send endpoint, and the socket
  connection itself.
- Meeting detail page shows the schedule (start/end time) and an "Enter
  room" link.
- Online/offline presence tracking for room participants.
- Unread room message counters on the "Enter room" link and the meetings
  list, based on a per-user last-read cursor per room.
- Notifications for new room activity: the organizer and other accepted
  participants (excluding the sender) are notified through the existing
  notification system when a room message is sent.

#### Frontend
- Dark mode: a nav toggle switches themes and remembers the choice, falling
  back to the system's light/dark preference on first visit. Covers the
  full site plus the FullCalendar dashboard view.
- WebSocket reconnection with exponential backoff for the notification,
  DM, and room chat sockets, so a dropped connection (network blip, server
  restart) recovers automatically instead of leaving live updates silently
  stopped until the page is reloaded.
- Meeting room chat now gives each participant a deterministic display
  color for their name, so a multi-person conversation is easier to
  follow at a glance (not needed for DMs, which are always 1:1).

#### Infrastructure
- Channels' Redis channel layer now uses its own Redis DB index (1),
  separate from Celery's broker/result backend (DB 0), which had been
  implicitly sharing DB 0 with no explicit index set.
- Prometheus metrics and Grafana panels for WebSocket connections: active
  connections and connect/disconnect rates, broken down by consumer
  (notifications vs. room chat) — previously invisible, since
  django-prometheus only instruments regular HTTP traffic.
- Consumer-level tests for two real-time scenarios that were previously
  only unit-tested indirectly: a user with two tabs open in the same room
  staying online until both disconnect, and a disconnect/reconnect cycle
  returning cleanly to baseline without leaking presence rows or
  connection metrics.
- Reviewed WebSocket scaling and long-lived connection reliability: Nginx
  already proxies `/ws/` correctly (HTTP/1.1 upgrade headers, a 24h
  read/send timeout, so idle connections aren't killed early) and Redis
  channel layer config is sound. Further scaling (e.g. multiple Daphne
  workers) is deferred until there's real traffic data to size it
  against, rather than guessing at numbers with nothing to validate them.

#### Fixed
- Production `SECRET_KEY` no longer silently falls back to a hardcoded
  default when the environment variable is missing or misnamed.
- Registration now enforces the configured password strength validators.
- Notification WebSocket events are no longer sent twice per notification.
- User emails are validated for format, not just presence.
- Meeting detail page action buttons (Invite/Edit/Delete) restyled to match
  the rest of the UI instead of rendering as plain links.
- Message input field no longer capped at 500px width, out of alignment
  with the rest of the chat box.

---

## [v1.1.0] — Real-Time Notifications & Infrastructure Hardening (2026-07-19)

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
- Imported the existing AWS EC2 instance, Security Group and Elastic IP into
  Terraform state.
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
- Updated the production deployment workflow to synchronize configuration
  files from the repository.
- Updated the production Docker Compose configuration for Daphne.
- Updated Nginx configuration to support WebSocket connections.
- Recreated the application and Nginx containers during production
  deployment.
- Updated Pillow and development tooling dependencies.
- Required IMDSv2 for the production EC2 instance.
- Limited GitHub Actions checks to pushes and pull requests targeting `main`.
- Reduced production image dependencies by excluding development tools.
- Updated notification badge state after browser back and forward
  navigation.
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
- Configured Trivy to ignore a confirmed false positive originating from an
  Autobahn package example key.

---

## [v1.0.0] — Production Release (2026-07-02)

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
