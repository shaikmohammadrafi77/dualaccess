#!/bin/bash
set -euxo pipefail

# Log userdata output for troubleshooting
exec > >(tee /var/log/user-data.log | logger -t user-data -s 2>/dev/console) 2>&1

APP_NAME="dualaccess"
APP_DIR="/opt/${APP_NAME}"
APP_USER="ec2-user"
APP_GROUP="ec2-user"
REPO_URL="https://github.com/shaikmohammadrafi77/dualaccess.git"
PYTHON_BIN="/usr/bin/python3"
VENV_DIR="${APP_DIR}/venv"
ENV_FILE="/etc/${APP_NAME}.env"
SERVICE_FILE="/etc/systemd/system/${APP_NAME}.service"

dnf update -y
dnf install -y git python3 python3-pip

if [ ! -d "${APP_DIR}/.git" ]; then
  su -s /bin/bash "${APP_USER}" -c "git clone '${REPO_URL}' '${APP_DIR}'"
else
  su -s /bin/bash "${APP_USER}" -c "git -C '${APP_DIR}' pull --ff-only"
fi

chown -R "${APP_USER}:${APP_GROUP}" "${APP_DIR}"

${PYTHON_BIN} -m venv "${VENV_DIR}"
"${VENV_DIR}/bin/pip" install --upgrade pip wheel
"${VENV_DIR}/bin/pip" install -r "${APP_DIR}/requirements.txt" gunicorn

SECRET_KEY="$(${PYTHON_BIN} - <<'PY'
import secrets
print(secrets.token_urlsafe(48))
PY
)"
export SECRET_KEY

cat > "${ENV_FILE}" <<EOF
SECRET_KEY=${SECRET_KEY}
EOF

chmod 600 "${ENV_FILE}"

mkdir -p "${APP_DIR}/uploads"
chown -R "${APP_USER}:${APP_GROUP}" "${APP_DIR}/uploads"

cd "${APP_DIR}"
"${VENV_DIR}/bin/python" init_db.py
chown "${APP_USER}:${APP_GROUP}" "${APP_DIR}/dual_access_cloud.db"

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
ExecStart=${VENV_DIR}/bin/gunicorn --workers 3 --bind 0.0.0.0:80 --timeout 120 app:app
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable --now "${APP_NAME}.service"
