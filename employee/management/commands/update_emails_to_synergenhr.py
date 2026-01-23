"""
Django management command to update all email addresses from @horilla.com to @synergenhr.com

Usage:
    python manage.py update_emails_to_synergenhr [--dry-run] [--verbose]

Options:
    --dry-run: Show what would be changed without making actual changes
    --verbose: Show detailed output of all changes
"""

from django.core.management.base import BaseCommand
from django.db import transaction
from django.contrib.auth.models import User
from employee.models import Employee, EmployeeWorkInformation
from recruitment.models import Candidate
from base.models import EmailConfiguration, EmailLog
from outlook_auth.models import OutlookAccount


class Command(BaseCommand):
    help = 'Update all email addresses from @horilla.com to @synergenhr.com'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be changed without making actual changes',
        )
        parser.add_argument(
            '--verbose',
            action='store_true',
            help='Show detailed output of all changes',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        verbose = options['verbose']
        
        if dry_run:
            self.stdout.write(
                self.style.WARNING('DRY RUN MODE - No changes will be made')
            )
        
        total_changes = 0
        
        with transaction.atomic():
            # Update Employee emails
            total_changes += self.update_employee_emails(dry_run, verbose)
            
            # Update EmployeeWorkInformation emails
            total_changes += self.update_work_emails(dry_run, verbose)
            
            # Update User emails
            total_changes += self.update_user_emails(dry_run, verbose)
            
            # Update Candidate emails
            total_changes += self.update_candidate_emails(dry_run, verbose)
            
            # Update EmailConfiguration from_email
            total_changes += self.update_email_config(dry_run, verbose)
            
            # Update EmailLog emails
            total_changes += self.update_email_logs(dry_run, verbose)
            
            # Update OutlookAccount emails
            total_changes += self.update_outlook_accounts(dry_run, verbose)
            
            if dry_run:
                # Rollback transaction in dry run mode
                transaction.set_rollback(True)
        
        if dry_run:
            self.stdout.write(
                self.style.SUCCESS(
                    f'DRY RUN COMPLETE: Would update {total_changes} email addresses'
                )
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(
                    f'Successfully updated {total_changes} email addresses from @horilla.com to @synergenhr.com'
                )
            )

    def update_employee_emails(self, dry_run, verbose):
        """Update Employee model email field"""
        employees = Employee.objects.filter(email__icontains='@horilla.com')
        count = 0
        
        for employee in employees:
            old_email = employee.email
            new_email = old_email.replace('@horilla.com', '@synergenhr.com')
            
            if verbose or dry_run:
                self.stdout.write(f'Employee: {old_email} -> {new_email}')
            
            if not dry_run:
                employee.email = new_email
                employee.save()
            
            count += 1
        
        if count > 0:
            self.stdout.write(f'Employee emails: {count} records')
        
        return count

    def update_work_emails(self, dry_run, verbose):
        """Update EmployeeWorkInformation email field"""
        work_infos = EmployeeWorkInformation.objects.filter(email__icontains='@horilla.com')
        count = 0
        
        for work_info in work_infos:
            old_email = work_info.email
            new_email = old_email.replace('@horilla.com', '@synergenhr.com')
            
            if verbose or dry_run:
                self.stdout.write(f'Work Email: {old_email} -> {new_email}')
            
            if not dry_run:
                work_info.email = new_email
                work_info.save()
            
            count += 1
        
        if count > 0:
            self.stdout.write(f'Work emails: {count} records')
        
        return count

    def update_user_emails(self, dry_run, verbose):
        """Update User model email field"""
        users = User.objects.filter(email__icontains='@horilla.com')
        count = 0
        
        for user in users:
            old_email = user.email
            new_email = old_email.replace('@horilla.com', '@synergenhr.com')
            
            if verbose or dry_run:
                self.stdout.write(f'User: {old_email} -> {new_email}')
            
            if not dry_run:
                user.email = new_email
                # Also update username if it matches the email
                if user.username == old_email:
                    user.username = new_email
                user.save()
            
            count += 1
        
        if count > 0:
            self.stdout.write(f'User emails: {count} records')
        
        return count

    def update_candidate_emails(self, dry_run, verbose):
        """Update Candidate model email field"""
        try:
            from recruitment.models import Candidate
            candidates = Candidate.objects.filter(email__icontains='@horilla.com')
            count = 0
            
            for candidate in candidates:
                old_email = candidate.email
                new_email = old_email.replace('@horilla.com', '@synergenhr.com')
                
                if verbose or dry_run:
                    self.stdout.write(f'Candidate: {old_email} -> {new_email}')
                
                if not dry_run:
                    candidate.email = new_email
                    candidate.save()
                
                count += 1
            
            if count > 0:
                self.stdout.write(f'Candidate emails: {count} records')
            
            return count
        except ImportError:
            self.stdout.write('Recruitment app not available, skipping candidates')
            return 0

    def update_email_config(self, dry_run, verbose):
        """Update EmailConfiguration from_email field"""
        try:
            from base.models import EmailConfiguration
            configs = EmailConfiguration.objects.filter(from_email__icontains='@horilla.com')
            count = 0
            
            for config in configs:
                old_email = config.from_email
                new_email = old_email.replace('@horilla.com', '@synergenhr.com')
                
                if verbose or dry_run:
                    self.stdout.write(f'Email Config: {old_email} -> {new_email}')
                
                if not dry_run:
                    config.from_email = new_email
                    config.save()
                
                count += 1
            
            if count > 0:
                self.stdout.write(f'Email configurations: {count} records')
            
            return count
        except ImportError:
            return 0

    def update_email_logs(self, dry_run, verbose):
        """Update EmailLog from_email and to fields"""
        try:
            from base.models import EmailLog
            
            # Update from_email fields
            from_logs = EmailLog.objects.filter(from_email__icontains='@horilla.com')
            from_count = 0
            
            for log in from_logs:
                old_email = log.from_email
                new_email = old_email.replace('@horilla.com', '@synergenhr.com')
                
                if verbose or dry_run:
                    self.stdout.write(f'Email Log From: {old_email} -> {new_email}')
                
                if not dry_run:
                    log.from_email = new_email
                    log.save()
                
                from_count += 1
            
            # Update to fields
            to_logs = EmailLog.objects.filter(to__icontains='@horilla.com')
            to_count = 0
            
            for log in to_logs:
                old_email = log.to
                new_email = old_email.replace('@horilla.com', '@synergenhr.com')
                
                if verbose or dry_run:
                    self.stdout.write(f'Email Log To: {old_email} -> {new_email}')
                
                if not dry_run:
                    log.to = new_email
                    log.save()
                
                to_count += 1
            
            total_count = from_count + to_count
            if total_count > 0:
                self.stdout.write(f'Email logs: {total_count} records')
            
            return total_count
        except ImportError:
            return 0

    def update_outlook_accounts(self, dry_run, verbose):
        """Update OutlookAccount email field"""
        try:
            from outlook_auth.models import OutlookAccount
            accounts = OutlookAccount.objects.filter(outlook_email__icontains='@horilla.com')
            count = 0
            
            for account in accounts:
                old_email = account.outlook_email
                new_email = old_email.replace('@horilla.com', '@synergenhr.com')
                
                if verbose or dry_run:
                    self.stdout.write(f'Outlook Account: {old_email} -> {new_email}')
                
                if not dry_run:
                    account.outlook_email = new_email
                    account.save()
                
                count += 1
            
            if count > 0:
                self.stdout.write(f'Outlook accounts: {count} records')
            
            return count
        except ImportError:
            self.stdout.write('Outlook auth app not available, skipping outlook accounts')
            return 0