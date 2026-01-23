# SynergenHR Complete Database Schema

## How Tables Are Created

Django automatically creates database tables from Python model definitions. When you run:

```bash
python manage.py makemigrations  # Generates migration files
python manage.py migrate         # Creates actual database tables
```

Django scans all apps and creates tables based on the models defined in each app's `models.py` file.

## Complete Table List

Here are ALL the tables that get created in your SynergenHR database:

### Core Django Tables (Framework)
```sql
-- User authentication and permissions
auth_user                    -- User accounts
auth_group                   -- User groups
auth_permission             -- System permissions
auth_user_groups            -- User-group relationships
auth_user_user_permissions  -- User-specific permissions

-- Django framework tables
django_content_type         -- Content type framework
django_migrations          -- Migration tracking
django_session             -- User sessions
django_admin_log           -- Admin interface logs
```

### Base App Tables (Company Structure)
```sql
-- Company and organizational structure
base_company                -- Company information
base_department            -- Departments
base_jobposition           -- Job positions/roles
base_jobrole              -- Job role definitions
base_worktype             -- Work types (full-time, part-time, etc.)
base_employeetype         -- Employee types (permanent, contract, etc.)
base_employeeshift        -- Work shifts
base_employeeshiftday     -- Shift day configurations
base_shiftrequest         -- Shift change requests
base_worktyperequest      -- Work type change requests
base_rotatingshift        -- Rotating shift patterns
base_rotatingshiftassign  -- Rotating shift assignments
base_tags                 -- System tags
base_multipleapprovalcondition -- Approval workflow conditions

-- Audit and history
base_historicalcompany    -- Company change history
base_historicaldepartment -- Department change history
base_historicaljobposition -- Job position change history
```

### Employee App Tables (Employee Management)
```sql
-- Core employee data
employee_employee                    -- Employee master data
employee_employeeworkinformation    -- Work-related information
employee_employeebankdetails        -- Bank account details
employee_employeesalarydetails      -- Salary information

-- Employee actions and discipline
employee_actiontype                 -- Disciplinary action types
employee_disciplinaryaction        -- Disciplinary actions taken
employee_bonuspoint                -- Employee bonus points
employee_penaltyaccount            -- Penalty tracking

-- Employee policies and documents
employee_policy                    -- Company policies
employee_employeepolicy           -- Employee-policy assignments

-- History tables (track changes)
employee_historicalemployee                    
employee_historicalemployeeworkinformation    
employee_historicalemployeebankdetails        
employee_historicalemployeesalarydetails      
```

### Attendance App Tables (Time Tracking)
```sql
-- Attendance tracking
attendance_attendance              -- Daily attendance records
attendance_attendanceovertime     -- Overtime records
attendance_attendancerequest      -- Attendance correction requests
attendance_attendancevalidationrequest -- Attendance validation requests

-- Grace time and late policies
attendance_gracetime             -- Grace time configurations
attendance_attendancelatecomeearlyout -- Late/early policies

-- Attendance activities
attendance_attendanceactivity    -- Attendance-related activities

-- History tables
attendance_historicalattendance
attendance_historicalattendanceovertime
```

### Leave App Tables (Leave Management)
```sql
-- Leave types and policies
leave_leavetype                   -- Types of leave (sick, vacation, etc.)
leave_availableleave             -- Available leave balances
leave_leaverequest               -- Leave applications
leave_leaverequestcomment        -- Comments on leave requests
leave_leaverequestconditionapproval -- Conditional approvals

-- Leave allocation and restrictions
leave_leaveallocationrequest     -- Leave allocation requests
leave_restrictleave              -- Leave restrictions
leave_companyLeave               -- Company-wide leave policies

-- Holiday management
leave_holiday                    -- Public holidays
leave_holidayrequest            -- Holiday requests

-- Leave encashment
leave_leaveencashmentrequest    -- Leave encashment requests
leave_leaveencashmentgeneralsettings -- Encashment settings

-- History tables
leave_historicalleaverequest
leave_historicalavailableleave
```

### Payroll App Tables (Salary & Compensation)
```sql
-- Salary structures
payroll_allowance               -- Salary allowances
payroll_deduction              -- Salary deductions
payroll_payslip                -- Monthly payslips
payroll_payslipovertime        -- Overtime in payslips
payroll_contract               -- Employment contracts
payroll_contractallowance      -- Contract-specific allowances
payroll_contractdeduction      -- Contract-specific deductions

-- Loan management
payroll_loanaccount           -- Employee loans
payroll_installment           -- Loan installments

-- Reimbursements
payroll_reimbursement         -- Expense reimbursements
payroll_reimbursementrequest  -- Reimbursement requests

-- Tax and filing
payroll_taxbracket           -- Tax brackets
payroll_filingstatustype    -- Tax filing status types

-- Federal and state taxes
payroll_federaltax           -- Federal tax configurations
payroll_statetax             -- State tax configurations

-- History tables
payroll_historicalpayslip
payroll_historicalcontract
```

### Recruitment App Tables (Hiring Process)
```sql
-- Job postings and recruitment
recruitment_recruitment          -- Job postings
recruitment_recruitmentsurvey   -- Recruitment surveys
recruitment_recruitmentgeneralsettings -- Recruitment settings

-- Candidates
recruitment_candidate           -- Job candidates
recruitment_candidaterating    -- Candidate ratings
recruitment_candidatehistory   -- Candidate interaction history

-- Interview process
recruitment_stage              -- Interview stages
recruitment_interviewschedule  -- Interview scheduling
recruitment_interviewquestion  -- Interview questions

-- Skills and qualifications
recruitment_skill              -- Required skills
recruitment_candidateskill     -- Candidate skills
recruitment_recruitmentskill   -- Job-skill requirements

-- Recruitment pipeline
recruitment_recruitmentmailtemplate -- Email templates
recruitment_rejected_candidate      -- Rejected candidates

-- History tables
recruitment_historicalrecruitment
recruitment_historicalcandidate
```

### Asset App Tables (Asset Management)
```sql
-- Asset tracking
asset_asset                    -- Company assets
asset_assetcategory           -- Asset categories
asset_assetassignment         -- Asset assignments to employees
asset_assetrequest            -- Asset requests
asset_returnasset             -- Asset returns

-- Asset history and tracking
asset_historicalasset
asset_historicalassetassignment
```

### PMS App Tables (Performance Management)
```sql
-- Performance management
pms_period                    -- Performance review periods
pms_keyresultarea            -- Key result areas
pms_objective                -- Performance objectives
pms_keyresult                -- Key results
pms_employeeobjective       -- Employee-specific objectives
pms_employeekeyresult       -- Employee key results

-- Performance reviews
pms_feedback                 -- Performance feedback
pms_answer                   -- Review answers
pms_question                 -- Review questions
pms_questiontemplate        -- Question templates
pms_questionoptions         -- Question options

-- Performance tracking
pms_comment                  -- Performance comments
pms_anonymousfeedback       -- Anonymous feedback

-- History tables
pms_historicalperiod
pms_historicalobjective
```

### Onboarding App Tables (New Employee Process)
```sql
-- Onboarding process
onboarding_onboarding           -- Onboarding processes
onboarding_onboardingtask      -- Onboarding tasks
onboarding_onboardingstage     -- Onboarding stages
onboarding_candidateselection  -- Selected candidates
onboarding_onboardingemployee  -- Employee onboarding records

-- History tables
onboarding_historicalonboarding
```

### Offboarding App Tables (Employee Exit)
```sql
-- Offboarding process
offboarding_offboarding        -- Offboarding processes
offboarding_offboardingtask   -- Exit tasks
offboarding_offboardingstage  -- Exit stages
offboarding_offboardingemployee -- Employee exit records
offboarding_resignation       -- Resignation requests

-- History tables
offboarding_historicaloffboarding
```

### Helpdesk App Tables (Support System)
```sql
-- Help desk and support
helpdesk_ticket              -- Support tickets
helpdesk_tickettype         -- Ticket categories
helpdesk_faq                -- Frequently asked questions
helpdesk_faqcategory       -- FAQ categories
helpdesk_ticketcomment     -- Ticket comments

-- History tables
helpdesk_historicalticket
```

### Notification App Tables (System Notifications)
```sql
-- Notification system
notifications_notification  -- System notifications
```

### Biometric App Tables (Biometric Integration)
```sql
-- Biometric device integration
biometric_biometricdevices  -- Biometric device configurations
biometric_biometricemployees -- Employee biometric data
```

### Audit App Tables (System Auditing)
```sql
-- Audit logging
horilla_audit_auditlog      -- System audit logs
horilla_audit_auditlogentry -- Detailed audit entries
```

### Dynamic Fields App Tables (Custom Fields)
```sql
-- Custom field system
dynamic_fields_dynamicfield -- Custom field definitions
dynamic_fields_dynamicfieldvalue -- Custom field values
```

## Table Relationships

The tables are interconnected through foreign keys:

```sql
-- Example relationships:
employee_employee.user_id → auth_user.id
employee_employee.employee_work_info_id → employee_employeeworkinformation.id
attendance_attendance.employee_id → employee_employee.id
leave_leaverequest.employee_id → employee_employee.id
payroll_payslip.employee_id → employee_employee.id
```

## Indexes and Constraints

Django automatically creates:
- Primary key indexes on all `id` fields
- Foreign key indexes for relationships
- Unique constraints where specified
- Database-level constraints for data integrity

## Data Types Used

Common field types in the schema:
- `BigAutoField` - Auto-incrementing primary keys
- `CharField` - Text fields with max length
- `TextField` - Long text fields
- `IntegerField` - Integer numbers
- `DecimalField` - Decimal numbers (for money)
- `DateTimeField` - Date and time stamps
- `BooleanField` - True/false values
- `ForeignKey` - Relationships to other tables
- `ManyToManyField` - Many-to-many relationships

## Total Table Count

**Approximately 200+ tables** are created, including:
- ~50 main business tables
- ~80 history tables (for audit trails)
- ~30 relationship tables (many-to-many)
- ~40 configuration and lookup tables

This comprehensive schema supports all HR functions from recruitment to offboarding, with full audit trails and historical data tracking.