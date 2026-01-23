#!/bin/bash

# EUK Cloud Server Setup Script for SynergenHR

echo "🚀 Setting up EUK Cloud server for SynergenHR deployment..."

# Update system packages
echo "📦 Updating system packages..."
sudo apt update && sudo apt upgrade -y

# Install essential packages
echo "🔧 Installing essential packages..."
sudo apt install -y curl wget git unzip software-properties-common apt-transport-https ca-certificates gnupg lsb-release

# Install Docker
echo "🐳 Installing Docker..."
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin

# Install Docker Compose (standalone)
echo "🔗 Installing Docker Compose..."
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Add current user to docker group
echo "👤 Adding user to docker group..."
sudo usermod -aG docker $USER

# Start and enable Docker
echo "▶️ Starting Docker service..."
sudo systemctl start docker
sudo systemctl enable docker

# Install Python and pip (for Django management commands)
echo "🐍 Installing Python..."
sudo apt install -y python3 python3-pip python3-venv

# Create application directory
echo "📁 Creating application directory..."
sudo mkdir -p /opt/synergenhr
sudo chown $USER:$USER /opt/synergenhr

# Install Nginx (for reverse proxy)
echo "🌐 Installing Nginx..."
sudo apt install -y nginx

# Install certbot for SSL certificates
echo "🔒 Installing Certbot for SSL..."
sudo apt install -y certbot python3-certbot-nginx

# Configure firewall
echo "🔥 Configuring firewall..."
sudo ufw allow OpenSSH
sudo ufw allow 'Nginx Full'
sudo ufw allow 80
sudo ufw allow 443
sudo ufw --force enable

echo "✅ Server setup completed!"
echo ""
echo "📋 Next steps:"
echo "1. Log out and log back in (or run: newgrp docker)"
echo "2. Clone your SynergenHR repository"
echo "3. Run the deployment script"
echo ""
echo "🔄 Please run: newgrp docker"
echo "   Or logout and login again to apply docker group changes"