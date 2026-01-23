#!/usr/bin/env python
"""
SynergenHR Sidebar Setup Script
This script ensures the sidebar shows "SynergenHR" with the correct logo
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
    """Copy SynergenHR logo to all required locations"""
    print("📁 Copying SynergenHR logo files...")
    
    source_logo = "synergen/SYN_LOGO.png"
    
    if not os.path.exists(source_logo):
        print(f"❌ ERROR: Logo file not found: {source_logo}")
        print("   Please make sure synergen/SYN_LOGO.png exists")
        return False
    
    # Logo locations for the sidebar and login
    logo_locations = [
        "static/images/ui/auth-logo.png",
        "static/images/ui/horilla-logo.png",
        "media/base/icon/SynergenHR_1.png",
        "media/base/icon/SynergenHR_2.png", 
        "media/base/icon/SynergenHR_3.png"
    ]
    
    # Create directories if they don't exist
    for logo_path in logo_locations:
        os.makedirs(os.path.dirname(logo_path), exist_ok=True)
        
        try:
            shutil.copy2(source_logo, logo_path)
            print(f"   ✅ Copied to {logo_path}")
        except Exception as e:
            print(f"   ❌ Failed to copy to {logo_path}: {e}")
    
    return True

def update_company_names():
    """Update company names in database to show SynergenHR in sidebar"""
    print("\n🔍 Updating company names in database...")
    
    # Find all companies that need updating
    companies_to_update = Company.objects.filter(
        models.Q(company__icontains='horilla') | 
        models.Q(company__exact='SynergenHR.') |
        models.Q(company__exact='SynergenHR..')
    )
    
    if not companies_to_update.exists():
        print("✅ No companies need updating")
        return
    
    print(f"📋 Found {companies_to_update.count()} companies to update:")
    
    for company in companies_to_update:
        old_name = company.company
        
        # Clean up the name
        new_name = old_name.replace('Horilla', 'SynergenHR').replace('horilla', 'SynergenHR')
        
        # Remove extra dots but keep "Inc." if it exists
        if new_name.endswith('..'):
            new_name = new_name[:-2]
        elif new_name.endswith('.') and not new_name.endswith('Inc.'):
            new_name = new_name[:-1]
        
        print(f"   • '{old_name}' → '{new_name}'")
        
        company.company = new_name
        company.save()
    
    print(f"\n✅ Successfully updated {companies_to_update.count()} companies!")

def main():
    """Main function"""
    print("🚀 Setting up SynergenHR Sidebar...")
    print("=" * 50)
    
    # Step 1: Copy logo files
    if not copy_logo_files():
        return False
    
    # Step 2: Update company names
    update_company_names()
    
    print("\n" + "=" * 50)
    print("🎉 Sidebar setup complete!")
    print("\n📝 Next steps:")
    print("1. Run: python manage.py collectstatic --noinput")
    print("2. Restart Django server")
    print("3. Clear browser cache (Ctrl+Shift+Delete)")
    print("4. Reload page to see 'SynergenHR' in sidebar!")
    
    return True

if __name__ == '__main__':
    try:
        from django.db import models
        main()
    except Exception as e:
        print(f"❌ Error: {e}")
        print("Make sure you're in the correct directory and Django is set up properly.")