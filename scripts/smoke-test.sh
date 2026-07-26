#!/usr/bin/env bash
# Smoke test: builds and starts the full Compose stack, verifies health,
# exercises an authenticated workflow, and cleans up.
#
# Usage: ./scripts/smoke-test.sh
# Env vars: SMOKE_TEST_TIMEOUT (default: 120)

set -euo pipefail

# Ensure required variables are set so the base compose file's ${VAR:?} assertions don't fail.
# Docker Compose interpolates each file's variables before merging overrides,
# so these must be in the shell environment even though the test overlay sets them.
export POSTGRES_PASSWORD=testpass
export NEO4J_PASSWORD=testpass
export REDIS_PASSWORD=testpass

# Create a minimal .env so the base compose file's env_file references don't fail.
# The test overlay disables env_file, but Compose validates the path before merging.
touch .env

COMPOSE_FILES="-f docker-compose.yml -f docker-compose.test.yml"
TIMEOUT="${SMOKE_TEST_TIMEOUT:-180}"
BACKEND_URL="http://localhost:8000"
ANALYTICS_URL="http://localhost:8001"
CADDY_URL="http://localhost:80"

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

# --- Step 3: Wait for backend health ---
echo "==> Waiting for backend to become healthy (timeout: ${TIMEOUT}s)..."
SECONDS=0
while true; do
  if [ $SECONDS -ge $TIMEOUT ]; then
    echo "FAIL: Backend not healthy after ${TIMEOUT}s."
    echo "==> Current service status:"
    docker compose $COMPOSE_FILES ps
    echo "==> Recent logs:"
    docker compose $COMPOSE_FILES logs --tail=50
    exit 1
  fi

  BACKEND_STATUS=$(curl -sf "$BACKEND_URL/health" 2>/dev/null \
    | python3 -c "import sys,json; print(json.load(sys.stdin).get('status',''))" 2>/dev/null || echo "")
  if [ "$BACKEND_STATUS" = "healthy" ]; then
    echo "==> Backend healthy after ${SECONDS}s."
    break
  fi

  sleep 5
done

# --- Step 4: Seed default users ---
echo "==> Seeding default users..."
docker compose $COMPOSE_FILES exec -T backend python -m app.db.seed || {
  echo "WARN: Seed script failed (users may already exist or seed data present)."
}

# --- Step 5: Auth workflow (the smoke test) ---
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

# --- Step 6: Bonus probes (non-blocking) ---
echo "==> Probing services (informational, non-blocking)..."

BACKEND_HEALTH=$(curl -sf "$BACKEND_URL/health" 2>/dev/null) && \
  echo "$BACKEND_HEALTH" | python3 -c "
import sys, json
data = json.load(sys.stdin)
assert data.get('database_revision'), 'database_revision missing'
print(f\"  Backend: status={data['status']}, revision={data['database_revision']}\")
" 2>/dev/null || echo "  Backend: (probe skipped)"

curl -sf "$ANALYTICS_URL/health" 2>/dev/null \
  | python3 -c "import sys,json; d=json.load(sys.stdin); print(f\"  Analytics: status={d['status']}\")" 2>/dev/null \
  || echo "  Analytics: (not reachable — non-blocking)"

curl -sf "$CADDY_URL/" >/dev/null 2>&1 \
  && echo "  Frontend via Caddy: reachable" \
  || echo "  Frontend via Caddy: (not reachable — non-blocking)"

echo ""
echo "========================================="
echo "  SMOKE TEST PASSED"
echo "========================================="
