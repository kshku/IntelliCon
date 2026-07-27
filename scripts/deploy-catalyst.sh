#!/bin/bash
set -euo pipefail

# ═══════════════════════════════════════════════════════
# IntelliCon Catalyst Deployment Script
# Builds all-in-one Docker image, pushes to Docker Hub,
# deploys to Zoho Catalyst AppSail
# ═══════════════════════════════════════════════════════

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
ROOT_DIR="$(dirname "$SCRIPT_DIR")"

# Load env
if [ -f "$ROOT_DIR/.env.catalyst" ]; then
    set -a
    source "$ROOT_DIR/.env.catalyst"
    set +a
else
    echo "ERROR: .env.catalyst not found."
    echo "Copy .env.catalyst.example to .env.catalyst and fill in your values."
    exit 1
fi

DOCKER_IMAGE="${DOCKER_IMAGE:-intellicon/catalyst}"
DOCKER_TAG="${DOCKER_TAG:-latest}"
CATALYST_PORT="${X_ZOHO_CATALYST_LISTEN_PORT:-9000}"

echo "╔══════════════════════════════════════════════════╗"
echo "║   IntelliCon Catalyst Deployment                ║"
echo "╠══════════════════════════════════════════════════╣"
echo "║  Image:  ${DOCKER_IMAGE}:${DOCKER_TAG}"
echo "║  Port:   ${CATALYST_PORT}"
echo "║  Slate:  ${SLATE_URL:-NOT SET}"
echo "╚══════════════════════════════════════════════════╝"
echo ""

# ─── Step 1: Build the all-in-one Docker image ───
echo "▶ Step 1/4: Building Docker image (linux/amd64)..."
cd "$ROOT_DIR"
docker build \
    --platform linux/amd64 \
    -f Dockerfile.catalyst \
    -t "${DOCKER_IMAGE}:${DOCKER_TAG}" \
    .

echo "✓ Image built: ${DOCKER_IMAGE}:${DOCKER_TAG}"
echo ""

# ─── Step 2: Quick local smoke test ───
echo "▶ Step 2/4: Quick local smoke test..."
docker run --rm -d \
    --name intellicon-test \
    -p 9000:9000 \
    -e POSTGRES_PASSWORD=test123 \
    -e NEO4J_PASSWORD=test123 \
    -e REDIS_PASSWORD=test123 \
    -e JWT_SECRET_KEY=test-secret-key-that-is-long-enough-32chars \
    -e LLM_API_KEY=test \
    "${DOCKER_IMAGE}:${DOCKER_TAG}" || true

sleep 8

if docker ps | grep -q intellicon-test; then
    echo "✓ Container is running."
    docker stop intellicon-test >/dev/null 2>&1 || true
else
    echo "⚠ Container didn't start. Check: docker logs intellicon-test"
    exit 1
fi
echo ""

# ─── Step 3: Push to Docker Hub ───
echo "▶ Step 3/4: Pushing to Docker Hub..."
docker push "${DOCKER_IMAGE}:${DOCKER_TAG}"
echo "✓ Pushed: ${DOCKER_IMAGE}:${DOCKER_TAG}"
echo ""

# ─── Step 4: Catalyst deployment instructions ───
echo "▶ Step 4/4: Catalyst deployment instructions"
echo ""
echo "  1. Go to https://console.catalyst.zoho.com"
echo "  2. Select your project"
echo "  3. Navigate to Serverless → AppSail"
echo "  4. Click 'Create Service' → 'Custom Runtime' → 'Docker Image'"
echo "  5. Connect Docker Hub:"
echo "     - Image: ${DOCKER_IMAGE}:${DOCKER_TAG}"
echo "  6. Configure:"
echo "     - Service Name: intellicon"
echo "     - Port: ${CATALYST_PORT}"
echo "     - Memory: 2048 MB"
echo "     - Disk: 5120 MB"
echo "  7. Add environment variables:"
echo "     ENVIRONMENT=production"
echo "     POSTGRES_DB=${POSTGRES_DB}"
echo "     POSTGRES_USER=${POSTGRES_USER}"
echo "     POSTGRES_PASSWORD=***"
echo "     NEO4J_USER=${NEO4J_USER}"
echo "     NEO4J_PASSWORD=***"
echo "     REDIS_PASSWORD=***"
echo "     JWT_SECRET_KEY=***"
echo "     LLM_PROVIDER=${LLM_PROVIDER}"
echo "     LLM_MODEL=${LLM_MODEL}"
echo "     LLM_API_KEY=***"
echo "     CORS_ORIGINS=${SLATE_URL}"
echo "     SEED_ADMIN_PASSWORD=***"
echo "     SEED_INVESTIGATOR_PASSWORD=***"
echo "     SEED_SUPERVISOR_PASSWORD=***"
echo "  8. Click 'Deploy'"
echo ""
echo "  After deployment, verify at:"
echo "  https://intellicon-<YOUR-ZAID>.development.catalystappsail.com/health"
echo ""
echo "  Then update your Slate frontend's VITE_API_URL to:"
echo "  https://intellicon-<YOUR-ZAID>.development.catalystappsail.com"
echo ""
echo "╔══════════════════════════════════════════════════╗"
echo "║  Deployment complete!                            ║"
echo "╚══════════════════════════════════════════════════╝"
