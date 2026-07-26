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
fi

DOCKER_IMAGE="${DOCKER_IMAGE:-intellicon/catalyst}"
DOCKER_TAG="${DOCKER_TAG:-latest}"
CATALYST_PORT="${X_ZOHO_CATALYST_LISTEN_PORT:-9000}"

echo "╔══════════════════════════════════════════════════╗"
echo "║   IntelliCon Catalyst Deployment                ║"
echo "╠══════════════════════════════════════════════════╣"
echo "║  Image:  ${DOCKER_IMAGE}:${DOCKER_TAG}"
echo "║  Port:   ${CATALYST_PORT}"
echo "╚══════════════════════════════════════════════════╝"
echo ""

# ─── Step 1: Build the all-in-one Docker image ───
echo "▶ Step 1/5: Building Docker image (linux/amd64)..."
cd "$ROOT_DIR"
docker build \
    --platform linux/amd64 \
    -f Dockerfile.catalyst \
    -t "${DOCKER_IMAGE}:${DOCKER_TAG}" \
    .

echo "✓ Image built: ${DOCKER_IMAGE}:${DOCKER_TAG}"
echo ""

# ─── Step 2: Test the image locally ───
echo "▶ Step 2/5: Quick local test (5 seconds)..."
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
    echo "✓ Container is running. Testing health endpoint..."
    curl -s http://localhost:9000/health || echo "  (health check may take a moment to start)"
    docker stop intellicon-test >/dev/null 2>&1 || true
else
    echo "⚠ Container didn't start. Check logs: docker logs intellicon-test"
fi
echo ""

# ─── Step 3: Push to Docker Hub ───
echo "▶ Step 3/5: Pushing to Docker Hub..."
docker push "${DOCKER_IMAGE}:${DOCKER_TAG}"
echo "✓ Pushed: ${DOCKER_IMAGE}:${DOCKER_TAG}"
echo ""

# ─── Step 4: Deploy to Catalyst via Console ───
echo "▶ Step 4/5: Catalyst deployment instructions"
echo ""
echo "  Since you're deploying via Docker Hub (not CLI), follow these steps:"
echo ""
echo "  1. Go to https://console.catalyst.zoho.com"
echo "  2. Select your project (or create one named 'intellicon')"
echo "  3. Navigate to Serverless → AppSail"
echo "  4. Click 'Create Service'"
echo "  5. Select 'Custom Runtime' → 'Docker Image'"
echo "  6. Connect Docker Hub registry:"
echo "     - Registry: Docker Hub"
echo "     - Image: ${DOCKER_IMAGE}:${DOCKER_TAG}"
echo "  7. Configure:"
echo "     - Service Name: intellicon"
echo "     - Port: ${CATALYST_PORT}"
echo "     - Memory: 2048 MB"
echo "     - Disk: 5120 MB"
echo "  8. Add environment variables (from .env.catalyst):"
echo "     ENVIRONMENT=production"
echo "     POSTGRES_DB=intellicon"
echo "     POSTGRES_USER=intellicon"
echo "     POSTGRES_PASSWORD=<your-password>"
echo "     NEO4J_USER=neo4j"
echo "     NEO4J_PASSWORD=<your-password>"
echo "     REDIS_PASSWORD=<your-password>"
echo "     JWT_SECRET_KEY=<your-32-char-secret>"
echo "     LLM_PROVIDER=openai"
echo "     LLM_MODEL=gpt-4"
echo "     LLM_API_KEY=<your-api-key>"
echo "     CORS_ORIGINS=*"
echo "  9. Click 'Deploy'"
echo ""

# ─── Step 5: Verify ───
echo "▶ Step 5/5: After deployment, verify at:"
echo "  https://intellicon-<YOUR-ZAID>.development.catalystappsail.com/health"
echo ""
echo "╔══════════════════════════════════════════════════╗"
echo "║  Deployment complete! 🎉                        ║"
echo "╚══════════════════════════════════════════════════╝"
