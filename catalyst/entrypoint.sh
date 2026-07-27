#!/bin/bash
set -e

export PATH="/usr/lib/postgresql/16/bin:$PATH"

PORT="${X_ZOHO_CATALYST_LISTEN_PORT:-9000}"
echo "=== IntelliCon Catalyst Entrypoint ==="
echo "Listening on port: $PORT"

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
        reverse_proxy localhost:8001
    }

    handle /api/chat/ws {
        reverse_proxy localhost:8000 {
            transport http {
                read_timeout 86400s
            }
        }
    }

    handle {
        reverse_proxy localhost:8000
    }
}
CADDYEOF

# ─── Start all services via supervisord ───
echo "Starting all services..."
exec /usr/bin/supervisord -c /etc/supervisor/conf.d/supervisord.conf
