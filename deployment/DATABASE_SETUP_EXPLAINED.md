# SynergenHR Database Setup - Detailed Explanation

## Overview

The database setup happens in several phases, depending on which deployment method you choose.

## Phase 1: Database Container/Service Creation

### Docker Method (Recommended)
```yaml
# docker-compose.yaml creates:
db:
  image: postgres:16-bullseye          # Downloads PostgreSQL 16
  environment:
    POSTGRES_DB: synergenhr            # Creates database named 'synergenhr'
    POSTGRES_USER: postgres            # Creates user 'postgres'
    POSTGRES_PASSWORD: postgres        # Sets password 'postgres'
  volumes:
    - synergenhr-data:/var/lib/postgresql/data  # Persistent storage
```

**What happens:**
1. Docker downloads PostgreSQL 16 image (~200MB)
2. Creates a container with PostgreSQL running
3. Automatically creates the database and user
4. Sets up persistent storage so data survives container restarts

### Manual Method
```bash
# Installs PostgreSQL directly on server
sudo apt install postgresql postgresql-contrib

# Creates database and user manually
sudo -u postgres psql
CREATE DATABASE synergenhr;
CREATE USER synergenhr WITH PASSWORD 'synergenhr';
GRANT ALL PRIVILEGES ON DATABASE synergenhr TO synergenhr;
```

## Phase 2: Django Database Schema Creation

Once the database is running, Django creates all the tables:

### Step 1: Generate Migration Files
```bash
python3 manage.py makemigrations
```

**This scans all Django apps and creates migration files for:**
- `base` app: Companies, departments, job positions, users
- `employee` app: Employee profiles, work info, personal info
- `attendance` app: Attendance records, shifts, overtime
- `leave` app: Leave types, leave requests, leave allocations
- `payroll` app: Salary structures, payslips, allowances, deductions
- `recruitment` app: Job postings, candidates, interviews
- `asset` app: Company assets, asset assignments
- `pms` app: Performance management, goals, reviews
- And many more...

### Step 2: Apply Migrations
```bash
python3 manage.py migrate
```

**This creates approximately 200+ database tables including:**

#### Core Tables:
- `auth_user` - Django user authentication
- `django_content_type` - Content type framework
- `django_migrations` - Migration tracking

#### SynergenHR Business Tables:
- `base_company` - Company information
- `base_department` - Departments
- `base_jobposition` - Job positions
- `employee_employee` - Employee master data
- `employee_employeeworkinformation` - Work details
- `attendance_attendance` - Attendance records
- `leave_leaverequest` - Leave applications
- `payroll_payslip` - Salary slips
- `recruitment_recruitment` - Job postings
- And 150+ more tables...

### Step 3: Create Static Files
```bash
python3 manage.py collectstatic --noinput
```

**Collects all CSS, JavaScript, images from:**
- Django admin interface
- SynergenHR custom styles
- Third-party libraries (Bootstrap, jQuery, etc.)
- Stores them in `/staticfiles/` directory

### Step 4: Create Initial Admin User
```bash
python3 manage.py createhorillauser \
  --first_name admin \
  --last_name admin \
  --username admin \
  --password admin \
  --email admin@example.com \
  --phone 1234567890
```

**This creates:**
- Admin user in `auth_user` table
- Employee record in `employee_employee` table
- Links the user to employee record
- Sets up basic company structure

## Phase 3: Database Connection Configuration

### Environment Variables
```env
# Database connection string
DATABASE_URL=postgresql://postgres:postgres@db:5432/synergenhr

# Or individual components
DB_ENGINE=django.db.backends.postgresql
DB_NAME=synergenhr
DB_USER=postgres
DB_PASSWORD=postgres
DB_HOST=db  # Docker service name, or 'localhost' for manual install
DB_PORT=5432
```

### Django Settings
```python
# horilla/settings.py
if env("DATABASE_URL", default=None):
    DATABASES = {
        "default": env.db(),  # Parses DATABASE_URL automatically
    }
else:
    DATABASES = {
        "default": {
            "ENGINE": env("DB_ENGINE", default="django.db.backends.sqlite3"),
            "NAME": env("DB_NAME", default="TestDB_Horilla.sqlite3"),
            "USER": env("DB_USER", default=""),
            "PASSWORD": env("DB_PASSWORD", default=""),
            "HOST": env("DB_HOST", default=""),
            "PORT": env("DB_PORT", default=""),
        }
    }
```

## Database Schema Overview

The database contains these main functional areas:

### 1. User Management & Authentication
- User accounts, permissions, groups
- Employee profiles and personal information
- Company organizational structure

### 2. Human Resources Core
- **Recruitment**: Job postings, candidates, interviews, hiring pipeline
- **Onboarding**: New employee tasks, document collection
- **Employee Management**: Personal info, work info, documents
- **Offboarding**: Exit procedures, asset return

### 3. Time & Attendance
- **Attendance**: Clock in/out, work hours tracking
- **Leave Management**: Leave types, requests, approvals, balances
- **Shifts**: Shift schedules, rotating shifts, overtime

### 4. Payroll & Compensation
- **Salary Structures**: Basic pay, allowances, deductions
- **Payslip Generation**: Monthly salary calculations
- **Reimbursements**: Expense claims and approvals
- **Loans**: Employee loans and repayments

### 5. Performance & Development
- **Goal Setting**: Individual and team objectives
- **Performance Reviews**: Periodic evaluations
- **Feedback**: 360-degree feedback system

### 6. Asset Management
- **Asset Tracking**: Company assets, assignments
- **Maintenance**: Asset maintenance schedules

### 7. System & Configuration
- **Audit Logs**: Track all system changes
- **Notifications**: System notifications and alerts
- **Settings**: Company-wide configurations

## Data Persistence & Backup

### Docker Volume Storage
```bash
# Data is stored in Docker volume
docker volume ls
# Shows: synergenhr_synergenhr-data

# Volume location on host system
docker volume inspect synergenhr_synergenhr-data
# Shows actual path: /var/lib/docker/volumes/synergenhr_synergenhr-data/_data
```

### Backup Process
```bash
# Create backup
docker-compose exec -T db pg_dump -U postgres synergenhr > backup.sql

# Restore backup
docker-compose exec -T db psql -U postgres synergenhr < backup.sql
```

## Security Considerations

### Database Security
- Database runs in isolated Docker container
- Only accessible from Django application container
- Uses strong authentication (scram-sha-256)
- Regular security updates via base image updates

### Connection Security
- Database connections use encrypted passwords
- No direct external access to database port
- All connections go through Django ORM (prevents SQL injection)

## Monitoring & Maintenance

### Health Checks
```bash
# Check database status
docker-compose exec db pg_isready -U postgres

# View database size
docker-compose exec db psql -U postgres -c "SELECT pg_size_pretty(pg_database_size('synergenhr'));"

# Check active connections
docker-compose exec db psql -U postgres -c "SELECT count(*) FROM pg_stat_activity;"
```

### Performance Monitoring
```bash
# View slow queries
docker-compose exec db psql -U postgres -c "SELECT query, mean_time, calls FROM pg_stat_statements ORDER BY mean_time DESC LIMIT 10;"

# Check table sizes
docker-compose exec db psql -U postgres synergenhr -c "SELECT schemaname,tablename,pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as size FROM pg_tables ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC LIMIT 10;"
```

This comprehensive setup ensures your SynergenHR database is properly configured, secure, and ready for production use.