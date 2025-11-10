cp install.sh install.sh.bak

cat > install.sh <<'SH'
#!/usr/bin/env bash
# Universal installer for Ozon Inventory Analytics (safe preflight)
set -Eeuo pipefail

LOG_DIR="${LOG_DIR:-./logs}"
LOG_FILE="${LOG_FILE:-${LOG_DIR}/install_$(date +%Y%m%d_%H%M%S).log}"
mkdir -p "${LOG_DIR}"; : > "${LOG_FILE}"

STEP_NUM=0
GREEN='\033[0;32m'; RED='\033[0;31m'; YELLOW='\033[1;33m'; CYAN='\033[0;36m'; NC='\033[0m'
say(){ echo -e "${CYAN}$*${NC}"; }
ok(){  echo -e "${GREEN}✔ $*${NC}"; }
warn(){echo -e "${YELLOW}▲ $*${NC}"; }
err(){ echo -e "${RED}✖ $*${NC}"; }
log(){ echo "[$(date +%H:%M:%S)] $*" | tee -a "${LOG_FILE}"; }
step(){ ((STEP_NUM++)); echo -e "\n${CYAN}==[ STEP ${STEP_NUM} ]== $* ${NC}"; log "STEP ${STEP_NUM}: $*"; }
run_cmd(){ log "RUN: $*"; bash -c "$*" >> "${LOG_FILE}" 2>&1; }

require_root(){ if [[ ${EUID} -ne 0 ]]; then err "Запустите: sudo ./install.sh"; exit 1; fi; }
require_root

# Проверим, что мы в корне проекта
if [[ ! -f "docker-compose.yml" ]]; then
  warn "Файл docker-compose.yml не найден в $(pwd)"
  read -rp "Продолжить в любом случае? [y/N]: " CONT || true
  [[ "${CONT,,}" == "y" || "${CONT,,}" == "yes" ]] || exit 1
fi

step "Системная информация"
OS_NAME="$(grep -E '^NAME=' /etc/os-release | cut -d= -f2- | tr -d '"' || true)"
OS_VER="$(grep -E '^VERSION=' /etc/os-release | cut -d= -f2- | tr -d '"' || true)"
KERNEL="$(uname -r || true)"
say "Дистрибутив: ${OS_NAME:-unknown} ${OS_VER:-}"
say "Ядро: ${KERNEL:-unknown}"
say "Логи: ${LOG_FILE}"

# Определяем пакетный менеджер
PKG=""
command -v apt-get >/dev/null 2>&1 && PKG=apt
command -v dnf >/dev/null 2>&1 && PKG=${PKG:-dnf}
if [[ -z "${PKG}" ]]; then err "Поддерживаются apt или dnf"; exit 1; fi
ok "Пакетный менеджер: ${PKG}"

step "Установка базовых зависимостей"
if [[ "${PKG}" == "apt" ]]; then
  run_cmd "apt-get update -y"
  run_cmd "apt-get install -y ca-certificates curl gnupg lsb-release unzip"
else
  run_cmd "dnf install -y ca-certificates curl gnupg2 unzip"
fi
ok "Базовые зависимости готовы"

step "Docker + Docker Compose"
if ! command -v docker >/dev/null 2>&1; then
  if [[ "${PKG}" == "apt" ]]; then
    run_cmd "install -m 0755 -d /etc/apt/keyrings"
    run_cmd "curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor -o /etc/apt/keyrings/docker.gpg"
    run_cmd "chmod a+r /etc/apt/keyrings/docker.gpg"
    UB_CODENAME="$(. /etc/os-release; echo \${VERSION_CODENAME:-jammy})"
    echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu ${UB_CODENAME} stable" > /etc/apt/sources.list.d/docker.list
    run_cmd "apt-get update -y"
    run_cmd "apt-get install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin"
  else
    run_cmd "dnf -y install dnf-plugins-core"
    run_cmd "dnf config-manager --add-repo https://download.docker.com/linux/centos/docker-ce.repo"
    run_cmd "dnf install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin"
  fi
  run_cmd "systemctl enable --now docker"
fi
ok "Docker: $(docker --version 2>/dev/null || echo installed)"
ok "Compose: $(docker compose version 2>/dev/null | head -n1 || echo installed)"

step "Подготовка .env"
if [[ ! -f ".env" ]]; then
  if [[ -f ".env.sample" ]]; then run_cmd "cp .env.sample .env"; else
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

read -rp "Админ e-mail [оставить по умолчанию — Enter]: " ADM_EMAIL || true
read -rp "Админ пароль [оставить по умолчанию — Enter]: " -s ADM_PASS || true; echo
read -rp "Telegram Bot Token (опц.): " TG_TOKEN || true
read -rp "SMTP host (опц.): " SMTP_HOST || true
read -rp "SMTP user (опц.): " SMTP_USER || true
read -rp "SMTP pass (опц.): " SMTP_PASS || true
read -rp "SMTP from (опц., напр. 'Ozon <noreply@domain>'): " SMTP_FROM || true

apply_env(){ local k="$1" v="$2"; [[ -z "${v}" ]] && return 0; grep -qE "^${k}=" .env && sed -i "s|^${k}=.*|${k}=${v}|" .env || echo "${k}=${v}" >> .env; }
apply_env FIRST_ADMIN_EMAIL "${ADM_EMAIL:-}"
apply_env FIRST_ADMIN_PASSWORD "${ADM_PASS:-}"
apply_env TELEGRAM_BOT_TOKEN "${TG_TOKEN:-}"
apply_env SMTP_HOST "${SMTP_HOST:-}"
apply_env SMTP_USER "${SMTP_USER:-}"
apply_env SMTP_PASSWORD "${SMTP_PASS:-}"
apply_env SMTP_FROM "${SMTP_FROM:-}"
ok ".env готов"

step "Nginx + HTTPS (опционально)"
read -rp "Настроить HTTPS сейчас? [y/N]: " USE_HTTPS || true
if [[ "${USE_HTTPS,,}" =~ ^y ]]; then
  read -rp "Домен (frontend), напр. example.com: " DOMAIN
  read -rp "E-mail для Let's Encrypt: " LE_EMAIL
  API_DOMAIN="api.${DOMAIN}"
  if [[ -n "${DOMAIN}" && -n "${LE_EMAIL}" ]]; then
    if [[ "${PKG}" == "apt" ]]; then run_cmd "apt-get install -y nginx certbot python3-certbot-nginx"; else run_cmd "dnf install -y nginx certbot python3-certbot-nginx"; fi
    run_cmd "systemctl enable --now nginx"
    cat >/etc/nginx/conf.d/ozon-inventory.conf <<NGX
map \$http_upgrade \$connection_upgrade { default upgrade; '' close; }
server { listen 80; server_name ${DOMAIN};
  location / { proxy_pass http://127.0.0.1:3000; proxy_set_header Host \$host; proxy_set_header X-Real-IP \$remote_addr;
    proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for; proxy_set_header X-Forwarded-Proto \$scheme;
    proxy_http_version 1.1; proxy_set_header Upgrade \$http_upgrade; proxy_set_header Connection \$connection_upgrade; } }
server { listen 80; server_name ${API_DOMAIN};
  location / { proxy_pass http://127.0.0.1:8000; proxy_set_header Host \$host; proxy_set_header X-Real-IP \$remote_addr;
    proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for; proxy_set_header X-Forwarded-Proto \$scheme; proxy_read_timeout 600s; } }
NGX
    run_cmd "nginx -t"
    run_cmd "systemctl reload nginx"
    if certbot --nginx -d "${DOMAIN}" -d "${API_DOMAIN}" --non-interactive --agree-tos -m "${LE_EMAIL}" --redirect; then
      ok "HTTPS настроен"
    else
      warn "Certbot не выдал сертификаты — проверьте DNS и повторите вручную"
    fi
  else
    warn "Домен/e-mail пустые — пропускаем HTTPS"
  fi
else
  warn "HTTPS пропущен. Сервисы будут доступны по 127.0.0.1:3000 и :8000"
fi

step "Docker Compose up"
run_cmd "docker compose up -d --build"
ok "Контейнеры подняты"

step "Миграции Alembic"
run_cmd "docker compose exec -T backend alembic upgrade head"
ok "Миграции применены"

step "Создание первого администратора"
run_cmd "docker compose exec -T backend python - <<'PY'
from app.db.session import SessionLocal
from app.db.seed import seed_first_admin
s=SessionLocal(); seed_first_admin(s); s.close()
print(\"admin seeded\")
PY"
ok "Администратор создан"

step "Готово"
if [[ -n "${DOMAIN:-}" ]]; then
  say "Frontend: https://${DOMAIN}"
  say "API:      https://api.${DOMAIN}"
else
  say "Frontend: http://127.0.0.1:3000"
  say "API:      http://127.0.0.1:8000"
fi
say "Логи: ${LOG_FILE}"
ok "Установка завершена"
SH
