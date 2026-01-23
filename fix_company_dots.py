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
    print("Fixing company names to remove dots...")
    companies = Company.objects.all()
    
    for company in companies:
        old_name = company.company
        # Remove trailing dots and spaces, but keep "Inc." if it exists
        if company.company == 'SynergenHR.' or company.company == 'SynergenHR..':
            company.company = 'SynergenHR'
            company.save()
            print(f"  ✅ Updated: '{old_name}' → '{company.company}'")
        else:
            print(f"  ℹ️  Kept: '{company.company}' (no change needed)")

if __name__ == '__main__':
    main()