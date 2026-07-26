#!/bin/bash
set -e

PORT="${X_ZOHO_CATALYST_LISTEN_PORT:-9000}"
echo "=== IntelliCon Catalyst Entrypoint ==="
echo "Listening on port: $PORT"

# ─── Set database credentials from env ───
export POSTGRES_DB="${POSTGRES_DB:-intellicon}"
export POSTGRES_USER="${POSTGRES_USER:-intellicon}"
export POSTGRES_PASSWORD="${POSTGRES_PASSWORD:-intellicon}"
export NEO4J_PASSWORD="${NEO4J_PASSWORD:-intellicon}"
export REDIS_PASSWORD="${REDIS_PASSWORD:-intellicon}"

# ─── Initialize PostgreSQL if needed ───
PGDATA="/var/lib/postgresql/data"
if [ ! -s "$PGDATA/PG_VERSION" ]; then
    echo "Initializing PostgreSQL..."
    gosu postgres initdb -D "$PGDATA"
    
    # Start postgres temporarily for user setup
    gosu postgres pg_ctl -D "$PGDATA" -w start
    
    gosu postgres psql -c "CREATE USER $POSTGRES_USER WITH SUPERUSER PASSWORD '$POSTGRES_PASSWORD';"
    gosu postgres psql -c "CREATE DATABASE $POSTGRES_DB OWNER $POSTGRES_USER;"
    
    gosu postgres pg_ctl -D "$PGDATA" -w stop
    echo "PostgreSQL initialized."
fi

# ─── Initialize Neo4j if needed ───
if [ ! -d "/var/lib/neo4j/data/databases" ] || [ ! -f "/var/lib/neo4j/data/databases/neo4j/neostore" ]; then
    echo "Initializing Neo4j..."
    neo4j-admin dbms initial-password "$NEO4J_PASSWORD" 2>/dev/null || true
    echo "Neo4j password set."
fi

# ─── Build frontend if dist is empty ───
if [ ! -f "/app/frontend/dist/index.html" ]; then
    echo "Building frontend..."
    cd /tmp/frontend-build
    npm ci && npm run build
    cp -r dist/* /app/frontend/dist/
    echo "Frontend built."
fi

# ─── Write Caddyfile with correct port ───
cat > /etc/caddy/Caddyfile <<CADDYEOF
:{$PORT} {
    header {
        Strict-Transport-Security "max-age=31536000; includeSubDomains"
        X-Frame-Options "SAMEORIGIN"
        X-Content-Type-Options "nosniff"
        X-XSS-Protection "1; mode=block"
        Referrer-Policy "strict-origin-when-cross-origin"
        -Server
    }

    handle /api/chat/ws {
        reverse_proxy localhost:8000 {
            transport http {
                read_timeout 86400s
            }
        }
    }

    handle /api/* {
        reverse_proxy localhost:8000
    }

    handle /analytics/* {
        reverse_proxy localhost:8001
    }

    handle {
        reverse_proxy localhost:3000
    }
}
CADDYEOF

# ─── Write nginx config for frontend ───
cat > /etc/nginx/conf.d/default.conf <<'NGINXEOF'
server {
    listen 3000;
    root /app/frontend/dist;
    index index.html;

    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;

    location /api/ {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /api/chat/ws {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_read_timeout 86400;
    }

    location / {
        try_files $uri $uri/ /index.html;
    }
}
NGINXEOF

# ─── Start all services via supervisord ───
echo "Starting all services..."
exec /usr/bin/supervisord -c /etc/supervisor/conf.d/supervisord.conf
