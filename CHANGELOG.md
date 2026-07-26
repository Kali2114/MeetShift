# Changelog

All notable changes to this project will be documented in this file.

---

## [Unreleased]

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

#### Fixed
- Production `SECRET_KEY` no longer silently falls back to a hardcoded
  default when the environment variable is missing or misnamed.
- Registration now enforces the configured password strength validators.
- Notification WebSocket events are no longer sent twice per notification.
- User emails are validated for format, not just presence.
- Meeting detail page action buttons (Invite/Edit/Delete) restyled to match
  the rest of the UI instead of rendering as plain links.

### Planned for v2.0.0 — Real-Time Communication & Meeting Rooms

#### Messaging polish
- Responsive messaging layout for small screens (not yet built or verified
  on mobile).
- Conversation header avatar (currently sidebar-only).

#### Meeting rooms
- Presence tracking for meeting participants.
- Online and offline participant status.
- Unread room message counters.
- Notifications for new room activity.

#### Frontend
- Dark mode.
- Meeting room chat UI polish (currently a basic thread + input, reusing DM
  styling as-is).
- Better real-time state handling (e.g. WebSocket reconnection/backoff).

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

...
