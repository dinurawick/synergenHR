# SynergenHR Demo Data Guide

## What is Demo Data?

The demo data provides a complete, realistic HR system with sample employees, departments, and business processes. It's perfect for:

- **Testing** the system before adding real data
- **Training** users on how to use SynergenHR
- **Demonstrations** to stakeholders
- **Development** and customization work

## What Demo Data Includes

### 🏢 Company Structure
- **3 Companies**: SynergenHR (HQ), SynergenHR Inc., SynergenHR Next Inc.
- **Multiple Departments**: HR, IT, Finance, Marketing, Operations
- **Job Positions**: Manager, Developer, Analyst, Coordinator, etc.
- **Work Types**: Full-time, Part-time, Contract, Intern

### 👥 Sample Employees
- **20+ Demo Employees** with complete profiles
- **Realistic Names**: Adam Luis, Sarah Johnson, Michael Chen, etc.
- **Complete Information**: Photos, contact details, addresses
- **Work Information**: Job positions, departments, salaries
- **Bank Details**: Sample banking information

### ⏰ Attendance Data
- **Historical Attendance**: Past 3 months of attendance records
- **Overtime Records**: Sample overtime entries
- **Attendance Requests**: Leave early, come late requests
- **Shift Schedules**: Different shift patterns

### 🏖️ Leave Management
- **Leave Types**: Annual Leave, Sick Leave, Maternity, Paternity
- **Leave Requests**: Approved, pending, and rejected requests
- **Leave Balances**: Current available leave for each employee
- **Holiday Calendar**: Public holidays and company holidays

### 💰 Payroll Data
- **Salary Structures**: Different pay scales and allowances
- **Payslips**: Sample monthly payslips for employees
- **Allowances**: Housing, Transport, Medical allowances
- **Deductions**: Tax, Insurance, Loan deductions
- **Loan Accounts**: Employee loan records

### 📋 Recruitment Pipeline
- **Job Postings**: Open positions across departments
- **Candidates**: Sample job applicants with resumes
- **Interview Schedules**: Upcoming and completed interviews
- **Recruitment Stages**: Application, Interview, Offer stages

### 🎯 Performance Management
- **Goals & Objectives**: Individual and team goals
- **Performance Reviews**: Quarterly and annual reviews
- **Feedback**: 360-degree feedback examples
- **Key Result Areas**: Performance metrics

### 📦 Asset Management
- **Company Assets**: Laptops, phones, furniture, vehicles
- **Asset Categories**: IT Equipment, Office Furniture, Vehicles
- **Asset Assignments**: Who has which assets
- **Asset Requests**: Pending asset allocation requests

### 🚀 Onboarding & Offboarding
- **Onboarding Tasks**: New employee checklists
- **Onboarding Stages**: Documentation, Training, Setup
- **Offboarding Process**: Exit procedures and tasks
- **Document Templates**: Offer letters, contracts

### ❓ Help & Support
- **FAQ Categories**: HR, IT, Payroll, Leave policies
- **FAQ Entries**: Common questions and answers
- **Help Tickets**: Sample support requests

## How to Load Demo Data

### Option 1: During Initial Deployment
When you run the deployment script, you'll be prompted:
```bash
./deployment/deploy.sh
# You'll see: "Would you like to load demo data? (y/N):"
# Type 'y' and press Enter
```

### Option 2: After Deployment (Docker)
```bash
# Make the script executable
chmod +x deployment/load_demo_data.sh

# Run the demo data loader
./deployment/load_demo_data.sh
```

### Option 3: Manual Installation
```bash
# Make the script executable
chmod +x deployment/load_demo_data_manual.sh

# Run the demo data loader
./deployment/load_demo_data_manual.sh
```

### Option 4: Individual Data Files
You can load specific data sets:
```bash
# Load only employee data
python manage.py loaddata load_data/employee_info_data.json

# Load only payroll data
python manage.py loaddata load_data/payroll_data.json

# Load only recruitment data
python manage.py loaddata load_data/recruitment_data.json
```

## Demo Data Loading Order

The data is loaded in dependency order:

1. **base_data.json** - Companies, departments, job positions
2. **user_data.json** - User accounts
3. **employee_info_data.json** - Employee profiles
4. **work_info_data.json** - Work information
5. **tags.json** - System tags
6. **mail_templates.json** - Email templates
7. **mail_automations.json** - Email automation rules
8. **leave_data.json** - Leave types and requests
9. **attendance_data.json** - Attendance records
10. **payroll_data.json** - Salary and payroll data
11. **recruitment_data.json** - Jobs and candidates
12. **asset_data.json** - Company assets
13. **pms_data.json** - Performance management
14. **onboarding_data.json** - Onboarding processes
15. **offboarding_data.json** - Offboarding processes
16. **project_data.json** - Project management
17. **faq_data.json** - Help and FAQ content

## Sample Demo Users

After loading demo data, you can log in as different users:

### Admin User
- **Username**: admin
- **Password**: admin
- **Role**: System Administrator
- **Access**: Full system access

### Sample Employees
- **Username**: adam.luis
- **Password**: (check user_data.json for passwords)
- **Role**: Employee
- **Access**: Employee self-service

### Managers
- **Username**: sarah.johnson
- **Password**: (check user_data.json for passwords)
- **Role**: Manager
- **Access**: Team management features

## Exploring Demo Data

### Dashboard Overview
After login, you'll see:
- **Employee Count**: 20+ demo employees
- **Attendance Summary**: Current month statistics
- **Leave Requests**: Pending approvals
- **Recruitment Pipeline**: Open positions

### Key Areas to Explore

#### Employee Management
- Go to **Employees** → **Employee Directory**
- View employee profiles with photos and details
- Check work information and salary details

#### Attendance Tracking
- Go to **Attendance** → **Attendance View**
- See daily attendance records
- Check overtime and attendance requests

#### Leave Management
- Go to **Leave** → **Leave Requests**
- View approved, pending, and rejected leaves
- Check leave balances and policies

#### Payroll System
- Go to **Payroll** → **Payslips**
- View monthly salary slips
- Check allowances and deductions

#### Recruitment
- Go to **Recruitment** → **Recruitments**
- View job postings and candidates
- Check interview schedules

## Customizing Demo Data

### Modify Company Information
1. Go to **Settings** → **Company**
2. Update company name, logo, and address
3. Add your actual company details

### Update Employee Information
1. Go to **Employees** → **Employee Directory**
2. Edit employee profiles
3. Replace with actual employee data

### Configure Leave Policies
1. Go to **Leave** → **Leave Types**
2. Modify leave policies to match your company
3. Update leave balances

## Removing Demo Data

If you want to start fresh after testing:

### Option 1: Reset Database (Docker)
```bash
# Stop services
docker-compose -f docker-compose.prod.yml down

# Remove database volume
docker volume rm synergenhr_synergenhr-data

# Restart services (creates fresh database)
docker-compose -f docker-compose.prod.yml up -d
```

### Option 2: Manual Database Reset
```bash
# Connect to database
docker-compose -f docker-compose.prod.yml exec db psql -U postgres

# Drop and recreate database
DROP DATABASE synergenhr;
CREATE DATABASE synergenhr;

# Run migrations again
python manage.py migrate
```

## Production Considerations

### ⚠️ Important Warnings

1. **Never load demo data on production systems**
2. **Change all default passwords immediately**
3. **Remove demo employees before adding real staff**
4. **Update company information with real details**
5. **Configure proper email settings**
6. **Set up proper backup procedures**

### Transitioning from Demo to Production

1. **Keep the structure**: Companies, departments, job positions
2. **Remove demo employees**: Delete sample employee records
3. **Clear demo data**: Remove sample attendance, leave, payroll records
4. **Add real employees**: Import or manually add actual staff
5. **Configure policies**: Update leave policies, salary structures
6. **Set up integrations**: Email, biometric devices, etc.

## Support

If you encounter issues with demo data:

1. **Check logs**: `docker-compose -f docker-compose.prod.yml logs`
2. **Verify data integrity**: Check for missing dependencies
3. **Reload specific data**: Load individual JSON files
4. **Reset if needed**: Start with fresh database

The demo data provides a comprehensive starting point for exploring all SynergenHR features!