# SynergenHR Quick Reference

## Essential Commands

### Initial Deployment
```bash
# 1. Connect to server
ssh username@your-server-ip

# 2. Setup server
curl -fsSL https://raw.githubusercontent.com/dinurawick/synergenHR/main/deployment/server_setup.sh | bash
newgrp docker

# 3. Clone and deploy
cd /opt/synergenhr
git clone https://github.com/dinurawick/synergenHR.git .
chmod +x deployment/deploy.sh
./deployment/deploy.sh
```

### Daily Management
```bash
# Check status
docker-compose -f docker-compose.prod.yml ps

# View logs
docker-compose -f docker-compose.prod.yml logs

# Restart services
docker-compose -f docker-compose.prod.yml restart

# Create backup
./deployment/db_backup.sh
```

### Access Points
- **Application**: `http://your-server-ip:8000`
- **Admin Login**: `admin` / `admin`
- **Database**: `docker-compose -f docker-compose.prod.yml exec db psql -U postgres synergenhr`

### Emergency Commands
```bash
# Stop everything
docker-compose -f docker-compose.prod.yml down

# Start everything
docker-compose -f docker-compose.prod.yml up -d

# Reset database (⚠️ DANGER - loses all data)
docker-compose -f docker-compose.prod.yml down
docker volume rm synergenhr_synergenhr-data
docker-compose -f docker-compose.prod.yml up -d
```

## File Locations
- **Application**: `/opt/synergenhr/`
- **Backups**: `/opt/synergenhr/backups/`
- **Logs**: `docker-compose -f docker-compose.prod.yml logs`
- **Config**: `/opt/synergenhr/.env.production`