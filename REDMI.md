# Machine Test – Task Scheduler System (Django + React)

## Overview
This project implements a simplified Task Scheduler similar to Airflow / Celery.
It includes:
- Task creation with cron expressions
- Cron preview (next 5 run times)
- Automatic scheduling engine
- Retry logic with exponential backoff
- Task dependencies
- Pause / Resume
- Run Now
- Execution history logs
- React UI for task management

## Tech Stack
- Backend: Django, Django REST Framework, croniter
- Frontend: React, Axios
- Scheduler Worker: Django Custom Management Command

---

## Features Implemented

### ✔ Task Management
- Create task with cron expression
- Preview next 5 run times
- Edit / Delete / Pause / Resume
- Run task immediately

### ✔ Cron Engine
- Custom scheduler running via:  
  `python manage.py run_scheduler`
- Runs tasks when `next_run_at <= now`
- Supports 5-second or 10-second polling

### ✔ Retry Logic
- On failure:
  - Retry in 1 min → 2 min → 4 → 8 …
- On success:
  - retry_count resets to 0
  - next_run_at recalculated using cron

### ✔ Task Dependencies
- Parent task must succeed before child runs
- Prevents circular dependency

### ✔ Logs
- Every execution inserted into `TaskExecutionHistory`
- Includes:
  - status (success / failed / skipped / manual)
  - timestamp
  - log message

---

## How to Run

### 1. Clone & Install
git clone https://github.com/Vvk0105/task-schedule-system-server.git

pip install -r requirements.txt

### 2. Apply Migrations
python manage.py migrate

### 3. Run Backend Server
python manage.py runserver


### 4. Run Scheduler Worker (separate terminal)
python manage.py run_scheduler


### 5. Run React Frontend

npm i
npm run dev


## API Endpoints

- POST `/api/create-task/`
- GET `/api/tasks/`
- POST `/api/tasks/:id/run-now/`
- POST `/api/tasks/:id/pause/`
- POST `/api/tasks/:id/resume/`
- GET `/api/logs/`
- GET `/api/cron-preview/`

---

## Notes
- Timezone set to Asia/Kolkata
- Cron parsing using croniter
- No unnecessary features added
