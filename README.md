# Academic Information Management System (AIMS) - Version 2 🚀

Welcome to **Version 2** of the AIMS Final Year Project! 

The transition from V1's foundation introduces a state-of-the-art **Glassmorphic Sub-Portal Architecture**, intelligently routing administrative actors away from archaic backend panels and directly into highly responsive, custom-styled dashboards.

## 🌟 Key Features of Version 2

### 1. Isolated Teacher Dashboard Portal
- Users with the `TEACHER` role are now logically segregated into a beautiful frontend portal `/portal/`. 
- **Active Issue Tracking:** Teachers can submit issues, draft them, route them efficiently to proper departments matching their assignments, and safely monitor the resolution logic from HODs and Deans entirely in a read-only viewer logic flow securely isolated from data-alteration tampering.
- **Meeting Module Integration:** Teachers can seamlessly jump into the Meeting schedule to visually identify attached Agenda Issues, view Organizer logistics, and download securely uploaded `Meeting Minutes` PDF attachments natively.

### 2. Live Global Notification Engine
- Fully automated `pre_save` standard interceptors that hook into native framework structures to instantly track and flag data deltas dynamically.
- When an issue receives an official Decision from Leadership, or when a Dean uploads minutes to a finalized Meeting, a brand new `Notification` is quietly created and immediately propagated to the Teacher’s UI Bell indicator.

### 3. Glassmorphism UI Identity
- Strict adherence to premium styling aesthetics featuring a deep indigo/violet gradient logic.
- Translucent backdrop filters overlaid with active hovering responses to create depth.

## 🛠 Tech Stack
- **Backend:** Python + Django 6.0
- **Database:** PostgreSQL (Azure server structure)
- **Frontend Design:** Vanilla HTML + Global Component CSS (Glassmorphism Identity)

## 📦 Setting Up Environment
If deploying locally or pulling V2 for the first time natively:
1. Initialize the virtual environment natively inside the root directory.
2. `pip install djangorestframework psycopg2-binary`
3. Execute `python manage.py runserver`
4. Jump into `http://127.0.0.1:8000/login/`

## 🔮 Roadmap (Moving Towards V3)
Our goal for the upcoming iterations moves progressively up the hierarchy ladder! With the bottom floor entirely stabilized and automated, we will look to begin pulling the `HOD` and `DEAN` level users directly into their proprietary Glassmorphic tracking instances to construct the first fully cohesive interface block entirely detached from `/admin/`.
