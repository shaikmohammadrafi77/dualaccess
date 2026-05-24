#!/bin/bash
set -euo pipefail

APP_NAME="${APP_NAME:-dualaccess}"
APP_DIR="${APP_DIR:-/opt/${APP_NAME}}"
APP_USER="${APP_USER:-ec2-user}"
APP_GROUP="${APP_GROUP:-ec2-user}"
REPO_URL="${REPO_URL:-https://github.com/shaikmohammadrafi77/dualaccess.git}"
APP_BRANCH="${APP_BRANCH:-main}"
APP_PORT="${APP_PORT:-80}"
PYTHON_BIN="${PYTHON_BIN:-/usr/bin/python3}"
VENV_DIR="${APP_DIR}/venv"
ENV_FILE="/etc/${APP_NAME}.env"
SERVICE_FILE="/etc/systemd/system/${APP_NAME}.service"

if [ "${EUID}" -ne 0 ]; then
  echo "Run this script with sudo or as root."
  exit 1
fi

echo "Installing system packages..."
dnf update -y
dnf install -y git python3 python3-pip

echo "Cloning or updating project..."
if [ ! -d "${APP_DIR}/.git" ]; then
  su -s /bin/bash "${APP_USER}" -c "git clone --branch '${APP_BRANCH}' '${REPO_URL}' '${APP_DIR}'"
else
  su -s /bin/bash "${APP_USER}" -c "git -C '${APP_DIR}' fetch origin '${APP_BRANCH}'"
  su -s /bin/bash "${APP_USER}" -c "git -C '${APP_DIR}' checkout '${APP_BRANCH}'"
  su -s /bin/bash "${APP_USER}" -c "git -C '${APP_DIR}' pull --ff-only origin '${APP_BRANCH}'"
fi

chown -R "${APP_USER}:${APP_GROUP}" "${APP_DIR}"

echo "Creating Python virtual environment..."
${PYTHON_BIN} -m venv "${VENV_DIR}"
"${VENV_DIR}/bin/pip" install --upgrade pip wheel
"${VENV_DIR}/bin/pip" install -r "${APP_DIR}/requirements.txt" gunicorn

if [ ! -f "${ENV_FILE}" ]; then
  echo "Creating environment file..."
  SECRET_KEY="$(${PYTHON_BIN} - <<'PY'
import secrets
print(secrets.token_urlsafe(48))
PY
)"

  cat > "${ENV_FILE}" <<EOF
SECRET_KEY=${SECRET_KEY}
EOF

  chmod 600 "${ENV_FILE}"
fi

mkdir -p "${APP_DIR}/uploads"
chown -R "${APP_USER}:${APP_GROUP}" "${APP_DIR}/uploads"

echo "Initializing database..."
cd "${APP_DIR}"
su -s /bin/bash "${APP_USER}" -c "set -a && source '${ENV_FILE}' && set +a && '${VENV_DIR}/bin/python' init_db.py"

if [ -f "${APP_DIR}/dual_access_cloud.db" ]; then
  chown "${APP_USER}:${APP_GROUP}" "${APP_DIR}/dual_access_cloud.db"
fi

echo "Creating systemd service..."
cat > "${SERVICE_FILE}" <<EOF
[Unit]
Description=Dual Access Flask App
After=network.target

[Service]
User=${APP_USER}
Group=${APP_GROUP}
WorkingDirectory=${APP_DIR}
EnvironmentFile=${ENV_FILE}
Environment=PYTHONUNBUFFERED=1
AmbientCapabilities=CAP_NET_BIND_SERVICE
CapabilityBoundingSet=CAP_NET_BIND_SERVICE
ExecStart=${VENV_DIR}/bin/gunicorn --workers 3 --bind 0.0.0.0:${APP_PORT} --timeout 120 app:app
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

echo "Starting application service..."
systemctl daemon-reload
systemctl enable --now "${APP_NAME}.service"
systemctl restart "${APP_NAME}.service"

echo
echo "Hosting completed."
echo "Service name: ${APP_NAME}.service"
echo "Port: ${APP_PORT}"
echo "Status command: sudo systemctl status ${APP_NAME}.service"
echo "Logs command: sudo journalctl -u ${APP_NAME}.service -f"
