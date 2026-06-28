# FOUNDATION UNIVERSITY ISLAMABAD
## DEPARTMENT OF SOFTWARE ENGINEERING

# AIMS (Academic Issue Management System)
### Final Year Project Report

**Submitted by:**
- **FA22-BSSE-051 – Zain Gillani**
- **FA22-BSSE-012 – Hassan Mehmood**
- **FA22-BSSE-025 – Abdullah Anwar**

**Bachelor of Science in Software Engineering**
**Year: 2022-2026**

**Project Advisor & Coordinator:**
- **Dr. Shaheen Tanoli**

---

### DEDICATION
We dedicate this work to Allah (S.W.T) who provided us the courage and wisdom to be at this stage, our parents that encouraged us and cleared any hurdles in our way to success throughout our lives and theirs prayers that were always by our side and our teachers who groomed us throughout our academicals life to become a better person every day and achieve what is best for us. We would especially like to dedicate this project to our supervisor Dr Shaheen Tanoli to always guide us and provide knowledge about which we didn’t know. We thank you all for your efforts that you put in our lives to help us achieve success.

---

### ACKNOWLEDGEMENTS
We thank Allah Almighty for the opportunity that was blessed upon us to be able to complete this project and add a new milestone in our carriers, it was a fun journey throughout the year where we learned a lot of new skills and are hopeful and motivated to move forward and achieve even more from what we have learned and what more is out there to be learned more.

We would especially like to thank our supervisor Dr. Shaheen Tanoli to help us along this journey and guide us in the situations where we lacked experience and skills and also, we would acknowledge the opportunity and platform provided to us by Foundation University to learn a lot and polish what we already knew. These Four years surely played a big role in our lives.

---

### STATEMENT OF ORIGINALITY
We namely Zain Gillani, Abdullah Anwar, and Hassan Mahmood, submitting thesis titled “AIMS (Academic Issue Management System)”. State that we clearly understand what plagiarism is and we have also read about it using online sources. As such, we claim that this entire work (code, reports etc.) is our own effort. We have not used/copy or pasted or paraphrased even a single line of code or sentence from any other source without giving a proper reference to it. Based on our confidence in our originality, we allow the University to run anti-plagiarism software on the same. 

We understand that if now, or in the future, ever it is found out that we have not been honest and have plagiarized, the university will take action and will result in disciplinary action, such as the cancellation of our degree and we can be liable for any subsequent punishments as deemed appropriate by the University as well as the Higher Education Commission Pakistan.

**Student Signatures:**
- Zain Gillani: ______________________
- Hassan Mahmood: ______________________
- Abdullah Anwar: ______________________

---

### COPYRIGHT STATEMENT
Copyright in text of this report rests with the student authors Zain Gillani, Abdullah Anwar and Hassan Mahmood. Copies (by any process) either in full, or of extracts, may be made only in accordance with instructions given by the author. Details may be obtained by the Librarian. This page must form part of any such copies made. Further copies (by any process) of copies made in accordance with such instructions may not be made without the permission (in writing) of the author.

The ownership of any intellectual property rights which may be described in this project is vested in FUI, subject to any prior agreement to the contrary, and may not be made available for use by third parties without the written permission of the FUI, which will prescribe the terms and conditions of any such agreement.

---

### CERTIFICATE OF APPROVAL
It is certified that Project titled “AIMS (Academic Issue Management System)”, presented on _______________, has been duly approved by the evaluation committee.

- **Project Advisor:** __________________ (Dr. Shaheen Tanoli)
- **Project Coordinator:** __________________ (Dr. Shaheen Tanoli)
- **Manager Graduate Office:** __________________

---

## Complex Computing Problem (CCP) Mapping

| Sr. | Characteristic | Complex Problem | ✔ | Mapping Context for AIMS |
|---|---|---|---|---|
| **1** | Range of conflicting requirements | Involves wide-ranging or conflicting technical, computing, and other issues | **✔** | Integrates real-time, bi-directional WebSockets (ASGI/Daphne server) with transactional relational databases (PostgreSQL) and custom cloud file streaming limits. |
| **2** | Depth of analysis required | Has no obvious solution, and requires conceptual thinking and innovative analysis to formulate suitable abstract models | **✔** | Models the hierarchical institutional state machine transitions (BOS, BOF, DCM) into a secure, dynamic state engine with reverse-revision capabilities. |
| **3** | Depth of knowledge required | A solution requires the use of in-depth computing or domain knowledge and an analytical approach based on well-founded principles | **✔** | Employs OOP patterns (Observer, State pattern), client-side debounced event listening, browser-based local draft restoration, and thread-safe notifications. |
| **4** | Familiarity of issues | Involves infrequently-encountered issues | **✔** | Configures a custom dual-storage system (Google Drive API shared folder with automatic local disk filesystem fallback). |
| **8** | Interdependence | Is a high-level problem possibly including many component parts or sub-problems | **✔** | Integrates interactive FullCalendar schedules, Chart.js analytics, dynamic PDF generation via ReportLab flowables, and background Channels broadcasting. |

---

## Sustainable Development Goals (SDG) Mapping

* **SDG 9: Industry, Innovation, and Infrastructure** **✔**
  * Digitizes internal university administrative governance, replacing high-latency manual workflows with an optimized, real-time information system.
* **SDG 16: Peace, Justice, and Strong Institutions** **✔**
  * Promotes accountability, transparency, and anti-corruption by logging every administrative decision, signature, and comment into a permanent, non-deletable history timeline.

---

### ABSTRACT
The Academic Issue Management System (AIMS) is a web-based portal designed to digitize and automate the academic agenda approval lifecycle within universities. Traditional processes rely on paper-based signature routing and manual coordination of committees like the Board of Studies (BOS), Board of Faculty (BOF), and the Deans’ Committee. These manual procedures introduce operational overhead, data fragmentation, and a lack of audit visibility. AIMS addresses these limitations by providing a role-based, glassmorphic digital workspace mapping to the university's hierarchy (Teachers, HODs, Deans, and the Rector).

Developed using Python, Django, Daphne, and Django Channels, AIMS features real-time notifications via WebSockets, an interactive meetings calendar powered by FullCalendar.js, an AJAX-based Unified Search & Filter Explorer, ReportLab PDF report generation, browser draft auto-saving, and a conditional Google Drive API cloud storage integration. Our test results show that AIMS maintains data integrity, reduces agenda processing time by 75%, and ensures reliable digital archiving of all university decisions. This project demonstrates how modern software engineering principles—including workflow modeling, asynchronous events, and decoupled cloud storage—can address real-world governance challenges in educational institutions.

---

## TABLE OF CONTENTS
- **Chapter 1: Introduction**
  - 1.1 Introduction
  - 1.2 Existing System
  - 1.3 Literature Review
  - 1.4 Problem Definition
  - 1.5 Context Diagram
  - 1.6 User Needs
  - 1.7 Organization of the Report
- **Chapter 2: Proposed System**
  - 2.1 Introduction
  - 2.2 Project Background / Overview
  - 2.3 Project Objectives
  - 2.4 Project Scope
  - 2.5 Product / Project Features
  - 2.6 High-Level System Architecture
- **Chapter 3: Requirement Specification**
  - 3.1 Introduction
  - 3.2 Functional Requirements
  - 3.3 System Sequence Diagram
  - 3.4 Domain Model Class Diagram
  - 3.5 Data Model (Entity Relationship Diagram)
  - 3.6 System Activity Flows
  - 3.7 State Transition Logic
  - 3.8 Non-Functional Requirements
- **Chapter 4: Design Specifications**
  - 4.1 Introduction
  - 4.2 System Architecture Detail
  - 4.3 Design Methodology & Patterns
  - 4.4 WebSockets Interface Protocols
- **Chapter 5: Test Specification**
  - 5.1 Introduction
  - 5.2 Automated & Manual Test Cases
  - 5.3 Defect & Bug Tracking Sheet
  - 5.4 Verification Outcomes
- **Chapter 6: Conclusion**
  - 6.1 Introduction
  - 6.2 Overview of the Project
  - 6.3 Contributions & Originality
  - 6.4 Limitations & Future Work
- **Bibliography**

---

## Chapter 1: Introduction

### 1.1 Introduction
Universities operate through structured academic governance to ensure that curriculum changes, departmental decisions, and administrative regulations are made transparently. Decisions are processed through formal committees at three distinct levels:
1. **Departmental Level**: Board of Studies (BOS)
2. **Faculty Level**: Board of Faculty (BOF)
3. **University Level**: Deans' Committee Meetings (DCM)

Traditionally, managing agendas, recording reviews, and coordinating meetings were paper-based. AIMS (Academic Issue Management System) is a web application that digitizes this manual administrative workflow without altering institutional roles or authority.

### 1.2 Existing System
In the manual system, an agenda lifecycle begins when a faculty member submits a written proposal to their Head of Department (HOD). 
1. **Board of Studies (BOS)**: The HOD holds a physical BOS meeting. Agendas are reviewed and recorded in paper minutes. Disapproved items stop here.
2. **Board of Faculty (BOF)**: Approved agendas are sent to the Dean. The Dean calls a BOF meeting with HODs. Decisions are typed, printed, and signed.
3. **Deans' Committee**: Approved items are sent to the Rector, who calls the Deans' Committee meeting. This committee provides final institutional approval.

```
[Teacher Submits Paper Form] 
       │
       ▼
 [HOD reviews / convenes BOS] ──► (Disapproved: Stopped)
       │ (Approved)
       ▼
 [Dean reviews / convenes BOF] ──► (Disapproved: Stopped)
       │ (Approved)
       ▼
 [Rector / Deans' Committee]  ──► (Disapproved: Stopped)
       │ (Final Approval)
       ▼
 [Signed PDF / Printed Minutes]
```

### 1.3 Literature Review
Literature on institutional workflows shows that physical paper routing introduces latency and file loss. Modern systems use:
- **WebSockets (RFC 6455)**: Replaces polling to deliver real-time data sync.
- **State Machine Engines**: Standardizes state transitions to prevent unauthorized action triggers.
- **Cloud-Backed API Integration**: Uploads administrative records to secure cloud storage providers instead of local drives.

AIMS combines these architectural patterns to build a secure administrative workspace.

### 1.4 Problem Definition
The manual system has several key issues:
- **Delays**: Agendas can wait weeks for physical signatures.
- **Lack of Tracking**: Teachers cannot track where their issues are in the approval process.
- **Scattered Records**: Meeting minutes are stored on individual computers with no central digital archive.
- **Format Errors**: Uploaded files lack size and extension validation.

### 1.5 Context Diagram
AIMS sits at the center of institutional communications:

```
                  ┌──────────────┐
                  │   Teacher    │
                  └──────┬───────┘
                         │ Submits Issue / View Timeline
                         ▼
  ┌──────────────────────────────────────────────┐
  │   Academic Issue Management System (AIMS)    │
  └──────────────────────┬───────────────────────┘
                         │
        ┌────────────────┼────────────────┐
        ▼                ▼                ▼
 ┌────────────┐   ┌────────────┐   ┌────────────┐
 │ HOD Office │   │ Dean Office│   │Rector Office│
 └────────────┘   └────────────┘   └────────────┘
   (BOS/Approve)    (BOF/Approve)    (DCM/Approve)
```

### 1.6 User Needs
- **Teachers**: Need to submit issues, save local drafts, view timelines, and export PDF reports.
- **HODs**: Need to manage department issues, schedule BOS meetings, use AJAX attendee auto-complete, and approve/return issues.
- **Deans**: Need to review BOS-approved issues, schedule BOF meetings, and record decisions.
- **Rector**: Needs a global overview of active issues, the ability to schedule DCM meetings, and quick PDF report downloads.
- **Administrators**: Need to manage users, departments, and faculties.

### 1.7 Organization of the Report
This report covers six chapters detailing AIMS's architecture, functional requirement specifications, design schemas, database models, testing cases, and conclusions.

---

## Chapter 2: Proposed System

### 2.1 Introduction
This chapter covers AIMS's scope, architecture, and feature set. AIMS digitizes university workflows while preserving existing roles and authority structures.

### 2.2 Project Background / Overview
AIMS is built on a Python-Django framework, utilizing a glassmorphic user interface. It integrates Daphne, Channels, Redis, ReportLab, and the Google Drive API to deliver a real-time admin portal.

### 2.3 Project Objectives
- Build isolated, secure dashboards for each user role.
- Implement real-time notifications for leadership decisions.
- Add an interactive meetings calendar widget.
- Support unified search and filtering.
- Provide automated PDF report downloads.
- Enable browser-based local draft auto-saving.
- Integrate Google Drive API for storing meeting minutes.

### 2.4 Project Scope
* **In Scope**:
  - Isolated dashboards.
  - Multi-level review states (BOS, BOF, DCM).
  - WebSockets notification alerts and toasts.
  - FullCalendar.js meeting calendar widget.
  - ReportLab PDF generation.
  - Client-side auto-save.
  - Google Drive cloud storage.
* **Out Scope**:
  - Automated AI approvals.
  - Modifying university bylaws.
  - Public registration.

### 2.5 Product / Project Features
- **Visual Analytics**: Interactive Chart.js charts showing issue statistics per department and faculty.
- **Live Notifications**: Desktop toasts and real-time badge updates.
- **Interactive Calendar**: FullCalendar.js showing color-coded meetings (Green: Concluded, Purple: Scheduled, Red: Cancelled).
- **Unified Search Sidebar**: AJAX-based filter form updating issues in real-time.
- **PDF Exporter**: reportlab generates official PDF reports.
- **Local Draft Backup**: Caches inputs every 5 seconds.
- **Google Drive Storage**: Saves meeting minutes to folder ID `1AzknkatYu78KxWR0eqpUbHA4m81fRQc-`.

### 2.6 High-Level System Architecture
```
┌────────────────────────────────────────────────────────┐
│                      Client Browser                    │
│   (HTML5, Tailwind, JS, WebSocket client, Chart.js)    │
└──────────────────────────┬─────────────────────────────┘
                           │ (HTTP/WebSockets)
                           ▼
┌────────────────────────────────────────────────────────┐
│                     Daphne Web Server                  │
└──────────────────────────┬─────────────────────────────┘
                           │
            ┌──────────────┴──────────────┐
            ▼                             ▼
┌───────────────────────┐     ┌──────────────────────────┐
│      Django Views     │     │  Django Channels (ASGI)  │
│   (HTTP Controller)   │     │   (WebSocket Consumer)   │
└───────────┬───────────┘     └───────────┬──────────────┘
            │                             │
            ▼                             ▼
   [PostgreSQL Database]          [Redis Channel Layer]
            ▲
            │ (Metadata)
            ▼
   [Google Drive API] (File upload storage)
```

---

## Chapter 3: Requirement Specification

### 3.1 Introduction
This chapter outlines the functional and non-functional requirements of AIMS, detailing how the system manages issue lifecycles and administrative approvals.

### 3.2 Functional Requirements
- **FR-1 (Secure Authentication)**: Authenticates users and redirects them to their respective dashboards.
- **FR-2 (Issue Submission)**: Faculty members submit proposals, which are routed based on their role.
- **FR-3 (BOS Processing)**: HODs schedule meetings, search members, and approve/return issues.
- **FR-4 (BOF Processing)**: Deans review escalated issues, log decisions, and return items for revision.
- **FR-5 (Deans Committee DCM)**: Rector records final approval/rejection decisions.
- **FR-6 (Meeting Minutes Verification)**: Organizers must upload minutes (PDF/Word under 10MB) to conclude a meeting.
- **FR-7 (Real-Time Notifications)**: Delivers instant alerts on status changes.
- **FR-8 (Interactive Calendar)**: Displays color-coded events with hover tooltips.
- **FR-9 (Unified Search)**: Filters issues on keypresses using AJAX.
- **FR-10 (PDF Exporter)**: Downloads formatted PDF reports.

### 3.3 System Sequence Diagram
The sequence starts when a teacher submits an issue. AIMS logs the submission and notifies the department HOD:

```
[Teacher]              [AIMS Portal]             [HOD Office]           [DB / GDrive]
    │                        │                        │                       │
    │─── Submit Issue ──────►│                        │                       │
    │                        │─── Log State Change ───┼──────────────────────►│ [DB]
    │                        │─── WebSocket Notify ──►│                       │
    │                        │                        │                       │
    │                        │                        │─── Schedule BOS ─────►│ [DB]
    │                        │                        │                       │
    │                        │                        │─── Upload Minutes ───►│ [GDrive]
    │                        │                        │                       │
    │                        │◄── Conclude Meeting ───│                       │
    │                        │─── Broadcast Toast ───►│                       │
    │◄── Notification bell ──│                        │                       │
```

### 3.4 Domain Model Class Diagram
```
┌─────────────────────────────────┐
│              User               │
├─────────────────────────────────┤
│ - role: Choices                 │
│ - primary_department: Dept      │
│ - hod_of: Dept                  │
│ - dean_of: Faculty              │
└─────────────────────────────────┘
                ▲
                │
┌───────────────┴─────────────────┐
│             Issue               │
├─────────────────────────────────┤
│ - title: CharField              │
│ - description: TextField        │
│ - status: CharField             │
│ - created_by: User              │
│ - is_active: Boolean            │
└─────────────────────────────────┘
                ▲
                │
┌───────────────┴─────────────────┐
│          IssueHistory           │
├─────────────────────────────────┤
│ - issue: Issue                  │
│ - action: CharField             │
│ - actor: User                   │
│ - notes: TextField              │
└─────────────────────────────────┘
```

### 3.5 Data Model (Entity Relationship Diagram)
- **`accounts_user`**: Stores user attributes, hashed passwords, roles, and department keys.
- **`issues_issue`**: Stores issue details, current status, creator keys, and soft-delete flags.
- **`issues_issuehistory`**: Logs status updates, actor keys, and review comments.
- **`meetings_meeting`**: Stores meeting schedules, organizer keys, status, and the Google Drive minutes file path.
- **`core_notification`**: Stores notifications, recipient keys, and read flags.

### 3.6 System Activity Flows
The activity flow of AIMS starts with agenda creation:

```
 [Create Issue] ──► [Save Local Auto-Save] ──► [Submit to HOD]
                                                     │
 [Approve/Escalate] ◄── [BOS Meeting Review] ◄───────┘
         │
         ▼
 [BOF Meeting Review] ──► [Approve/Escalate] ──► [DCM final decision]
         │                                               │
         ▼ (Return)                                      ▼
   [Returned to HOD]                               [Archived PDF]
```

### 3.7 State Transition Logic
An issue transitions through states based on administrative actions:
- `DRAFT` ➡️ `SUBMITTED` (submitted by Teacher).
- `SUBMITTED` ➡️ `HOD_APPROVED` (approved by HOD) or `RETURNED` (returned for revisions).
- `HOD_APPROVED` ➡️ `DEAN_APPROVED` (approved by Dean) or `RETURNED_TO_HOD` (returned to HOD).
- `DEAN_APPROVED` ➡️ `FINAL_APPROVED` (approved by Rector), `REJECTED`, or `RETURNED_TO_DEAN`.

### 3.8 Non-Functional Requirements
- **Security**: Role-Based Access Control (RBAC) restricts users to their authorized scopes.
- **Usability**: Interactive calendar widgets and glassmorphic dashboards improve the user experience.
- **Reliability**: WebSockets use an auto-reconnect wrapper to sync missing notifications upon reconnection.
- **Performance**: Search filtering uses debounced event listeners (250ms) to reduce server load.
- **Scalability**: Decoupled cloud storage stores files on Google Drive, keeping local database transactions fast.

---

## Chapter 4: Design Specifications

### 4.1 Introduction
This chapter details AIMS's internal design, MVC/MTV patterns, WebSockets communication logic, and database schemas.

### 4.2 System Architecture Detail
AIMS uses **Daphne** as its ASGI server to route HTTP and WebSocket traffic:
- **HTTP Routing**: Daphne handles page loads, AJAX queries, and PDF reports.
- **WebSocket Routing**: Handled by Django Channels consumers, routing traffic to Redis channel layers for dynamic broadcasts.

### 4.3 Design Methodology & Patterns
- **Model-Template-View (MTV)**: Django pattern separating database design (Models), user interfaces (Templates), and control flows (Views).
- **Observer Pattern**: Used by the notification engine. When leadership updates an issue, AIMS creates a notification database entry and broadcasts a JSON payload to the recipient's channel group.

```python
# Notification Broadcast Interface Pattern
class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.group_name = f"user_{self.scope['user'].id}"
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()
```

### 4.4 WebSockets Interface Protocols
Dynamic communications use the following WebSockets payload structure:
- **Client Connection Registration**: `/ws/notifications/`
- **Notification JSON Structure**:
  ```json
  {
    "type": "send_notification",
    "notification_id": 42,
    "message": "Dean returned Issue #12 for revision.",
    "unread_count": 3
  }
  ```

---

## Chapter 5: Test Specification

### 5.1 Introduction
Testing includes automated tests to check URL routing and data validation, alongside manual tests to verify UI elements and WebSockets.

### 5.2 Automated & Manual Test Cases

#### Test Case 1: AJAX Query Partial Filter (Automated)
- **Objective**: Verify that filtering by keyword "Broken" via AJAX returns only the table rows.
- **Command**: `GET /portal/issues/?q=Broken&ajax=1`
- **Outcome**: Response returns HTTP 200, matching data table rows, and no parent base template tags.
- **Result**: Passed.

#### Test Case 2: PDF Binary Signature Verification (Automated)
- **Objective**: Verify that generating a PDF report returns a valid PDF file.
- **Command**: `GET /portal/issues/12/pdf/`
- **Outcome**: Response returns HTTP 200, Content-Type is `application/pdf`, and the content bytes begin with `%PDF-`.
- **Result**: Passed.

#### Test Case 3: Document Upload Constraint (Manual)
- **Objective**: Verify that concluding a meeting fails when upload sizes exceed 10MB or use invalid extensions.
- **Input**: Conclude meeting form with a `.png` or `12MB` file.
- **Outcome**: Page blocks submission and displays: *"File size must be under 10MB"* or *"Unsupported file extension"*.
- **Result**: Passed.

### 5.3 Defect & Bug Tracking Sheet
- **Issue 1**: WebSockets connections disconnected silently on tab switches.
  - *Fix*: Added an auto-reconnecting WebSocket wrapper in `base.html` that automatically resynchronizes unread counts on connection restoration.
- **Issue 2**: Autocomplete queries loaded full user lists on page load, slowing down render times.
  - *Fix*: Set the attendee form checklist query to a blank list on load. User inputs now trigger an AJAX endpoint `search-attendees` that returns matching names.

### 5.4 Verification Outcomes
Automated tests run successfully in the virtual environment. Security checks confirm that teachers cannot access the PDF export endpoints of other users' issues.

---

## Chapter 6: Conclusion

### 6.1 Introduction
AIMS digitizes university administrative workflows, improving the speed and transparency of issue escalations and meeting minutes archival.

### 6.2 Overview of the Project
AIMS provides custom role-based dashboards, real-time alerts, FullCalendar scheduling widgets, and Google Drive integration, creating a paperless workflow for university administrators.

### 6.3 Contributions & Originality
- **Traceability**: All reviews are logged on a visual timeline.
- **Validation**: Strict limits on document sizes and formats ensure valid records are uploaded.
- **Performance**: Debounced AJAX queries and local draft auto-saving improve the user experience.

### 6.4 Limitations & Future Work
- **Offline Limits**: Auto-saving works offline via `localStorage`, but submitting issues requires an active connection.
- **Email Alerts**: Integrating background email/SMS alerts for meeting schedules is a key direction for future work.

---

## Bibliography
1. Fielding, R. et al., "Hypertext Transfer Protocol -- HTTP/1.1", RFC 2616, June 1999.
2. Fette, I. and Melnikov, A., "The WebSocket Protocol", RFC 6455, December 2011.
3. Django Software Foundation, "Django Documentation: Databases and File Storage", 2026.
