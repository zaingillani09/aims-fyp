# Academic Information Management System (AIMS) - Version 2 🚀

Welcome to **Version 2** of the AIMS Final Year Project! 

The transition from V1's foundation introduces a state-of-the-art **Glassmorphic Sub-Portal Architecture**, intelligently routing administrative actors away from archaic backend panels and directly into highly responsive, custom-styled dashboards.

## 🌟 Key Features of Version 2

### 1. Isolated Role-Based Dashboards
- **Teacher Dashboard:** Segregated into a beautiful frontend portal `/portal/`. Teachers can submit issues, draft them, route them to proper departments, and track resolution.
- **HOD Dashboard:** HODs can manage department-specific BOS (Board of Studies) meetings, review pending department issues, make administrative decisions, and submit department-level issues to the Dean.
- **Dean Dashboard:** Deans can manage BOF (Board of Faculty) meetings, review escalated issues from all departments in their faculty, record decisions, and submit faculty-level issues to the Rector.
- **Rector Dashboard:** The Rector can review and give final approval or revision returns on escalated Dean-approved issues and schedule DCM (Deans Committee Meetings).

### 2. Multi-Level Issue Review & Workflow Engine
- **Role-Adaptive Actions:** Issue forms automatically adapt their labels based on the user's role (e.g. Teachers see *"Submit to HOD"*, HODs see *"Submit to Dean"*, and Deans see *"Submit to Rector"*).
- **Revision Lifecycle:** Fully supports returning issues for revision at the department (`RETURNED_TO_HOD`) and faculty (`RETURNED_TO_DEAN`) levels.

### 3. Smart Meeting Module & Validation
- **Minutes Upload Verification:** To conclude a scheduled meeting, organizers are strictly required to upload an official Minutes of Meeting (MOM) document. The system prevents concluding without an upload.
- **Format Restrictions:** The file picker restricts uploads to Word documents (`.doc`, `.docx`) and PDF (`.pdf`) formats, with backend validators enforcing strict format alignment.
- **Dynamic Attendee filtering:** The meeting scheduling portal features a dynamic department filter dropdown next to the search box, allowing organizers to easily filter and select teachers belonging to specific departments (e.g. Software Engineering).

### 4. Live Global Notification Engine
- Fully automated `pre_save` standard interceptors that hook into native framework structures to instantly track and flag data deltas dynamically.
- When an issue receives an official Decision from Leadership, or when a meeting minutes file is uploaded, a notification is quietly created and propagated to the target user's UI Bell indicator.

### 5. Glassmorphism UI Identity
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
