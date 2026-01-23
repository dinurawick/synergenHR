#!/usr/bin/env python
import os
import sys
import django

# Add the project directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'horilla.settings')
django.setup()

from base.models import Company

def main():
    print("Current companies in database:")
    companies = Company.objects.all()
    
    for company in companies:
        print(f"  - ID {company.id}: '{company.company}'")
        
        # Update to ensure it ends with a dot
        if 'SynergenHR' in company.company and not company.company.endswith('.'):
            old_name = company.company
            company.company = company.company + '.'
            company.save()
            print(f"    Updated: '{old_name}' → '{company.company}'")

if __name__ == '__main__':
    main()