#!/usr/bin/env bash
set -e

# ============================================================
#              CONFIGURATION (EDIT THESE ONLY)
# ============================================================
SERVICE_PREFIX="flood_simulator_dev"
COMPOSE_FILE="docker-compose.yml"
PORT="${PORT:-8501}"

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

# ============================================================
#                     HELPERS
# ============================================================
check_docker() {
  if ! command -v docker &>/dev/null; then
    echo "ERROR: Docker is not installed or not on PATH."
    echo "  Install Docker Desktop: https://www.docker.com/products/docker-desktop/"
    exit 1
  fi
  if ! docker info &>/dev/null 2>&1; then
    echo "ERROR: Docker daemon is not running. Please start Docker Desktop."
    exit 1
  fi
}

remove_images() {
  echo ""
  echo "Searching for images starting with \"$SERVICE_PREFIX\"..."
  FOUND=0
  for IMAGE in $(docker images --format "{{.Repository}}:{{.Tag}}" | grep -i "^${SERVICE_PREFIX}"); do
      echo "Found image: $IMAGE"
      echo "Removing image $IMAGE..."
      docker rmi -f "$IMAGE" 2>/dev/null || true
      FOUND=1
  done
  if [[ $FOUND -eq 0 ]]; then
      echo "No images found matching prefix \"$SERVICE_PREFIX\"."
  fi
}

# ============================================================
#                  PARSE ARGUMENTS
# ============================================================
for arg in "$@"; do
  case "$arg" in
    --help|-h)
      echo "Usage: $0 [OPTIONS]"
      echo ""
      echo "Options:"
      echo "  -h, --help      Show this help"
      echo ""
      echo "Environment:"
      echo "  PORT              Server port (default: 8501)"
      exit 0
      ;;
  esac
done

# ============================================================
#                     RUN DOCKER COMPOSE
# ============================================================
check_docker

echo "==> Starting FAC14 - Flood-Adjusted Carbon-14 Simulator..."
PORT="$PORT" docker compose -f "$COMPOSE_FILE" up --build -d

echo ""
echo "=============================="
echo "FAC14 running at http://localhost:$PORT"
echo ""
echo "Press k + Enter = stop but keep image"
echo "Press q + Enter = stop & remove image"
echo "Press r + Enter = full reset & restart (rebuild from scratch)"
echo "=============================="

# Auto-open browser
if command -v open &>/dev/null; then
  sleep 2
  open "http://localhost:$PORT"
elif command -v xdg-open &>/dev/null; then
  sleep 2
  xdg-open "http://localhost:$PORT"
fi

while true; do
    read -rp "Enter selection (k/q/r): " CHOICE
    CHOICE=$(printf '%s' "$CHOICE" | tr '[:upper:]' '[:lower:]')
    case "$CHOICE" in
        k)
            echo ""
            echo "Stopping containers but keeping images..."
            docker compose -f "$COMPOSE_FILE" down
            exit 0
            ;;
        q)
            echo ""
            echo "Stopping and removing all containers..."
            docker compose -f "$COMPOSE_FILE" down --remove-orphans
            remove_images
            exit 0
            ;;
        r)
            echo ""
            echo "==> Full reset & restart..."

            docker compose -f "$COMPOSE_FILE" down --volumes --remove-orphans
            remove_images

            echo "==> Rebuilding Docker image..."
            PORT="$PORT" docker compose -f "$COMPOSE_FILE" up --build -d

            echo ""
            echo "=============================="
            echo "FAC14 restarted at http://localhost:$PORT"
            echo ""
            echo "Press k + Enter = stop but keep image"
            echo "Press q + Enter = stop & remove image"
            echo "Press r + Enter = full reset & restart (rebuild from scratch)"
            echo "=============================="

            if command -v open &>/dev/null; then
              sleep 2
              open "http://localhost:$PORT"
            elif command -v xdg-open &>/dev/null; then
              sleep 2
              xdg-open "http://localhost:$PORT"
            fi
            ;;
        *) echo "Invalid selection. Enter k, q, or r." ;;
    esac
done
