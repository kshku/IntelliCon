#!/usr/bin/env bash
# Smoke test: builds and starts the full Compose stack, verifies health,
# exercises an authenticated workflow, and cleans up.
#
# Usage: ./scripts/smoke-test.sh
# Env vars: SMOKE_TEST_TIMEOUT (default: 120)

set -euo pipefail

# Ensure REDIS_PASSWORD is set so the base compose file's ${REDIS_PASSWORD:?} doesn't fail.
export REDIS_PASSWORD=testpass

COMPOSE_FILES="-f docker-compose.yml -f docker-compose.test.yml"
TIMEOUT="${SMOKE_TEST_TIMEOUT:-120}"
BACKEND_URL="http://localhost:8000"
ANALYTICS_URL="http://localhost:8001"

# --- Cleanup trap ---
cleanup() {
  echo "==> Cleaning up containers and volumes..."
  docker compose $COMPOSE_FILES down -v --remove-orphans 2>/dev/null || true
}
trap cleanup EXIT

# --- Step 1: Build ---
echo "==> Building all images..."
docker compose $COMPOSE_FILES build

# --- Step 2: Start ---
echo "==> Starting the full stack..."
docker compose $COMPOSE_FILES up -d

# --- Step 3: Wait for health ---
echo "==> Waiting for all services to become healthy (timeout: ${TIMEOUT}s)..."
SECONDS=0
while true; do
  if [ $SECONDS -ge $TIMEOUT ]; then
    echo "FAIL: Timed out after ${TIMEOUT}s waiting for services."
    echo "==> Current service status:"
    docker compose $COMPOSE_FILES ps
    echo "==> Recent logs:"
    docker compose $COMPOSE_FILES logs --tail=50
    exit 1
  fi

  # Check if all services are healthy
  UNHEALTHY=$(docker compose $COMPOSE_FILES ps --format json 2>/dev/null \
    | python3 -c "
import sys, json
services = [json.loads(line) for line in sys.stdin if line.strip()]
unhealthy = [s['Service'] for s in services if s.get('Health', '') != 'healthy']
print('\n'.join(unhealthy))
" 2>/dev/null || echo "")

  if [ -z "$UNHEALTHY" ]; then
    echo "==> All services healthy after ${SECONDS}s."
    break
  fi

  sleep 5
done

# --- Step 4: Seed default users ---
echo "==> Seeding default users..."
docker compose $COMPOSE_FILES exec -T backend python -m app.db.seed || {
  echo "WARN: Seed script failed (users may already exist or seed data present)."
}

# --- Step 5: Health probes ---
echo "==> Probing backend health..."
BACKEND_HEALTH=$(curl -sf "$BACKEND_URL/health" 2>/dev/null) || {
  echo "FAIL: Backend health endpoint unreachable."
  exit 1
}

echo "$BACKEND_HEALTH" | python3 -c "
import sys, json
data = json.load(sys.stdin)
assert data['status'] == 'healthy', f\"Expected status 'healthy', got '{data['status']}'\"
assert data.get('database_revision'), 'database_revision is empty — migrations may not have run'
print(f\"  Backend: status={data['status']}, revision={data['database_revision']}\")
"

echo "==> Probing analytics health..."
ANALYTICS_HEALTH=$(curl -sf "$ANALYTICS_URL/health" 2>/dev/null) || {
  echo "FAIL: Analytics health endpoint unreachable."
  exit 1
}

echo "$ANALYTICS_HEALTH" | python3 -c "
import sys, json
data = json.load(sys.stdin)
assert data['status'] == 'healthy', f\"Expected status 'healthy', got '{data['status']}'\"
print(f\"  Analytics: status={data['status']}\")
"

# --- Step 6: Auth workflow ---
echo "==> Testing auth workflow (login + /me)..."

LOGIN_RESPONSE=$(curl -sf -X POST "$BACKEND_URL/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}' 2>/dev/null) || {
  echo "FAIL: Login request failed."
  exit 1
}

TOKEN=$(echo "$LOGIN_RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin)['access_token'])")

ME_RESPONSE=$(curl -sf "$BACKEND_URL/auth/me" \
  -H "Authorization: Bearer $TOKEN" 2>/dev/null) || {
  echo "FAIL: /me request failed."
  exit 1
}

echo "$ME_RESPONSE" | python3 -c "
import sys, json
data = json.load(sys.stdin)
assert data['username'] == 'admin', f\"Expected username 'admin', got '{data['username']}'\"
assert data['role'] == 'admin', f\"Expected role 'admin', got '{data['role']}'\"
print(f\"  Auth OK: username={data['username']}, role={data['role']}\")
"

echo ""
echo "========================================="
echo "  SMOKE TEST PASSED"
echo "========================================="
