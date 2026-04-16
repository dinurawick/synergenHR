#!/bin/bash
# Run on server as root: bash deploy_pibt.sh
# Sets up pibt.synergenhr.lk as a third SynergenHR instance

set -e

PIBT_DIR=/opt/synergenhr-pibt
REPO_URL="https://github.com/dinurawick/synergenHR.git"

echo "=== [1/6] Clone repo ==="
if [ ! -d "$PIBT_DIR" ]; then
    git clone "$REPO_URL" "$PIBT_DIR"
else
    echo "Directory exists, pulling latest..."
    cd "$PIBT_DIR" && git pull origin main
fi

echo ""
echo "=== [2/6] Set up env file ==="
if [ ! -f "$PIBT_DIR/.env.production" ]; then
    cat > "$PIBT_DIR/.env.production" << 'EOF'
DEBUG=False
SECRET_KEY=REPLACE_WITH_NEW_SECRET_KEY
ALLOWED_HOSTS=pibt.synergenhr.lk
CSRF_TRUSTED_ORIGINS=https://pibt.synergenhr.lk
TIME_ZONE=Asia/Colombo
DB_PASSWORD=REPLACE_WITH_STRONG_PASSWORD
EOF
    echo ""
    echo ">>> Edit the env file: nano $PIBT_DIR/.env.production"
    echo ">>> Set SECRET_KEY (from https://djecrety.ir) and DB_PASSWORD"
    echo ">>> Then re-run this script"
    exit 0
fi

echo ""
echo "=== [3/6] Copy docker-compose and build ==="
cp "$PIBT_DIR/deployment/docker-compose.pibt.yml" "$PIBT_DIR/docker-compose.prod.yml"
cd "$PIBT_DIR"
export $(grep -v '^#' .env.production | xargs -d '\n')
docker compose -f docker-compose.prod.yml up -d --build

echo ""
echo "=== [4/6] Issue SSL cert for pibt.synergenhr.lk ==="
certbot certonly --standalone \
    --non-interactive \
    --agree-tos \
    --email admin@synergenhr.lk \
    -d pibt.synergenhr.lk \
    --pre-hook "systemctl stop nginx" \
    --post-hook "systemctl start nginx"

echo ""
echo "=== [5/6] Install nginx config ==="
cp "$PIBT_DIR/deployment/pibt.synergenhr.lk.conf" /etc/nginx/conf.d/pibt.synergenhr.lk.conf
nginx -t && systemctl reload nginx

echo ""
echo "=== [6/6] Done ==="
echo "pibt.synergenhr.lk is live at https://pibt.synergenhr.lk"
echo ""
echo "Container status:"
docker ps | grep synergenhr-pibt
