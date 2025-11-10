#!/bin/bash
# Universal installer for Ozon Inventory Analytics (safe, verbose)
# Usage: sudo ./install.sh

set -euo pipefail

# -----------------------------
# Logging & helpers
# -----------------------------
LOG_DIR="${LOG_DIR:-./logs}"
mkdir -p "$LOG_DIR"
LOG_FILE="${LOG_FILE:-${LOG_DIR}/install_$(date +%Y%m%d_%H%M%S).log}"
: > "$LOG_FILE"

STEP_NUM=0
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

say() { echo -e "${CYAN}$*${NC}"; }
ok()  { echo -e "${GREEN}✔ $*${NC}"; }
warn(){ echo -e "${YELLOW}▲ $*${NC}"; }
err() { echo -e "${RED}✖ $*${NC}"; }
log() { echo "[$(date +%H:%M:%S)] $*" | tee -a "$LOG_FILE" >/dev/null; }
step(){ STEP_NUM=$((STEP_NUM+1)); echo -e "\n${CYAN}==[ STEP ${STEP_NUM} ]== $* ${NC}"; log "STEP ${STEP_NUM}: $*"; }
run_cmd() {
  log "RUN: $*"
  bash -c "$*" >>"$LOG_FILE" 2>&1
}

require_root() {
  if [ "$(id -u)" -ne 0 ]; then
    err "Запустите: sudo ./install.sh"
    exit 1
  fi
}
require_root

# -----------------------------
# Pre-flight
# -----------------------------
if [ ! -f "docker-compose.yml" ]; then
  warn "Файл docker-compose.yml не найден в $(pwd)"
  read -r -p "Продолжить в любом случае? [y/N]: " CONT
  case "$CONT" in
    y|Y|yes|YES) ;;
    *) exit 1 ;;
  esac
fi

step "Системная информация"
OS_NAME="$(grep -E '^NAME=' /etc/os-release 2>/dev/null | cut -d= -f2- | tr -d '"' || true)"
OS_VER="$(grep -E '^VERSION=' /etc/os-release 2>/dev/null | cut -d= -f2- | tr -d '"' || true)"
KERNEL="$(uname -r || true)"
say "Дистрибутив: ${OS_NAME:-unknown} ${OS_VER:-}"
say "Ядро: ${KERNEL:-unknown}"
say "Логи: ${LOG_FILE}"

PKG=""
if command -v apt-get >/dev/null 2>&1; then PKG="apt"; fi
if command -v dnf >/dev/null 2>&1; then PKG="${PKG:-dnf}"; fi
if [ -z "$PKG" ]; then
  err "Поддерживаются только apt и dnf."
  exit 1
fi
ok "Пакетный менеджер: $PKG"

# -----------------------------
# Base deps
# -----------------------------
step "Установка базовых зависимостей"
if [ "$PKG" = "apt" ]; then
  run_cmd "apt-get update -y"
  run_cmd "apt-get install -y ca-certificates curl gnupg lsb-release unzip"
else
  run_cmd "dnf install -y ca-certificates curl gnupg2 unzip"
fi
ok "Базовые зависимости готовы"

# -----------------------------
# Docker & Compose
# -----------------------------
step "Docker + Docker Compose"
if ! command -v docker >/dev/null 2>&1; then
  if [ "$PKG" = "apt" ]; then
    run_cmd "install -m 0755 -d /etc/apt/keyrings"
    run_cmd "curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor -o /etc/apt/keyrings/docker.gpg"
    run_cmd "chmod a+r /etc/apt/keyrings/docker.gpg"
    UB_CODENAME="$(. /etc/os-release 2>/dev/null; echo ${VERSION_CODENAME:-jammy})"
    echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu ${UB_CODENAME} stable" >/etc/apt/sources.list.d/docker.list
    run_cmd "apt-get update -y"
    run_cmd "apt-get install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin"
  else
    run_cmd "dnf -y install dnf-plugins-core"
    run_cmd "dnf config-manager --add-repo https://download.docker.com/linux/centos/docker-ce.repo"
    run_cmd "dnf install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin"
  fi
  run_cmd "systemctl enable --now docker"
else
  ok "Docker уже установлен: $(docker --version 2>/dev/null || echo)"
fi

if ! docker compose version >/dev/null 2>&1; then
  err "Docker Compose v2 (docker-compose-plugin) не найден."
  exit 1
fi
ok "Compose: $(docker compose version 2>/dev/null | head -n1 || echo installed)"

# -----------------------------
# .env setup
# -----------------------------
step "Подготовка .env"
if [ ! -f ".env" ]; then
  if [ -f ".env.sample" ]; then
    run_cmd "cp .env.sample .env"
  else
    cat > .env <<'ENVV'
SECRET_KEY=changeme
SQLALCHEMY_DATABASE_URI=postgresql+psycopg2://postgres:postgres@db:5432/postgres
POSTGRES_DB=postgres
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
REDIS_URL=redis://redis:6379/0
FIRST_ADMIN_EMAIL=admin@local
FIRST_ADMIN_PASSWORD=admin123
SMTP_HOST=
SMTP_PORT=587
SMTP_USER=
SMTP_PASSWORD=
SMTP_FROM="Ozon Analytics <noreply@example.com>"
TELEGRAM_BOT_TOKEN=
SYNC_PERIOD_SECONDS=10800
DAILY_REPORT_SECONDS=86400
OZON_BASE_URL=https://api-seller.ozon.ru
OZON_READONLY=true
ENVV
  fi
fi

printf "Админ e-mail [Enter — оставить по умолчанию]: "
read -r ADM_EMAIL || true
printf "Админ пароль [Enter — оставить]: "
stty -echo; read -r ADM_PASS || true; stty echo; echo
printf "Telegram Bot Token (опционально): "
read -r TG_TOKEN || true
printf "SMTP host (опц.): "
read -r SMTP_HOST || true
printf "SMTP user (опц.): "
read -r SMTP_USER || true
printf "SMTP pass (опц.): "
read -r SMTP_PASS || true
printf "SMTP from (опц., напр. 'Ozon <noreply@domain>'): "
read -r SMTP_FROM || true

apply_env() {
  key="$1"; val="$2"
  [ -z "$val" ] && return 0
  if grep -qE "^${key}=" .env; then
    sed -i "s|^${key}=.*|${key}=${val}|" .env
  else
    echo "${key}=${val}" >> .env
  fi
}
apply_env FIRST_ADMIN_EMAIL "$ADM_EMAIL"
apply_env FIRST_ADMIN_PASSWORD "$ADM_PASS"
apply_env TELEGRAM_BOT_TOKEN "$TG_TOKEN"
apply_env SMTP_HOST "$SMTP_HOST"
apply_env SMTP_USER "$SMTP_USER"
apply_env SMTP_PASSWORD "$SMTP_PASS"
apply_env SMTP_FROM "$SMTP_FROM"

ok ".env готов"

# -----------------------------
# Nginx + HTTPS (optional)
# -----------------------------
step "Nginx + HTTPS (опционально)"
printf "Настроить HTTPS сейчас? [y/N]: "
read -r USE_HTTPS || true
if [ "$USE_HTTPS" = "y" ] || [ "$USE_HTTPS" = "Y" ] || [ "$USE_HTTPS" = "yes" ] || [ "$USE_HTTPS" = "YES" ]; then
  printf "Домен (frontend), напр. example.com: "
  read -r DOMAIN
  printf "E-mail для Let's Encrypt: "
  read -r LE_EMAIL
  API_DOMAIN="api.${DOMAIN}"
  if [ -n "$DOMAIN" ] && [ -n "$LE_EMAIL" ]; then
    if [ "$PKG" = "apt" ]; then
      run_cmd "apt-get install -y nginx certbot python3-certbot-nginx"
    else
      run_cmd "dnf install -y nginx certbot python3-certbot-nginx"
    fi
    run_cmd "systemctl enable --now nginx"

    cat >/etc/nginx/conf.d/ozon-inventory.conf <<NGX
map \$http_upgrade \$connection_upgrade { default upgrade; '' close; }
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
  client_max_body_size 50m;
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

    run_cmd "nginx -t"
    run_cmd "systemctl reload nginx"

    say "Запрашиваю сертификаты для ${DOMAIN} и ${API_DOMAIN}..."
    if certbot --nginx -d "$DOMAIN" -d "$API_DOMAIN" --non-interactive --agree-tos -m "$LE_EMAIL" --redirect; then
      ok "HTTPS настроен"
    else
      warn "Certbot не выдал сертификаты. Проверьте DNS и повторите команду вручную:
  certbot --nginx -d ${DOMAIN} -d ${API_DOMAIN} -m ${LE_EMAIL} --agree-tos --redirect"
    fi
  else
    warn "Домен/e-mail не заданы — пропускаем HTTPS"
  fi
else
  warn "HTTPS пропущен. Сервисы будут доступны по 127.0.0.1:3000 и :8000"
fi

# -----------------------------
# Docker Compose up
# -----------------------------
step "Сборка и запуск контейнеров"
run_cmd "docker compose up -d --build"
ok "Контейнеры подняты"

# -----------------------------
# DB migrations & seed
# -----------------------------
step "Миграции Alembic"
run_cmd "docker compose exec -T backend alembic upgrade head"
ok "Миграции применены"

step "Создание первого администратора"
run_cmd "docker compose exec -T backend python - <<'PY'
from app.db.session import SessionLocal
from app.db.seed import seed_first_admin
s=SessionLocal(); seed_first_admin(s); s.close()
print("admin seeded")
PY"
ok "Администратор создан"

# -----------------------------
# Finish
# -----------------------------
step "Готово"
if [ "${DOMAIN:-}" ]; then
  say "Frontend: https://${DOMAIN}"
  say "API:      https://api.${DOMAIN}"
else
  say "Frontend: http://127.0.0.1:3000"
  say "API:      http://127.0.0.1:8000"
fi
say "Логи: ${LOG_FILE}"
ok "Установка завершена"
