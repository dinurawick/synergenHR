#!/usr/bin/env python
"""
Standalone script to update all email addresses from @horilla.com to @synergenhr.com

This script can be run directly with: python update_emails_script.py

Options:
    --dry-run: Show what would be changed without making actual changes
    --verbose: Show detailed output of all changes
"""

import os
import sys
import django
from django.db import transaction

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'horilla.settings')
django.setup()

from django.contrib.auth.models import User
from employee.models import Employee, EmployeeWorkInformation


def update_emails(dry_run=False, verbose=False):
    """
    Update all email addresses from @horilla.com to @synergenhr.com
    """
    if dry_run:
        print("DRY RUN MODE - No changes will be made")
        print("-" * 50)
    
    total_changes = 0
    
    with transaction.atomic():
        # Update Employee emails using bulk update
        employees = Employee.objects.filter(email__icontains='@horilla.com')
        employee_count = employees.count()
        
        print(f"Found {employee_count} employees with @horilla.com emails")
        
        if verbose or dry_run:
            for employee in employees:
                old_email = employee.email
                new_email = old_email.replace('@horilla.com', '@synergenhr.com')
                print(f'Employee: {employee.get_full_name()} - {old_email} -> {new_email}')
        
        if not dry_run and employee_count > 0:
            # Use raw SQL to avoid model validation
            from django.db import connection
            cursor = connection.cursor()
            cursor.execute("""
                UPDATE employee_employee 
                SET email = REPLACE(email, '@horilla.com', '@synergenhr.com') 
                WHERE email LIKE '%@horilla.com%'
            """)
        
        total_changes += employee_count
        
        # Update EmployeeWorkInformation emails
        work_infos = EmployeeWorkInformation.objects.filter(email__icontains='@horilla.com')
        work_count = work_infos.count()
        
        print(f"Found {work_count} work emails with @horilla.com")
        
        if verbose or dry_run:
            for work_info in work_infos:
                old_email = work_info.email
                new_email = old_email.replace('@horilla.com', '@synergenhr.com')
                print(f'Work Email: {work_info.employee_id.get_full_name()} - {old_email} -> {new_email}')
        
        if not dry_run and work_count > 0:
            cursor.execute("""
                UPDATE employee_employeeworkinformation 
                SET email = REPLACE(email, '@horilla.com', '@synergenhr.com') 
                WHERE email LIKE '%@horilla.com%'
            """)
        
        total_changes += work_count
        
        # Update User emails
        users = User.objects.filter(email__icontains='@horilla.com')
        user_count = users.count()
        
        print(f"Found {user_count} users with @horilla.com emails")
        
        if verbose or dry_run:
            for user in users:
                old_email = user.email
                new_email = old_email.replace('@horilla.com', '@synergenhr.com')
                print(f'User: {user.username} - {old_email} -> {new_email}')
        
        if not dry_run and user_count > 0:
            # Update both email and username if they match
            cursor.execute("""
                UPDATE auth_user 
                SET email = REPLACE(email, '@horilla.com', '@synergenhr.com'),
                    username = CASE 
                        WHEN username = email THEN REPLACE(username, '@horilla.com', '@synergenhr.com')
                        ELSE username 
                    END
                WHERE email LIKE '%@horilla.com%'
            """)
        
        total_changes += user_count
        
        # Update Candidate emails (if recruitment app is available)
        try:
            from recruitment.models import Candidate
            candidates = Candidate.objects.filter(email__icontains='@horilla.com')
            candidate_count = candidates.count()
            
            print(f"Found {candidate_count} candidates with @horilla.com emails")
            
            if verbose or dry_run:
                for candidate in candidates:
                    old_email = candidate.email
                    new_email = old_email.replace('@horilla.com', '@synergenhr.com')
                    print(f'Candidate: {candidate.name} - {old_email} -> {new_email}')
            
            if not dry_run and candidate_count > 0:
                cursor.execute("""
                    UPDATE recruitment_candidate 
                    SET email = REPLACE(email, '@horilla.com', '@synergenhr.com') 
                    WHERE email LIKE '%@horilla.com%'
                """)
            
            total_changes += candidate_count
        except ImportError:
            print("Recruitment app not available, skipping candidates")
        
        # Update EmailConfiguration (if base app is available)
        try:
            from base.models import EmailConfiguration
            configs = EmailConfiguration.objects.filter(from_email__icontains='@horilla.com')
            config_count = configs.count()
            
            print(f"Found {config_count} email configurations with @horilla.com")
            
            if verbose or dry_run:
                for config in configs:
                    old_email = config.from_email
                    new_email = old_email.replace('@horilla.com', '@synergenhr.com')
                    print(f'Email Config: {old_email} -> {new_email}')
            
            if not dry_run and config_count > 0:
                cursor.execute("""
                    UPDATE base_emailconfiguration 
                    SET from_email = REPLACE(from_email, '@horilla.com', '@synergenhr.com') 
                    WHERE from_email LIKE '%@horilla.com%'
                """)
            
            total_changes += config_count
        except ImportError:
            print("Base EmailConfiguration not available")
        
        # Update EmailLog records
        try:
            from base.models import EmailLog
            
            # Count from_email records
            from_logs = EmailLog.objects.filter(from_email__icontains='@horilla.com')
            from_count = from_logs.count()
            
            # Count to records  
            to_logs = EmailLog.objects.filter(to__icontains='@horilla.com')
            to_count = to_logs.count()
            
            log_count = from_count + to_count
            print(f"Found {log_count} email log records with @horilla.com")
            
            if verbose or dry_run:
                for log in from_logs:
                    old_email = log.from_email
                    new_email = old_email.replace('@horilla.com', '@synergenhr.com')
                    print(f'Email Log From: {old_email} -> {new_email}')
                
                for log in to_logs:
                    old_email = log.to
                    new_email = old_email.replace('@horilla.com', '@synergenhr.com')
                    print(f'Email Log To: {old_email} -> {new_email}')
            
            if not dry_run and log_count > 0:
                cursor.execute("""
                    UPDATE base_emaillog 
                    SET from_email = REPLACE(from_email, '@horilla.com', '@synergenhr.com') 
                    WHERE from_email LIKE '%@horilla.com%'
                """)
                cursor.execute("""
                    UPDATE base_emaillog 
                    SET to = REPLACE(to, '@horilla.com', '@synergenhr.com') 
                    WHERE to LIKE '%@horilla.com%'
                """)
            
            total_changes += log_count
        except ImportError:
            print("Base EmailLog not available")
        
        if dry_run:
            # Rollback transaction in dry run mode
            transaction.set_rollback(True)
    
    print("-" * 50)
    if dry_run:
        print(f'DRY RUN COMPLETE: Would update {total_changes} email addresses')
    else:
        print(f'Successfully updated {total_changes} email addresses from @horilla.com to @synergenhr.com')


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Update email addresses from @horilla.com to @synergenhr.com')
    parser.add_argument('--dry-run', action='store_true', help='Show what would be changed without making actual changes')
    parser.add_argument('--verbose', action='store_true', help='Show detailed output of all changes')
    
    args = parser.parse_args()
    
    update_emails(dry_run=args.dry_run, verbose=args.verbose)