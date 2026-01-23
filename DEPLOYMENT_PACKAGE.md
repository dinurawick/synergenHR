# SynergenHR Deployment Package

## What This Package Contains

This deployment package will rebrand Horilla to SynergenHR on any laptop with the following changes:

✅ **Logo**: Replace with SynergenHR logo (SYN_LOGO.png)
✅ **Colors**: Blue (#0a0a5a) and Yellow (#dbf30d) 
✅ **Text**: All "Horilla" → "SynergenHR"
✅ **Database**: Update company names in existing database
✅ **Sidebar**: Show "SynergenHR" with correct logo

## Files Included in This Package

### 1. Logo Files
- `synergen/SYN_LOGO.png` - The SynergenHR logo

### 2. Scripts
- `deploy_synergenhr.bat` - Main deployment script (run this!)
- `update_company_name.py` - Updates database company names
- `fix_company_dots.py` - Removes unwanted dots from names

### 3. Updated Files
- `base/context_processors.py` - Default company name
- `static/src/scss/abstracts/_variables.scss` - Color scheme
- `static/build/css/style.min.css` - Compiled CSS with new colors
- `templates/login.html` - New login page design
- Multiple template files with SynergenHR branding

## Installation Instructions

### Step 1: Copy Files
1. Copy this entire folder to the target laptop
2. Make sure the `synergen/SYN_LOGO.png` file is present

### Step 2: Run Deployment
1. Open PowerShell as Administrator
2. Navigate to the Horilla folder
3. Run: `.\deploy_synergenhr.bat`

### Step 3: Clear Browser Cache
1. Press `Ctrl + Shift + Delete`
2. Clear cached images and files
3. Reload the page

## What the Script Does

1. **Activates virtual environment**
2. **Copies SynergenHR logo** to all required locations
3. **Updates database** - Changes all "Horilla" company names to "SynergenHR"
4. **Collects static files** - Deploys new logo and CSS
5. **Starts Django server**

## Expected Results

After running the deployment:
- Sidebar shows "SynergenHR" (no dots)
- SynergenHR logo appears in sidebar
- Login page has new blue/yellow design
- All colors are blue (#0a0a5a) and yellow (#dbf30d)
- Database company names updated

## Troubleshooting

If you see "Horilla" still:
1. Make sure the script completed successfully
2. Clear browser cache completely
3. Try incognito/private browsing mode
4. Check that Django server restarted

If logo doesn't show:
1. Verify `synergen/SYN_LOGO.png` exists
2. Run `python manage.py collectstatic --noinput`
3. Clear browser cache

## Support

If you encounter issues:
1. Check the console output for error messages
2. Ensure PostgreSQL is running
3. Verify virtual environment is activated
4. Make sure all files were copied correctly