# SynergenHR - Quick Start Guide

## 🚀 Start the Server

Simply run:
```cmd
restart_server.bat
```

Or manually:
```cmd
.\horillavenv\Scripts\activate
python manage.py collectstatic --noinput --clear
python manage.py runserver
```

Then open: **http://localhost:8000**

## 🎨 Your Colors

- **Blue**: `#0a0a5a` (Dark Navy)
- **Yellow**: `#dbf30d` (Bright Yellow)

## ✅ What Changed

1. **Logo**: Your SynergenHR logo is now on all pages
2. **Colors**: Everything is now blue and yellow
3. **Text**: All "Horilla" changed to "SynergenHR"
4. **Branding**: Complete visual rebrand

## 🔍 First Time Setup

If this is your first time running:

1. Make sure PostgreSQL is running
2. Database should be: `horilla_main` with user `horilla:horilla`
3. Run migrations if needed:
   ```cmd
   python manage.py migrate
   ```
4. Create superuser:
   ```cmd
   python manage.py createsuperuser
   ```

## 💡 Tips

- **Clear browser cache** if you don't see changes (Ctrl+Shift+Delete)
- **Hard refresh** the page (Ctrl+F5)
- Check `REBRANDING_SUMMARY.md` for full details

## 🐛 Troubleshooting

**Colors not showing?**
- Run `python manage.py collectstatic --noinput --clear`
- Clear browser cache
- Hard refresh (Ctrl+F5)

**Database errors?**
- Check PostgreSQL is running
- Verify credentials in `.env` file
- Database name: `horilla_main`
- User: `horilla`, Password: `horilla`

**Logo not showing?**
- Check `static/images/ui/auth-logo.png` exists
- Run collectstatic command
- Clear browser cache

---

**You're all set!** Enjoy your rebranded SynergenHR system! 🎉
