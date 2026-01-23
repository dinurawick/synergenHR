# How Django Creates Database Tables - Step by Step

## The Process: From Python Code to Database Tables

### Step 1: Django Model Definition (Python Code)

```python
# employee/models.py
class Employee(models.Model):
    badge_id = models.CharField(max_length=50, null=True, blank=True)
    employee_first_name = models.CharField(max_length=200, null=False)
    employee_last_name = models.CharField(max_length=200, null=True, blank=True)
    email = models.EmailField(max_length=254, unique=True)
    phone = models.CharField(max_length=25)
    dob = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=10, choices=[('male', 'Male'), ('female', 'Female')])
    # ... many more fields
```

### Step 2: Django Generates Migration File

When you run `python manage.py makemigrations`, Django creates:

```python
# employee/migrations/0001_initial.py
class Migration(migrations.Migration):
    operations = [
        migrations.CreateModel(
            name='Employee',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True)),
                ('badge_id', models.CharField(blank=True, max_length=50, null=True)),
                ('employee_first_name', models.CharField(max_length=200)),
                ('employee_last_name', models.CharField(blank=True, max_length=200, null=True)),
                ('email', models.EmailField(max_length=254, unique=True)),
                ('phone', models.CharField(max_length=25)),
                ('dob', models.DateField(blank=True, null=True)),
                ('gender', models.CharField(choices=[('male', 'Male'), ('female', 'Female')], max_length=10)),
                # ... more fields
            ],
        ),
    ]
```

### Step 3: Django Executes SQL Commands

When you run `python manage.py migrate`, Django generates and executes SQL:

```sql
-- Creates the actual table in PostgreSQL
CREATE TABLE "employee_employee" (
    "id" bigserial NOT NULL PRIMARY KEY,
    "badge_id" varchar(50) NULL,
    "employee_first_name" varchar(200) NOT NULL,
    "employee_last_name" varchar(200) NULL,
    "email" varchar(254) NOT NULL UNIQUE,
    "phone" varchar(25) NOT NULL,
    "dob" date NULL,
    "gender" varchar(10) NULL,
    -- ... more columns
);

-- Creates indexes
CREATE INDEX "employee_employee_email_idx" ON "employee_employee" ("email");
CREATE UNIQUE INDEX "employee_employee_email_unique" ON "employee_employee" ("email");
```

## Real Example: Complete Employee Table Creation

Here's what actually happens for the Employee table:

### Python Model → SQL Table

```python
# Python Model (employee/models.py)
class Employee(models.Model):
    badge_id = models.CharField(max_length=50, null=True, blank=True)
    employee_user_id = models.OneToOneField(User, on_delete=models.CASCADE, null=True)
    employee_first_name = models.CharField(max_length=200, null=False)
    employee_last_name = models.CharField(max_length=200, null=True, blank=True)
    employee_profile = models.ImageField(upload_to='employee_profiles/', null=True)
    email = models.EmailField(max_length=254, unique=True)
    phone = models.CharField(max_length=25)
    address = models.TextField(max_length=200, blank=True, null=True)
    country = models.CharField(max_length=100, blank=True, null=True)
    state = models.CharField(max_length=100, null=True, blank=True)
    city = models.CharField(max_length=30, null=True, blank=True)
    zip = models.CharField(max_length=20, null=True, blank=True)
    dob = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=10, choices=[('male', 'Male'), ('female', 'Female')])
    qualification = models.CharField(max_length=50, blank=True, null=True)
    experience = models.IntegerField(null=True, blank=True)
    marital_status = models.CharField(max_length=20, choices=[('single', 'Single'), ('married', 'Married')])
    children = models.IntegerField(null=True, blank=True)
    emergency_contact = models.CharField(max_length=25, null=True, blank=True)
    emergency_contact_name = models.CharField(max_length=200, null=True, blank=True)
    employee_work_info = models.OneToOneField('EmployeeWorkInformation', on_delete=models.CASCADE, null=True)
    employee_bank_details = models.OneToOneField('EmployeeBankDetails', on_delete=models.CASCADE, null=True)
    employee_salary_details = models.OneToOneField('EmployeeSalaryDetails', on_delete=models.CASCADE, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
```

### Becomes This SQL Table:

```sql
CREATE TABLE "employee_employee" (
    "id" bigserial NOT NULL PRIMARY KEY,
    "badge_id" varchar(50) NULL,
    "employee_user_id" bigint NULL UNIQUE,
    "employee_first_name" varchar(200) NOT NULL,
    "employee_last_name" varchar(200) NULL,
    "employee_profile" varchar(100) NULL,
    "email" varchar(254) NOT NULL UNIQUE,
    "phone" varchar(25) NOT NULL,
    "address" text NULL,
    "country" varchar(100) NULL,
    "state" varchar(100) NULL,
    "city" varchar(30) NULL,
    "zip" varchar(20) NULL,
    "dob" date NULL,
    "gender" varchar(10) NULL,
    "qualification" varchar(50) NULL,
    "experience" integer NULL,
    "marital_status" varchar(20) NULL,
    "children" integer NULL,
    "emergency_contact" varchar(25) NULL,
    "emergency_contact_name" varchar(200) NULL,
    "employee_work_info_id" bigint NULL UNIQUE,
    "employee_bank_details_id" bigint NULL UNIQUE,
    "employee_salary_details_id" bigint NULL UNIQUE,
    "is_active" boolean NOT NULL DEFAULT true,
    "created_at" timestamp with time zone NOT NULL,
    "updated_at" timestamp with time zone NOT NULL
);

-- Foreign key constraints
ALTER TABLE "employee_employee" ADD CONSTRAINT "employee_employee_user_id_fkey" 
    FOREIGN KEY ("employee_user_id") REFERENCES "auth_user" ("id");

ALTER TABLE "employee_employee" ADD CONSTRAINT "employee_employee_work_info_fkey" 
    FOREIGN KEY ("employee_work_info_id") REFERENCES "employee_employeeworkinformation" ("id");

-- Indexes
CREATE INDEX "employee_employee_email_idx" ON "employee_employee" ("email");
CREATE INDEX "employee_employee_user_id_idx" ON "employee_employee" ("employee_user_id");
CREATE UNIQUE INDEX "employee_employee_email_unique" ON "employee_employee" ("email");
```

## All Apps Create Their Tables

This process happens for EVERY app in SynergenHR:

### 1. Base App Tables
```python
# base/models.py creates:
base_company                 # Company information
base_department             # Departments  
base_jobposition           # Job positions
base_employeeshift         # Work shifts
# ... and more
```

### 2. Attendance App Tables
```python
# attendance/models.py creates:
attendance_attendance           # Daily attendance records
attendance_attendanceovertime  # Overtime tracking
attendance_attendancerequest   # Attendance corrections
# ... and more
```

### 3. Leave App Tables
```python
# leave/models.py creates:
leave_leavetype            # Types of leave
leave_leaverequest         # Leave applications
leave_availableleave       # Leave balances
# ... and more
```

### 4. Payroll App Tables
```python
# payroll/models.py creates:
payroll_payslip           # Monthly payslips
payroll_allowance         # Salary allowances
payroll_deduction         # Salary deductions
payroll_contract          # Employment contracts
# ... and more
```

## Migration Commands in Detail

### 1. Generate Migrations
```bash
python manage.py makemigrations
```
**Output:**
```
Migrations for 'base':
  base/migrations/0001_initial.py
    - Create model Company
    - Create model Department
    - Create model JobPosition
    
Migrations for 'employee':
  employee/migrations/0001_initial.py
    - Create model Employee
    - Create model EmployeeWorkInformation
    - Create model EmployeeBankDetails
    
Migrations for 'attendance':
  attendance/migrations/0001_initial.py
    - Create model Attendance
    - Create model AttendanceOverTime
    
# ... for all 15+ apps
```

### 2. Apply Migrations
```bash
python manage.py migrate
```
**Output:**
```
Operations to perform:
  Apply all migrations: admin, auth, base, employee, attendance, leave, payroll, recruitment, asset, pms, onboarding, offboarding, helpdesk, notifications, biometric, contenttypes, sessions

Running migrations:
  Applying contenttypes.0001_initial... OK
  Applying auth.0001_initial... OK
  Applying base.0001_initial... OK
  Applying employee.0001_initial... OK
  Applying attendance.0001_initial... OK
  Applying leave.0001_initial... OK
  Applying payroll.0001_initial... OK
  # ... continues for all apps
```

### 3. View Created Tables
```bash
# Connect to database
docker-compose exec db psql -U postgres synergenhr

# List all tables
\dt

# Sample output:
                    List of relations
 Schema |                Name                 | Type  |  Owner   
--------+-------------------------------------+-------+----------
 public | auth_group                         | table | postgres
 public | auth_user                          | table | postgres
 public | base_company                       | table | postgres
 public | base_department                    | table | postgres
 public | employee_employee                  | table | postgres
 public | employee_employeeworkinformation  | table | postgres
 public | attendance_attendance              | table | postgres
 public | leave_leaverequest                 | table | postgres
 public | payroll_payslip                    | table | postgres
 # ... 200+ more tables
```

## Data Relationships

Tables are connected through foreign keys:

```sql
-- Employee belongs to a department
employee_employee.employee_work_info_id → employee_employeeworkinformation.id
employee_employeeworkinformation.department_id → base_department.id

-- Attendance belongs to an employee  
attendance_attendance.employee_id → employee_employee.id

-- Leave request belongs to an employee
leave_leaverequest.employee_id → employee_employee.id

-- Payslip belongs to an employee
payroll_payslip.employee_id → employee_employee.id
```

## The Result

After migration completes, you have a fully functional HR database with:

- **200+ tables** for all HR functions
- **Proper relationships** between all data
- **Indexes** for fast queries
- **Constraints** for data integrity
- **Audit trails** for tracking changes
- **History tables** for maintaining records

All created automatically from the Python model definitions!