# AIMS Faculty Portal (Academic Information Management System)

AIMS is a centralized administrative workflow and management portal built using Django. The system digitizes academic administration, enforcing strict Role-Based Access Control (RBAC) specifically tailored for hierarchical university operations.

## 🚀 Current Accomplishments (V1 MVP)
The initial structure of the AIMS portal has been successfully implemented and deployed to a PostgreSQL backend. Key accomplishments include:

- **Strict Hierarchical RBAC:** Complex user definitions ensuring security and data isolation across various hierarchical tiers:
  - `Teacher`
  - `HOD` (Head of Department)
  - `Dean`
  - `Rector`
  - `Sysadmin`
- **Issue Workflow Pipeline:** A fully functional, immutable decision-making pipeline where requests and issues are escalated tier-by-tier with complete digital trails and uneditable recorded notes.
- **Dynamic Onboarding:** Secure first-login flows requiring password resets and forced profile population with modern glassmorphic aesthetics.
- **Relational Integrity:** Strong Many-to-Many mappings accurately linking Users to primary and adjunct Departments and Faculties.

## 🎯 Future Goals & Roadmap
As we push towards the final iteration of the product, the portal will evolve into a comprehensive administrative hub. The upcoming modules include:

### 1. Advanced Meeting Scheduler
- A dedicated scheduling engine specifically for formal academic committees:
  - **BOF** (Board of Faculty)
  - **BOS** (Board of Studies)
  - **Dean's Committee**

### 2. Automated Notification System
- Real-time event triggers to alert and RSVP concerned members about their specific upcoming scheduled meetings.

### 3. Native Meeting Minutes Module
- A rigid record-keeping module to digitally log, archive, and disseminate Meeting Minutes. This ensures complete transparency and historical tracking of every formal decision that takes place within the institution.
