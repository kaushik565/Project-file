#!/bin/bash
# Install and enable the systemd service that keeps log_viewer.py running.

set -euo pipefail

SERVICE_NAME="batchlog-viewer.service"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TEMPLATE_PATH="$SCRIPT_DIR/systemd/$SERVICE_NAME"
TARGET_PATH="/etc/systemd/system/$SERVICE_NAME"

SERVICE_USER="${SERVICE_USER:-${1:-pi}}"
SERVICE_GROUP="${SERVICE_GROUP:-$SERVICE_USER}"
PROJECT_DIR="${PROJECT_DIR_OVERRIDE:-$SCRIPT_DIR}"
PYTHON_CMD="${PYTHON_CMD:-python3}"
PYTHON_PACKAGES="${PYTHON_PACKAGES:-flask}"
VENVDIR="$PROJECT_DIR/venv"
VENVPY="$VENVDIR/bin/python"
VENVPIP="$VENVDIR/bin/pip"

if [[ $EUID -ne 0 ]]; then
  echo "Please run this script as root (e.g. sudo $0)." >&2
  exit 1
fi

if ! command -v systemctl >/dev/null 2>&1; then
  echo "systemctl not found on this system; cannot install a systemd service." >&2
  exit 1
fi

if ! id "$SERVICE_USER" >/dev/null 2>&1; then
  echo "System user '$SERVICE_USER' does not exist." >&2
  exit 1
fi

if [[ ! -f "$TEMPLATE_PATH" ]]; then
  echo "Service template not found at $TEMPLATE_PATH" >&2
  exit 1
fi

if ! command -v "$PYTHON_CMD" >/dev/null 2>&1; then
  echo "Python interpreter '$PYTHON_CMD' not found in PATH." >&2
  exit 1
fi
echo "Using Python interpreter: $(command -v "$PYTHON_CMD")"

if [[ ! -x "$VENVPY" ]]; then
  echo "Creating virtualenv at $VENVDIR"
  "$PYTHON_CMD" -m venv "$VENVDIR"
fi

if [[ ! -x "$VENVPIP" ]]; then
  echo "Unable to locate pip inside virtualenv ($VENVDIR)." >&2
  exit 1
fi

echo "Installing Python dependencies into $VENVDIR"
"$VENVPIP" install --upgrade pip
if [[ -n "${PYTHON_PACKAGES// }" ]]; then
  "$VENVPIP" install --upgrade $PYTHON_PACKAGES
fi

chown -R "$SERVICE_USER:$SERVICE_GROUP" "$VENVDIR"

tmpfile="$(mktemp)"
trap 'rm -f "$tmpfile"' EXIT

sed \
  -e "s|__PROJECT_DIR__|$PROJECT_DIR|g" \
  -e "s|__SERVICE_USER__|$SERVICE_USER|g" \
  -e "s|__SERVICE_GROUP__|$SERVICE_GROUP|g" \
  "$TEMPLATE_PATH" >"$tmpfile"

install -m 0644 "$tmpfile" "$TARGET_PATH"

systemctl daemon-reload
systemctl enable --now "$SERVICE_NAME"
systemctl status --no-pager "$SERVICE_NAME"
