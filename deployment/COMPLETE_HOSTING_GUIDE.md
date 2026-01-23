# Complete SynergenHR Hosting Guide for EUK Cloud Linux

## Overview

This guide will walk you through hosting SynergenHR on EUK Cloud Linux from scratch. We'll use Docker for easy deployment and management.

## Prerequisites

### What You Need
- **EUK Cloud Linux Server** (Ubuntu 20.04+ recommended)
- **Minimum Server Specs**: 2 CPU cores, 4GB RAM, 20GB storage
- **SSH access** to your server
- **Domain name** (optional but recommended)
- **Your SynergenHR code** (already on GitHub)

### What You'll Get
- **Complete HR Management System** with all modules
- **PostgreSQL Database** with demo data
- **Nginx Reverse Proxy** for production
- **SSL Certificate** support
- **Automated backups** and maintenance scripts

---

## Step 1: Server Setup and Access

### 1.1 Connect to Your EUK Cloud Server

**From Windows (PowerShell):**
```powershell
# Replace with your actual server details
ssh username@your-server-ip

# Example:
ssh ubuntu@203.0.113.10
```

**From Windows (PuTTY):**
1. Download and install PuTTY
2. Enter your server IP address
3. Use your username and password/SSH key

### 1.2 Update Your Server
```bash
# Update package lists and upgrade system
sudo apt update && sudo apt upgrade -y

# Install essential tools
sudo apt install -y curl wget git unzip htop nano
```

---

## Step 2: Install Required Software

### 2.1 Run the Automated Server Setup
```bash
# Download and run the server setup script
curl -fsSL https://raw.githubusercontent.com/dinurawick/synergenHR/main/deployment/server_setup.sh | bash

# Or download first and inspect:
wget https://raw.githubusercontent.com/dinurawick/synergenHR/main/deployment/server_setup.sh
chmod +x server_setup.sh
./server_setup.sh
```

**This installs:**
- Docker and Docker Compose
- Python 3 and pip
- Nginx web server
- Certbot for SSL certificates
- Firewall configuration

### 2.2 Apply Docker Group Changes
```bash
# Apply docker group changes (choose one):
newgrp docker

# OR logout and login again:
exit
# Then SSH back in
```

---

## Step 3: Deploy SynergenHR

### 3.1 Clone Your Repository
```bash
# Create application directory
sudo mkdir -p /opt/synergenhr
sudo chown $USER:$USER /opt/synergenhr

# Clone your SynergenHR repository
cd /opt/synergenhr
git clone https://github.com/dinurawick/synergenHR.git .
```

### 3.2 Configure Environment
```bash
# Copy environment template
cp .env .env.production

# Edit the production environment file
nano .env.production
```

**Update these values in `.env.production`:**
```env
# IMPORTANT: Change these values!
DEBUG=False
SECRET_KEY=your-super-secure-secret-key-here-generate-new-one
ALLOWED_HOSTS=your-domain.com,www.your-domain.com,your-server-ip
CSRF_TRUSTED_ORIGINS=https://your-domain.com,https://www.your-domain.com
TIME_ZONE=America/New_York

# Database (will be auto-configured)
DATABASE_URL=postgresql://postgres:secure-password@db:5432/synergenhr

# Optional: Email configuration
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
```

### 3.3 Run the Deployment
```bash
# Make deployment script executable
chmod +x deployment/deploy.sh

# Run the deployment
./deployment/deploy.sh
```

**The deployment will:**
1. Generate secure passwords and secret keys
2. Build Docker containers
3. Start PostgreSQL database
4. Run Django migrations (create all tables)
5. Create admin user
6. Ask if you want demo data
7. Start the web application

---

## Step 4: Configure Domain and SSL (Optional)

### 4.1 Point Your Domain to Server
In your domain registrar's DNS settings:
```
Type: A Record
Name: @ (or your subdomain)
Value: your-server-ip-address
TTL: 300 (or default)

Type: A Record  
Name: www
Value: your-server-ip-address
TTL: 300 (or default)
```

### 4.2 Update Nginx Configuration
```bash
# Edit nginx configuration
nano deployment/nginx.conf

# Update these lines with your actual domain:
server_name your-actual-domain.com www.your-actual-domain.com;
```

### 4.3 Install SSL Certificate
```bash
# Wait for DNS to propagate (5-30 minutes), then:
sudo certbot --nginx -d your-domain.com -d www.your-domain.com

# Follow the prompts to get free SSL certificate
```

---

## Step 5: Access Your Application

### 5.1 Web Access
- **Without domain**: `http://your-server-ip:8000`
- **With domain**: `https://your-domain.com`

### 5.2 Default Login
- **Username**: `admin`
- **Password**: `admin`
- **⚠️ Change this immediately after first login!**

---

## Step 6: Load Demo Data (Recommended)

### 6.1 Load Demo Data
```bash
# If you didn't load it during deployment:
chmod +x deployment/load_demo_data.sh
./deployment/load_demo_data.sh
```

**Demo data includes:**
- 20+ sample employees with photos
- 3 companies and multiple departments
- Attendance records for past 3 months
- Leave requests and balances
- Payroll data with salary slips
- Recruitment pipeline with candidates
- Asset management examples
- Performance reviews and goals

---

## Step 7: System Management

### 7.1 Common Commands
```bash
# Check if services are running
docker-compose -f docker-compose.prod.yml ps

# View application logs
docker-compose -f docker-compose.prod.yml logs

# Restart services
docker-compose -f docker-compose.prod.yml restart

# Stop services
docker-compose -f docker-compose.prod.yml down

# Start services
docker-compose -f docker-compose.prod.yml up -d

# Update application
git pull origin main
docker-compose -f docker-compose.prod.yml up -d --build
```

### 7.2 Database Management
```bash
# Connect to database
docker-compose -f docker-compose.prod.yml exec db psql -U postgres synergenhr

# Create backup
chmod +x deployment/db_backup.sh
./deployment/db_backup.sh

# View database size
docker-compose -f docker-compose.prod.yml exec db psql -U postgres -c "SELECT pg_size_pretty(pg_database_size('synergenhr'));"
```

### 7.3 System Monitoring
```bash
# Check disk usage
df -h

# Check memory usage
free -h

# Check CPU usage
htop

# Check Docker container stats
docker stats
```

---

## Step 8: Security and Maintenance

### 8.1 Security Checklist
- [ ] Change default admin password
- [ ] Update all environment variables
- [ ] Configure firewall (UFW enabled by setup script)
- [ ] Set up SSL certificates
- [ ] Regular system updates
- [ ] Monitor application logs

### 8.2 Regular Maintenance
```bash
# Weekly system updates
sudo apt update && sudo apt upgrade -y

# Monthly Docker cleanup
docker system prune -f

# Weekly database backup
./deployment/db_backup.sh

# Check application health
curl -f http://localhost:8000/health/ || echo "Application down"
```

---

## Step 9: Troubleshooting

### 9.1 Common Issues

**Services won't start:**
```bash
# Check logs
docker-compose -f docker-compose.prod.yml logs

# Check disk space
df -h

# Restart services
docker-compose -f docker-compose.prod.yml restart
```

**Database connection issues:**
```bash
# Check database status
docker-compose -f docker-compose.prod.yml exec db pg_isready -U postgres

# Restart database
docker-compose -f docker-compose.prod.yml restart db
```

**SSL certificate issues:**
```bash
# Check certificate status
sudo certbot certificates

# Renew certificates
sudo certbot renew

# Test renewal
sudo certbot renew --dry-run
```

### 9.2 Performance Optimization

**For high traffic:**
```bash
# Increase worker processes in docker-compose.prod.yml
# Add Redis for caching
# Set up database connection pooling
# Configure CDN for static files
```

---

## Step 10: Backup and Recovery

### 10.1 Automated Backups
```bash
# Set up daily backups with cron
crontab -e

# Add this line for daily 2 AM backups:
0 2 * * * /opt/synergenhr/deployment/db_backup.sh
```

### 10.2 Full System Backup
```bash
# Backup entire application
tar -czf synergenhr-backup-$(date +%Y%m%d).tar.gz /opt/synergenhr

# Backup database
./deployment/db_backup.sh

# Store backups off-server (recommended)
```

---

## Complete Deployment Summary

### What Gets Installed
1. **Docker containers** running:
   - SynergenHR Django application
   - PostgreSQL database
   - Nginx reverse proxy

2. **Database** with:
   - 200+ tables for all HR functions
   - Demo data (optional)
   - Proper indexes and relationships

3. **Web server** with:
   - SSL certificate support
   - Static file serving
   - Reverse proxy configuration

### File Structure
```
/opt/synergenhr/
├── deployment/          # Deployment scripts
├── employee/           # Employee management
├── payroll/           # Payroll system
├── attendance/        # Attendance tracking
├── leave/            # Leave management
├── recruitment/      # Recruitment pipeline
├── asset/           # Asset management
├── pms/             # Performance management
├── static/          # Static files (CSS, JS, images)
├── media/           # Uploaded files
├── load_data/       # Demo data files
├── docker-compose.prod.yml  # Production configuration
└── .env.production  # Environment variables
```

### Ports and Services
- **Port 80**: HTTP (redirects to HTTPS)
- **Port 443**: HTTPS (main application)
- **Port 8000**: Direct application access
- **Port 5432**: PostgreSQL (internal only)

### Resource Usage
- **RAM**: ~2GB for full system
- **Storage**: ~5GB for application + database
- **CPU**: Minimal for small teams (<100 employees)

---

## Next Steps After Deployment

1. **Change admin password**
2. **Add your company information**
3. **Configure email settings**
4. **Add real employees** (or keep demo data for testing)
5. **Set up regular backups**
6. **Train users** on the system
7. **Customize** leave policies, salary structures, etc.

Your SynergenHR system is now fully deployed and ready for production use!