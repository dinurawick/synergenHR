# SynergenHR EUK Cloud Deployment Guide

## Prerequisites
- EUK Cloud Linux server (Ubuntu 20.04+ recommended)
- SSH access to the server
- Domain name (optional but recommended)

## Step-by-Step Deployment

### 1. Connect to Your EUK Cloud Server

```bash
# Replace with your actual server details
ssh username@your-server-ip
```

### 2. Run Server Setup Script

```bash
# Download and run the server setup script
curl -fsSL https://raw.githubusercontent.com/dinurawick/synergenHR/main/deployment/server_setup.sh | bash

# Or if you prefer to download first:
wget https://raw.githubusercontent.com/dinurawick/synergenHR/main/deployment/server_setup.sh
chmod +x server_setup.sh
./server_setup.sh
```

### 3. Apply Docker Group Changes

```bash
# Apply docker group changes (choose one):
newgrp docker
# OR logout and login again
```

### 4. Clone Your Repository

```bash
cd /opt/synergenhr
git clone https://github.com/dinurawick/synergenHR.git .
```

### 5. Configure Environment

```bash
# Copy and edit the environment file
cp .env .env.production

# Edit the production environment file
nano .env.production
```

**Update these values in `.env.production`:**
```env
DEBUG=False
SECRET_KEY=your-super-secure-secret-key-here
ALLOWED_HOSTS=your-domain.com,www.your-domain.com,your-server-ip
CSRF_TRUSTED_ORIGINS=https://your-domain.com,https://www.your-domain.com
TIME_ZONE=UTC
```

### 6. Run Deployment

```bash
# Make deployment script executable
chmod +x deployment/deploy.sh

# Run the deployment
./deployment/deploy.sh
```

### 7. Configure Domain and SSL (Optional)

If you have a domain name:

```bash
# Point your domain DNS to your server IP first, then:
sudo certbot --nginx -d your-domain.com -d www.your-domain.com
```

### 8. Access Your Application

- **Without domain:** `http://your-server-ip:8000`
- **With domain:** `https://your-domain.com`

**Default login:**
- Username: `admin`
- Password: `admin`

⚠️ **Change the default password immediately!**

## Troubleshooting

### Check if services are running:
```bash
docker-compose -f docker-compose.prod.yml ps
```

### View logs:
```bash
docker-compose -f docker-compose.prod.yml logs
```

### Restart services:
```bash
docker-compose -f docker-compose.prod.yml restart
```

### Update application:
```bash
git pull origin main
docker-compose -f docker-compose.prod.yml up -d --build
```

## Backup

### Create backup:
```bash
chmod +x deployment/db_backup.sh
./deployment/db_backup.sh
```

### Restore backup:
```bash
# Stop services
docker-compose -f docker-compose.prod.yml down

# Restore database (replace with your backup file)
docker-compose -f docker-compose.prod.yml up -d db
docker-compose -f docker-compose.prod.yml exec -T db psql -U postgres synergenhr < backup_file.sql

# Start all services
docker-compose -f docker-compose.prod.yml up -d
```

## Support

If you encounter issues:
1. Check the logs using the commands above
2. Ensure all prerequisites are installed
3. Verify your domain DNS settings (if using a domain)
4. Check firewall settings

## Security Notes

- Change default passwords immediately
- Keep your system updated: `sudo apt update && sudo apt upgrade`
- Monitor your application logs regularly
- Set up regular backups