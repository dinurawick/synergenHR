#!/bin/bash
# Usage:
#   bash update.sh gf      → updates gf.synergenhr.lk
#   bash update.sh main    → updates app.synergenhr.lk
#   bash update.sh pibt    → updates pibt.synergenhr.lk
#   bash update.sh all     → updates all instances

set -e

update_instance() {
    local name=$1
    local dir=$2
    local compose=$3

    echo "=== Updating $name ==="
    cd "$dir"
    git pull origin main
    export $(grep -v '^#' .env.production | xargs -d '\n')
    docker compose -f "$compose" up -d --build
    echo "=== $name updated ==="
}

case "$1" in
    gf)
        update_instance "gf.synergenhr.lk" /opt/synergenhr-gf docker-compose.prod.yml
        ;;
    main)
        update_instance "app.synergenhr.lk" /opt/synergenhr docker-compose.prod.yml
        ;;
    pibt)
        update_instance "pibt.synergenhr.lk" /opt/synergenhr-pibt docker-compose.prod.yml
        ;;
    all)
        update_instance "app.synergenhr.lk" /opt/synergenhr docker-compose.prod.yml
        update_instance "gf.synergenhr.lk" /opt/synergenhr-gf docker-compose.prod.yml
        update_instance "pibt.synergenhr.lk" /opt/synergenhr-pibt docker-compose.prod.yml
        ;;
    *)
        echo "Usage: bash update.sh [gf|main|pibt|all]"
        exit 1
        ;;
esac

echo ""
echo "Done. Running containers:"
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
