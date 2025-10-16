#!/bin/bash
# Remove old CSV logs to preserve space on the Raspberry Pi.

set -euo pipefail

RETENTION_DAYS=${RETENTION_DAYS:-14}
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

find "$PROJECT_DIR/batch_logs" -type f -name "*.csv" -mtime +"$RETENTION_DAYS" -delete
find "$PROJECT_DIR/Batch_Setup_Logs" -type f -name "*.csv" -mtime +"$RETENTION_DAYS" -delete
