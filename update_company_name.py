#!/usr/bin/env python
"""
Complete SynergenHR Rebranding Script
- Updates company names in database from Horilla to SynergenHR
- Copies SynergenHR logo to company icon locations
- Updates all branding in the database

Run this with: python update_company_name.py
"""

import os
import sys
import django
import shutil

# Add the project directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'horilla.settings')
django.setup()

from base.models import Company

def copy_logo_files():
    """Copy SynergenHR logo to company icon locations"""
    print("📁 Copying SynergenHR logo to company icon locations...")
    
    source_logo = "synergen/SYN_LOGO.png"
    
    if not os.path.exists(source_logo):
        print(f"❌ Source logo not found: {source_logo}")
        return False
    
    # Create media directories if they don't exist
    icon_dir = "media/base/icon"
    os.makedirs(icon_dir, exist_ok=True)
    
    # Copy logo to company icon locations
    icon_files = [
        "media/base/icon/SynergenHR_1.png",
        "media/base/icon/SynergenHR_2.png", 
        "media/base/icon/SynergenHR_3.png"
    ]
    
    for icon_file in icon_files:
        try:
            shutil.copy2(source_logo, icon_file)
            print(f"   ✅ Copied to {icon_file}")
        except Exception as e:
            print(f"   ❌ Failed to copy to {icon_file}: {e}")
    
    return True

def update_company_names():
    """Update all Horilla company names to SynergenHR"""
    
    print("🔍 Looking for companies with 'Horilla' in the name...")
    
    # Find all companies with "Horilla" in the name
    horilla_companies = Company.objects.filter(company__icontains='horilla')
    
    if not horilla_companies.exists():
        print("✅ No companies found with 'Horilla' in the name.")
        return
    
    print(f"📋 Found {horilla_companies.count()} companies to update:")
    
    for company in horilla_companies:
        old_name = company.company
        # Replace Horilla with SynergenHR (case insensitive) and remove any dots
        new_name = old_name.replace('Horilla', 'SynergenHR').replace('horilla', 'SynergenHR')
        # Remove any trailing dots and spaces
        new_name = new_name.rstrip('. ')
        
        print(f"   • '{old_name}' → '{new_name}'")
        
        # Update the company name
        company.company = new_name
        
        # Update icon path if it contains Horilla
        if company.icon and 'Horilla' in str(company.icon):
            old_icon = str(company.icon)
            new_icon = old_icon.replace('Horilla', 'SynergenHR')
            company.icon = new_icon
            print(f"     Icon: '{old_icon}' → '{new_icon}'")
        
        company.save()
    
    print(f"\n✅ Successfully updated {horilla_companies.count()} companies!")

def main():
    """Main function to run all updates"""
    print("🚀 Starting SynergenHR Rebranding...")
    print("=" * 50)
    
    # Step 1: Copy logo files
    copy_logo_files()
    
    print()
    
    # Step 2: Update company names in database
    update_company_names()
    
    print()
    print("=" * 50)
    print("🎉 SynergenHR Rebranding Complete!")
    print()
    print("📝 Next Steps:")
    print("1. Restart your Django server: python manage.py runserver")
    print("2. Clear your browser cache (Ctrl+Shift+Delete)")
    print("3. Reload the page to see 'SynergenHR' in the sidebar!")

if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print(f"❌ Error: {e}")
        print("Make sure you're in the correct directory and Django is set up properly.")