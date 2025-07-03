set -euo pipefail

# Define project root directory (two levels up from this script)
PROJECT_DIR="$(dirname "$(dirname "$(realpath "$0")")")"

# Path to Dockerfile for the backup service
DOCKERFILE="$PROJECT_DIR/services/remote_storage_backups/Dockerfile"

# Define backup name based on current timestamp (YYYYMMDDHHMM)
BACKUP_NAME="backup_$(date +%Y%m%d%H%M)"

# Directory where backups will be saved locally
BACKUP_DIR="/Users/lukas/Downloads"

# Build Docker image quietly and capture the image ID
IMAGE_ID=$(docker build --quiet --file "$DOCKERFILE" "$PROJECT_DIR")

# Run the backup container, mounting backup directory and passing parameters
docker run --rm \
  -v "${BACKUP_DIR}":/app/backups \
  "$IMAGE_ID" \
  -d /app/backups \
  -n "$BACKUP_NAME"

echo "Done! Backup created at: ${BACKUP_DIR}/${BACKUP_NAME}.zip"