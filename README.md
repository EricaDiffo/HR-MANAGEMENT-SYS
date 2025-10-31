## Employee Management (Django)

A simple HR-style employee management web app built with Django. It includes employee CRUD, department management, attendance tracking (with clock in/out), and leave requests with approval workflow. 
### Features
- **Employees**: Create, list, edit, delete
- **Departments**: Create, list, edit, delete (restricted to staff/admin)
- **Attendance**:
  - Daily dashboard with presence rate, average and total worked hours
  - Manual create/edit/delete (staff/admin)
  - Self-service clock in and clock out
- **Leave management**: Create requests, list, edit/delete/approve/reject (staff/admin)

### Tech Stack
- Django 5.x (SQLite by default)
- Optional: `supabase-py` for Supabase Auth integration

### Project Structure
```
LEARN DJANGO/
  ├─ employe_project/        # Django project (settings, urls)
  ├─ employe/               # Main app (models, views, urls, templates)
  ├─ db.sqlite3             # Local dev database
  ├─ manage.py
  └─ supabase/ (optional)   # Your Supabase artifacts, if any
```

### Prerequisites
- Python 3.10+
- Pip and virtual environments

### Installation
```bash
python -m venv env
./env/Scripts/activate  # PowerShell on Windows
pip install django supabase
```

If you prefer pinning versions:
```bash
pip install "django>=5,<6" "supabase>=2"
```

### Environment (optional: Supabase Auth)
Set these only if you want to use Supabase Auth; otherwise the app uses Django auth.

PowerShell (Windows):
```powershell
$env:SUPABASE_URL = "https://YOUR-PROJECT.supabase.co"
$env:SUPABASE_ANON_KEY = "YOUR-ANON-KEY"
```

Bash (macOS/Linux):
```bash
export SUPABASE_URL="https://YOUR-PROJECT.supabase.co"
export SUPABASE_ANON_KEY="YOUR-ANON-KEY"
```

### Database Setup
```bash
python manage.py migrate
python manage.py createsuperuser  # create admin/staff user
```

### Run the Server
```bash
python manage.py runserver
```
Visit `http://127.0.0.1:8000/`.

### Default URLs
- `admin/` — Django admin
- Auth: `login/`, `signup/`, `verify-email/`, `logout/`
- Dashboard: `dashboard/`
- Employees: `employes/`, `employes/ajouter/`, `employes/<id>/modifier/`, `employes/<id>/supprimer/`
- Departments: `departements/`, `departements/ajouter/`, `departements/<id>/modifier/`, `departements/<id>/supprimer/`
- Attendance: `attendance/`, `attendance/liste/`, `attendance/ajouter/`, `attendance/<id>/modifier/`, `attendance/<id>/supprimer/`, `attendance/clock-in/<employee_id>/`, `attendance/clock-out/<employee_id>/`
- Leaves: `leave/`, `leave/ajouter/`, `leave/<id>/modifier/`, `leave/<id>/supprimer/`, `leave/<id>/approve/`, `leave/<id>/reject/`

Note: Actual route names may vary slightly based on `employe/urls.py` definitions.

### Roles and Access
- Many management actions (departments, attendance CRUD, leave moderation) require a user with `is_staff` or `is_superuser`.
- Basic actions (e.g., viewing personal attendance or creating a leave request) require authentication.

### Models Overview
- `Department`: `name`, `description`
- `Employe`: `nom`, `email`, `poste`, `salaire`, `department`, `hire_date`
- `Attendance`: `employee`, `work_date`, `check_in`, `check_out`, `worked_hours`
- `LeaveRequest`: `employee`, `start_date`, `end_date`, `type`, `reason`, `status`, `approved_by`

### Development Tips
- Keep `DEBUG=True` for local development (default). Remember to disable it in production.
- SQLite is the default DB. For production, configure `DATABASES` in `employe_project/settings.py`.



