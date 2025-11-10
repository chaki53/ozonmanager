#!/bin/bash
set -euo pipefail

LOG_DIR="./logs"; mkdir -p "$LOG_DIR"
LOG_FILE="${LOG_DIR}/install_$(date +%Y%m%d_%H%M%S).log"; : > "$LOG_FILE"
log(){ echo "[$(date +%H:%M:%S)] $*" | tee -a "$LOG_FILE" >/dev/null; }
run(){ log "RUN: $*"; bash -c "$*" >>"$LOG_FILE" 2>&1; }
step(){ echo -e "\n==[ $* ]=="; log "STEP: $*"; }

[ "$(id -u)" -eq 0 ] || { echo "Run as root: sudo ./install.sh"; exit 1; }
[ -f docker-compose.yml ] || { echo "docker-compose.yml not found in $(pwd)"; exit 1; }

# Input
read -r -p "Домен фронтенда (например, example.com): " DOMAIN
read -r -p "E-mail для Let's Encrypt: " LE_EMAIL
API_DOMAIN="api.${DOMAIN}"
read -r -p "NEXT_PUBLIC_API_BASE [https://${API_DOMAIN}]: " API_BASE
API_BASE=${API_BASE:-https://${API_DOMAIN}}

# Base deps
step "Install base packages"
if command -v apt-get >/dev/null 2>&1; then
  run "apt-get update -y"
  run "apt-get install -y ca-certificates curl gnupg lsb-release unzip nginx certbot python3-certbot-nginx"
else
  run "dnf install -y ca-certificates curl gnupg2 unzip nginx certbot python3-certbot-nginx"
fi

# Docker
step "Install Docker & Compose"
if ! command -v docker >/dev/null 2>&1; then
  if command -v apt-get >/dev/null 2>&1; then
    run "install -m 0755 -d /etc/apt/keyrings"
    run "curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor -o /etc/apt/keyrings/docker.gpg"
    run "chmod a+r /etc/apt/keyrings/docker.gpg"
    UB_CODENAME="$(. /etc/os-release 2>/dev/null; echo ${VERSION_CODENAME:-jammy})"
    echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu ${UB_CODENAME} stable" >/etc/apt/sources.list.d/docker.list
    run "apt-get update -y"
    run "apt-get install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin"
  else
    run "dnf -y install dnf-plugins-core"
    run "dnf config-manager --add-repo https://download.docker.com/linux/centos/docker-ce.repo"
    run "dnf install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin"
  fi
  run "systemctl enable --now docker"
fi

# .env updates
step "Configure .env"
[ -f .env ] || cp .env.sample .env 2>/dev/null || touch .env
apply_env(){ k="$1"; v="$2"; grep -qE "^${k}=" .env && sed -i "s|^${k}=.*|${k}=${v}|" .env || echo "${k}=${v}" >> .env; }
apply_env NEXT_PUBLIC_API_BASE "${API_BASE}"

# Nginx
step "Configure Nginx reverse proxies"
SITE_CONF="/etc/nginx/conf.d/ozon-inventory.conf"
mkdir -p /etc/nginx/conf.d
cat > "$SITE_CONF" <<NGX
map \$http_upgrade \$connection_upgrade { default upgrade; '' close; }
limit_req_zone \$binary_remote_addr zone=login_zone:10m rate=10r/m;

server {
  listen 80;
  server_name ${DOMAIN};
  location / {
    proxy_pass http://127.0.0.1:3000;
    proxy_set_header Host \$host;
    proxy_set_header X-Real-IP \$remote_addr;
    proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto \$scheme;
    proxy_http_version 1.1;
    proxy_set_header Upgrade \$http_upgrade;
    proxy_set_header Connection \$connection_upgrade;
  }
}

server {
  listen 80;
  server_name ${API_DOMAIN};
  add_header Referrer-Policy no-referrer always;
  add_header X-Content-Type-Options nosniff always;
  add_header X-Frame-Options DENY always;
  add_header X-XSS-Protection "1; mode=block" always;

  location = /auth/login {
    limit_req zone=login_zone burst=10 nodelay;
    proxy_pass http://127.0.0.1:8000;
    proxy_set_header Host \$host;
    proxy_set_header X-Real-IP \$remote_addr;
    proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto \$scheme;
  }

  location / {
    proxy_pass http://127.0.0.1:8000;
    proxy_set_header Host \$host;
    proxy_set_header X-Real-IP \$remote_addr;
    proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto \$scheme;
    proxy_read_timeout 600s;
  }
}
NGX
nginx -t && systemctl reload nginx

# Certbot
step "Issue certificates via Let's Encrypt"
certbot --nginx -d "${DOMAIN}" -d "${API_DOMAIN}" -m "${LE_EMAIL}" --agree-tos --redirect --non-interactive || true

# Build & run
step "Build and start containers"
docker compose up -d --build

# DB migrate & seed
step "Apply migrations and seed admin"
docker compose exec -T backend alembic upgrade head || true
docker compose exec -T backend python - <<'PY' || true
from app.db.session import SessionLocal
try:
  from app.db.seed import seed_first_admin
  s=SessionLocal(); seed_first_admin(s); s.close()
except Exception as e:
  print(e)
PY

echo
echo "DONE. Frontend: https://${DOMAIN}  API: https://${API_DOMAIN}"
echo "NEXT_PUBLIC_API_BASE=${API_BASE} written to .env"
