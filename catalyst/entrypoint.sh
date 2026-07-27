#!/bin/bash
set -e

export PATH="/usr/lib/postgresql/16/bin:$PATH"

PORT="${X_ZOHO_CATALYST_LISTEN_PORT:-9000}"
echo "=== IntelliCon Catalyst Entrypoint ==="
echo "Listening on port: $PORT"

# ─── Ensure localhost resolves (Catalyst may lack /etc/hosts entry) ───
grep -q '127.0.0.1.*localhost' /etc/hosts 2>/dev/null || echo '127.0.0.1 localhost' >> /etc/hosts || true

# ─── Set database credentials from env ───
export POSTGRES_DB="${POSTGRES_DB:-intellicon}"
export POSTGRES_USER="${POSTGRES_USER:-intellicon}"
export POSTGRES_PASSWORD="${POSTGRES_PASSWORD:-intellicon}"
export NEO4J_USER="${NEO4J_USER:-neo4j}"
export NEO4J_PASSWORD="${NEO4J_PASSWORD:-intellicon}"
export REDIS_PASSWORD="${REDIS_PASSWORD:-intellicon}"
export ENVIRONMENT="${ENVIRONMENT:-development}"

# ─── Initialize PostgreSQL if needed ───
PGDATA="/var/lib/postgresql/data"
if [ ! -s "$PGDATA/PG_VERSION" ]; then
    echo "Initializing PostgreSQL..."
    rm -rf "$PGDATA"
    mkdir -p "$PGDATA"
    mkdir -p /var/run/postgresql
    chown postgres:postgres "$PGDATA" /var/run/postgresql
    gosu postgres initdb -D "$PGDATA"

    # Catalyst may not resolve "localhost" — bind PG to 127.0.0.1 explicitly
    sed -i "s/#listen_addresses = 'localhost'/listen_addresses = '127.0.0.1'/" "$PGDATA/postgresql.conf"

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

# ─── Write Caddyfile — routes API + analytics only (frontend is on Slate) ───
cat > /etc/caddy/Caddyfile <<CADDYEOF
:$PORT {
    header {
        Strict-Transport-Security "max-age=31536000; includeSubDomains"
        X-Frame-Options "SAMEORIGIN"
        X-Content-Type-Options "nosniff"
        X-XSS-Protection "1; mode=block"
        Referrer-Policy "strict-origin-when-cross-origin"
        -Server
    }

    handle /analytics/* {
        reverse_proxy 127.0.0.1:8001
    }

    handle /api/chat/ws {
        reverse_proxy 127.0.0.1:8000 {
            transport http {
                read_timeout 86400s
            }
        }
    }

    handle {
        reverse_proxy 127.0.0.1:8000
    }
}
CADDYEOF

# ─── Validate Caddyfile before starting ───
echo "Validating Caddyfile..."
if caddy validate --config /etc/caddy/Caddyfile --adapter caddyfile 2>&1; then
    echo "Caddyfile OK"
else
    echo "WARNING: Caddyfile validation failed (non-fatal, Caddy may still work)"
fi

# ─── Start all services via supervisord ───
echo "Starting all services..."
/usr/bin/supervisord -c /etc/supervisor/conf.d/supervisord.conf &
SUPERVISORD_PID=$!

# ─── Wait and collect diagnostics ───
echo "Waiting 30s for services to initialise..."
sleep 30

echo ""
echo "========== DIAGNOSTIC SNAPSHOT =========="
echo "--- Supervisord status ---"
supervisorctl -c /etc/supervisor/conf.d/supervisord.conf status 2>&1 || true

echo ""
echo "--- Ports in use ---"
ss -tlnp 2>/dev/null || netstat -tlnp 2>/dev/null || true

echo ""
echo "--- Backend health ---"
curl -sf http://127.0.0.1:8000/health 2>&1 || echo "Backend NOT responding on :8000"

echo ""
echo "--- Backend log (last 80 lines) ---"
tail -80 /var/log/supervisor/backend.log 2>/dev/null || echo "No backend.log"

echo ""
echo "--- Backend errors (last 80 lines) ---"
tail -80 /var/log/supervisor/backend-err.log 2>/dev/null || echo "No backend-err.log"

echo ""
echo "--- Caddy log (last 30 lines) ---"
tail -30 /var/log/supervisor/caddy.log 2>/dev/null || echo "No caddy.log"

echo ""
echo "--- Caddy errors (last 30 lines) ---"
tail -30 /var/log/supervisor/caddy-err.log 2>/dev/null || echo "No caddy-err.log"

echo ""
echo "--- Neo4j errors (last 30 lines) ---"
tail -30 /var/log/supervisor/neo4j-err.log 2>/dev/null || echo "No neo4j-err.log"

echo ""
echo "--- PostgreSQL log (last 20 lines) ---"
tail -20 /var/log/supervisor/postgres.log 2>/dev/null || echo "No postgres.log"

echo "========== END DIAGNOSTIC =========="
echo ""

# ─── Keep container alive, forwarding supervisord ───
wait $SUPERVISORD_PID
