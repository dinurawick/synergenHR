#!/bin/bash
# Run on server as root: bash deploy_gf.sh
# Sets up gf.synergenhr.lk as a second SynergenHR instance

set -e

GF_DIR=/opt/synergenhr-gf
REPO_URL="https://github.com/dinurawick/synergenHR.git"

echo "=== [1/6] Clone repo ==="
if [ ! -d "$GF_DIR" ]; then
    git clone "$REPO_URL" "$GF_DIR"
else
    echo "Directory exists, pulling latest..."
    cd "$GF_DIR" && git pull origin main
fi

echo ""
echo "=== [2/6] Set up env file ==="
if [ ! -f "$GF_DIR/.env.production" ]; then
    cat > "$GF_DIR/.env.production" <<EOF
DEBUG=False
SECRET_KEY=REPLACE_WITH_NEW_SECRET_KEY
ALLOWED_HOSTS=gf.synergenhr.lk
CSRF_TRUSTED_ORIGINS=https://gf.synergenhr.lk
TIME_ZONE=Asia/Colombo
DB_PASSWORD=REPLACE_WITH_STRONG_PASSWORD
EOF
    echo ""
    echo ">>> .env.production created at $GF_DIR/.env.production"
    echo ">>> Edit it now: nano $GF_DIR/.env.production"
    echo ">>> Then re-run this script"
    exit 0
fi

echo ""
echo "=== [3/6] Copy docker-compose and build ==="
cp "$GF_DIR/deployment/docker-compose.gf.yml" "$GF_DIR/docker-compose.prod.yml"
cd "$GF_DIR"
docker compose -f docker-compose.prod.yml up -d --build

echo ""
echo "=== [4/6] Issue SSL cert for gf.synergenhr.lk ==="
# Temporarily serve HTTP for certbot challenge
certbot certonly --standalone \
    --non-interactive \
    --agree-tos \
    --email admin@synergenhr.lk \
    -d gf.synergenhr.lk \
    --pre-hook "systemctl stop nginx" \
    --post-hook "systemctl start nginx"

echo ""
echo "=== [5/6] Install nginx config ==="
cp "$GF_DIR/deployment/gf.synergenhr.lk.conf" /etc/nginx/conf.d/gf.synergenhr.lk.conf
nginx -t && systemctl reload nginx

echo ""
echo "=== [6/6] Done ==="
echo "gf.synergenhr.lk is live at https://gf.synergenhr.lk"
echo ""
echo "Container status:"
docker ps | grep synergenhr-gf
