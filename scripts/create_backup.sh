#!/bin/bash

################################################################################
# create_backup.sh
#
# This script creates a full backup by first syncing files and then exporting 
# the associated Docker volume as a compressed archive.
################################################################################

# -------------------------------
# Configuration
# -------------------------------

BACKUP_DIR="" # <- set target backup directory
VERBOSE=1

SYNC_SERVICE="storage_sync"
VOLUME_NAME="minecraft-server_storage"

PROJECT_DIR="$(dirname "$(dirname "$(realpath "$0")")")"
TIMESTAMP=$(date +"%Y%m%d%H%M%S")
BACKUP="$BACKUP_DIR/backup_$TIMESTAMP.tar.gz"


# -------------------------------
# Functions
# -------------------------------

log() {
    if [ "$VERBOSE" -eq 1 ]; then
        echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1"
    fi
}


# -------------------------------
# Pre-flight Checks
# -------------------------------

echo "* Welcome :) - Starting pre-flight checks..."

# Check for Docker
if ! command -v docker &> /dev/null; then
    echo "[ERROR] Docker is not installed or not in PATH."
    exit 1
fi

# Check for valid backup directory
if [ ! -d "$BACKUP_DIR" ]; then
    echo "[ERROR] Backup directory '$BACKUP_DIR' does not exist. Aborting."
    exit 1
fi

# Check if service is already running
docker compose --project-directory "$PROJECT_DIR" ps --services --filter "status=running" \
    | grep -q "^$SYNC_SERVICE$"
SERVICE_RUNNING=$?

echo "* Pre-flight checks passed."


# -------------------------------
# Sync & Backup
# -------------------------------

if [ $SERVICE_RUNNING -ne 0 ]; then
    echo ""
    log "Starting sync service: $SYNC_SERVICE..."
    docker compose --project-directory "$PROJECT_DIR" up -d "$SYNC_SERVICE" > /dev/null 2>&1
    
    log "Waiting for sync completion log..."
    CONTAINER_ID=$(docker compose --project-directory "$PROJECT_DIR" ps -q "$SYNC_SERVICE")
    docker logs -f "$CONTAINER_ID" 2>&1 | grep -m 1 "✅ Sync with OCI bucket completed."
    
    if [ $? -eq 0 ]; then
        log "Sync completed successfully."
    else
        echo "[ERROR] Sync log message not detected. Timeout or failure occurred."
        exit 1
    fi

    log "Stopping sync service..."
    docker compose --project-directory "$PROJECT_DIR" stop "$SYNC_SERVICE" > /dev/null 2>&1
else
    log "Sync service already running - skipping startup."
fi

echo ""
echo "Creating backup ($VOLUME_NAME -> $BACKUP)"
docker run --rm \
    -v "${VOLUME_NAME}:/data" \
    -v "${BACKUP_DIR}:/backup" \
    alpine \
    sh -c "cd /data && tar czf /backup/$(basename "$BACKUP") ." > /dev/null 2>&1

if [ $? -eq 0 ]; then
    echo "Backup created!"
else
    echo "[ERROR] Backup process failed."
    exit 1
fi

# ##############################################################################
# ################################ END OF FILE #################################