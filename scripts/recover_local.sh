set -euo pipefail

STORAGE_VOLUME_NAME="minecraft-server_storage"
CONTAINER_TARGET="/var/lib/pufferpanel"
LOCAL_ZIP="${1:-}"

usage() {
    echo "Usage: $0 /path/to/backup.zip"
    exit 1
}

# Check if the backup ZIP file argument is provided and exists
if [[ -z "$LOCAL_ZIP" || ! -f "$LOCAL_ZIP" ]]; then
    usage
fi

echo "Starting recover from '$LOCAL_ZIP' into volume '$STORAGE_VOLUME_NAME'..."

docker run --rm \
    -v "${STORAGE_VOLUME_NAME}:${CONTAINER_TARGET}" \
    -v "$(realpath "$LOCAL_ZIP"):/import.zip:ro" \
    alpine:3.19 \
    /bin/sh -c "
        set -euxo pipefail

        echo 'Clearing existing contents in ${CONTAINER_TARGET}...'
        rm -rf ${CONTAINER_TARGET:?}/*

        echo 'Copying backup archive...'
        cp /import.zip ${CONTAINER_TARGET}/

        echo 'Extracting backup archive...'
        cd ${CONTAINER_TARGET}
        unzip -o -q import.zip

        echo 'Removing backup archive...'
        rm import.zip

        echo 'Creating recovery marker...'
        touch .recoverfile

        echo 'Recovery completed successfully.'
    "

echo "Done! Volume '$STORAGE_VOLUME_NAME' has been reset to the backup."