# 🚀 MeetShift

**MeetShift** is a Django-based web application designed to simplify meeting organization, scheduling, and rescheduling through a structured workflow.

The application allows users to create meetings, invite participants, propose multiple time slots, collect responses, and finalize the best possible meeting time.

---

## 🧠 Project Overview

Scheduling meetings is often chaotic:
- people suggest different times  
- responses are scattered  
- final decisions are unclear  
- rescheduling becomes messy  

👉 **MeetShift solves this problem** by providing a centralized system where the entire meeting lifecycle is managed in one place.

---

## 🎯 Key Features (MVP)

### 🔐 Authentication
- User registration  
- Login / logout  
- Access control  

### 📅 Meeting Management
- Create meetings  
- Edit and delete meetings  
- View meeting details  
- List user-created meetings  
- List meetings where the user is a participant  

### 👥 Participants
- Invite users  
- Remove participants  
- Organizer vs participants  

### ⏳ Scheduling
- Multiple time slot proposals  
- Participant responses:
  - ✅ Accepted  
  - ❌ Rejected  
  - 🤔 Maybe  

### ✔️ Final Decision
- Organizer selects final date  
- Meeting becomes confirmed  

### 🔄 Rescheduling
- Reopen scheduling  
- Add new proposals  
- Collect responses again  
- Update final date  

---

## 🏗️ Tech Stack

### Backend
- Python  
- Django  

### Database
- PostgreSQL  

### Frontend (MVP)
- Django Templates  
- HTML / CSS / JavaScript  

### Dev Tools
- Docker  
- Docker Compose  
- Git & GitHub  
- Ruff  
- Black  
- pre-commit  
- GitHub Actions  

---

## 📦 Project Structure

```
meetshift/
├── app/
│   ├── manage.py
│   ├── config/
│   ├── users/
│   ├── meetings/
│   ├── templates/
│   ├── static/
│   └── tests/
├── docker/
├── .github/
│   └── workflows/
│       └── ci.yml
├── docker-compose.yml
├── requirements.txt
├── .env
├── .env.example
├── .pre-commit-config.yaml
├── .gitignore
└── README.md
```

---

## 🐳 Running the Project (Docker)

```
docker-compose up --build
```

---

## ⚙️ Environment Variables

Example `.env` file:

```
DEBUG=True
SECRET_KEY=your_secret_key
POSTGRES_DB=meetshift
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_HOST=db
POSTGRES_PORT=5432
```

---

## 🧱 Core Models (Concept)

### 👤 User
Django user model (customizable)

### 📅 Meeting
- organizer  
- title  
- description  
- status  
- final date  

### 🤝 MeetingParticipant
Relation between user and meeting  

### ⏰ TimeSlotProposal
Proposed meeting times  

### 📊 TimeSlotResponse
User responses to proposals  

---

## 🔄 Meeting Lifecycle

- Draft  
- Pending  
- Confirmed  
- Rescheduling  
- Cancelled  
- Completed  

---

## 🔐 Permissions

### Organizer
- manage meeting  
- invite/remove participants  
- confirm final date  
- start rescheduling  

### Participant
- view meeting  
- respond to proposals  

---

## 🧪 Testing Strategy

Tests will cover:
- models  
- views  
- permissions  
- business logic  
- scheduling flow  

---

## ⚙️ Code Quality & pre-commit

```
pip install pre-commit
pre-commit install
pre-commit run --all-files
```

---

## ⚙️ CI/CD (GitHub Actions)

Pipeline includes:
- install dependencies  
- run linters (ruff)  
- check formatting (black)  
- run tests  

Triggers:
- push  
- pull request  

---

## 🛣️ Development Roadmap

- Phase 1: setup + docker + postgres  
- Phase 2: authentication  
- Phase 3: meeting CRUD  
- Phase 4: participants  
- Phase 5: time slots  
- Phase 6: responses  
- Phase 7: final date  
- Phase 8: rescheduling  
- Phase 9: tests + refactor  

---

## 📌 Future Improvements

- Email notifications  
- Calendar UI  
- Google Calendar integration  
- REST API  
- Mobile support  
- Smart scheduling  
- Timezone support  

---

## 💡 Why This Project?

This is more than a CRUD app.

It demonstrates:
- business logic design  
- state management  
- relational modeling  
- permissions handling  
- real-world problem solving  

---

## 👨‍💻 Author

Portfolio project built with Django to demonstrate backend and DevOps skills.