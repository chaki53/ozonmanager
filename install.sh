#!/usr/bin/env bash
# Universal installer for Ozon Inventory Analytics
# - Installs Docker & Compose, Nginx, Certbot
# - Builds & runs containers
# - Applies DB migrations, seeds first admin
# - Optional HTTPS with Let's Encrypt
# - Interactive prompts and per-step logs
#
# Usage: sudo bash install.sh

set -Eeuo pipefail

#=============================#
#         UTILITIES           #
#=============================#

LOG_DIR="${LOG_DIR:-./logs}"
LOG_FILE="${LOG_FILE:-${LOG_DIR}/install_$(date +%Y%m%d_%H%M%S).log}"
mkdir -p "${LOG_DIR}"
touch "${LOG_FILE}"

STEP_NUM=0
GREEN='\033[0;32m'; RED='\033[0;31m'; YELLOW='\033[1;33m'; CYAN='\033[0;36m'; NC='\033[0m'

say()      { echo -e "${CYAN}$*${NC}"; }
ok()       { echo -e "${GREEN}✔ $*${NC}"; }
warn()     { echo -e "${YELLOW}▲ $*${NC}"; }
err()      { echo -e "${RED}✖ $*${NC}"; }
log()      { echo "[$(date +%H:%M:%S)] $*" | tee -a "${LOG_FILE}"; }
step()     { ((STEP_NUM++)); echo -e "\n${CYAN}==[ STEP ${STEP_NUM} ]== $* ${NC}"; log "STEP ${STEP_NUM}: $*"; }
run_cmd()  { log "RUN: $*"; eval "$@" >> "${LOG_FILE}" 2>&1; }

require_root() {
  if [[ "${EUID}" -ne 0 ]]; then
    err "Запустите: sudo bash install.sh"
    exit 1
  fi
}

#=============================#
#         PRE-FLIGHT          #
#=============================#

require_root

if [[ ! -f "docker-compose.yml" ]]; then
  warn "Файл docker-compose.yml не найден в текущей директории: $(pwd)"
  warn "Убедитесь, что запускаете скрипт из корня проекта."
  read -rp "Продолжить в любом случае? [y/N]: " CONT
  [[ "${CONT,,}" == "y" || "${CONT,,}" == "yes" ]] || exit 1
fi

step "Системная информация"
say "Дистрибутив: $(. /etc/os-release; echo ${NAME} ${VERSION})"
say "Ядро: $(uname -r)"
say "Логи: ${LOG_FILE}"

# Detect package manager
PKG=""
if command -v apt-get >/dev/null 2>&1; then PKG=apt; fi
if command -v dnf >/dev/null 2>&1; then PKG=dnf; fi
if [[ -z "${PKG}" ]]; then err "Неизвестный пакетный менеджер. Поддерживаются apt и dnf."; exit 1; fi
ok "Пакетный менеджер: ${PKG}"

#=============================#
#       DEPENDENCIES          #
#=============================#

step "Установка зависимостей: curl, gnupg, ca-certificates, unzip"
if [[ "${PKG}" == "apt" ]]; then
  run_cmd "apt-get update -y"
  run_cmd "apt-get install -y ca-certificates curl gnupg lsb-release unzip"
else
  run_cmd "dnf install -y ca-certificates curl gnupg2 unzip"
fi
ok "Базовые зависимости готовы"

#=============================#
#         DOCKER SETUP        #
#=============================#

step "Проверка и установка Docker + Docker Compose"
if ! command -v docker >/dev/null 2>&1; then
  if [[ "${PKG}" == "apt" ]]; then
    run_cmd "install -m 0755 -d /etc/apt/keyrings"
    run_cmd "curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor -o /etc/apt/keyrings/docker.gpg"
    run_cmd "chmod a+r /etc/apt/keyrings/docker.gpg"
    UB_CODENAME="$(. /etc/os-release; echo $VERSION_CODENAME)"
    echo \
      "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] \
https://download.docker.com/linux/ubuntu ${UB_CODENAME} stable" \
      > /etc/apt/sources.list.d/docker.list
    run_cmd "apt-get update -y"
    run_cmd "apt-get install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin"
  else
    run_cmd "dnf -y install dnf-plugins-core"
    run_cmd "dnf config-manager --add-repo https://download.docker.com/linux/centos/docker-ce.repo"
    run_cmd "dnf install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin"
  fi
  run_cmd "systemctl enable --now docker"
else
  ok "Docker уже установлен: $(docker --version)"
fi

if ! docker compose version >/dev/null 2>&1; then
  err "Docker Compose v2 не установлен. Проверьте docker-compose-plugin."
  exit 1
fi
ok "Docker Compose: $(docker compose version | head -n1)"

#=============================#
#         .ENV SETUP          #
#=============================#

step "Подготовка .env"
if [[ ! -f ".env" ]]; then
  if [[ -f ".env.sample" ]]; then
    run_cmd "cp .env.sample .env"
    ok "Создан .env из .env.sample"
  else
    warn ".env.sample не найден — создаю минимальный .env"
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

# Prompt for key env vars
read -rp "Админ e-mail [$(grep -E '^FIRST_ADMIN_EMAIL=' .env | cut -d= -f2-)]: " ADM_EMAIL || true
read -rp "Админ пароль [скрыт, ENTER чтобы оставить]: " -s ADM_PASS || true; echo
read -rp "Телеграм Bot Token (опционально): " TG_TOKEN || true
read -rp "SMTP host (опционально): " SMTP_HOST || true
read -rp "SMTP user (опционально): " SMTP_USER || true
read -rp "SMTP password (опционально): " SMTP_PASS || true
read -rp "SMTP from (опционально, напр. 'Ozon <noreply@domain>'): " SMTP_FROM || true

# Apply edits
apply_env() {
  key="$1"; val="$2"
  if grep -qE "^${key}=" .env; then
    sed -i "s|^${key}=.*|${key}=${val}|" .env
  else
    echo "${key}=${val}" >> .env
  fi
}
[[ -n "${ADM_EMAIL:-}" ]] && apply_env "FIRST_ADMIN_EMAIL" "${ADM_EMAIL}"
[[ -n "${ADM_PASS:-}"  ]] && apply_env "FIRST_ADMIN_PASSWORD" "${ADM_PASS}"
[[ -n "${TG_TOKEN:-}"  ]] && apply_env "TELEGRAM_BOT_TOKEN" "${TG_TOKEN}"
[[ -n "${SMTP_HOST:-}" ]] && apply_env "SMTP_HOST" "${SMTP_HOST}"
[[ -n "${SMTP_USER:-}" ]] && apply_env "SMTP_USER" "${SMTP_USER}"
[[ -n "${SMTP_PASS:-}" ]] && apply_env "SMTP_PASSWORD" "${SMTP_PASS}"
[[ -n "${SMTP_FROM:-}" ]] && apply_env "SMTP_FROM" "${SMTP_FROM}"

ok ".env готов"

#=============================#
#       NGINX + CERTBOT       #
#=============================#

step "Настройка Nginx и HTTPS (опционально)"
read -rp "Указать домен и настроить HTTPS сейчас? (например, myshop.ru) [y/N]: " USE_HTTPS
if [[ "${USE_HTTPS,,}" == "y" || "${USE_HTTPS,,}" == "yes" ]]; then
  read -rp "Введите домен для фронтенда (например, example.com): " DOMAIN
  read -rp "Введите e-mail для Let's Encrypt: " LE_EMAIL
  API_DOMAIN="api.${DOMAIN}"
  if [[ -z "${DOMAIN}" || -z "${LE_EMAIL}" ]]; then
    err "Домен и e-mail обязательны для HTTPS. Пропускаю установку Nginx/LE."
  else
    # Install nginx + certbot
    if [[ "${PKG}" == "apt" ]]; then
      run_cmd "apt-get install -y nginx certbot python3-certbot-nginx"
    else
      run_cmd "dnf install -y nginx certbot python3-certbot-nginx"
    fi
    run_cmd "systemctl enable --now nginx"

    # Generate config
    SITE_CONF="/etc/nginx/conf.d/ozon-inventory.conf"
    cat > "${SITE_CONF}" <<NGX
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

    # Certbot
    say "Запрашиваю сертификаты для ${DOMAIN} и ${API_DOMAIN}..."
    if certbot --nginx -d "${DOMAIN}" -d "${API_DOMAIN}" --non-interactive --agree-tos -m "${LE_EMAIL}" --redirect; then
      ok "Sertbot успешно выдал сертификаты"
    else
      warn "Не удалось получить сертификаты. Проверьте DNS A-записи и повторите:\n  certbot --nginx -d ${DOMAIN} -d ${API_DOMAIN} -m ${LE_EMAIL} --agree-tos --redirect"
    fi
  fi
else
  warn "Пропускаем настройку Nginx/HTTPS. Сервисы будут доступны по 127.0.0.1:3000 и :8000"
fi

#=============================#
#     DOCKER COMPOSE UP       #
#=============================#

step "Сборка и запуск контейнеров Docker Compose"
run_cmd "docker compose up -d --build"
ok "Контейнеры запущены"

#=============================#
#    DB MIGRATIONS & SEED     #
#=============================#

step "Применение миграций Alembic"
run_cmd "docker compose exec -T backend alembic upgrade head"
ok "Миграции применены"

step "Создание первого администратора"
run_cmd "docker compose exec -T backend python - <<'PY'\nfrom app.db.session import SessionLocal\nfrom app.db.seed import seed_first_admin\ns=SessionLocal(); seed_first_admin(s); s.close()\nPY"
ok "Администратор готов"

#=============================#
#          FINISH             #
#=============================#

step "Готово!"
say "Логи установки: ${LOG_FILE}"
if [[ -n "${DOMAIN:-}" ]]; then
  say "Frontend: https://${DOMAIN}"
  say "API:      https://${API_DOMAIN}"
else
  say "Frontend: http://127.0.0.1:3000"
  say "API:      http://127.0.0.1:8000"
fi
say "Логин администратора и остальные настройки см. в .env"
ok "Установка завершена"
