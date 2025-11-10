#!/usr/bin/env bash
set -euo pipefail

# Colors
GREEN='\033[0;32m'; RED='\033[0;31m'; YELLOW='\033[1;33m'; NC='\033[0m'

confirm() {
  read -r -p "$1 [y/N]: " resp
  case "$resp" in [yY][eE][sS]|[yY]) true ;; *) false ;; esac
}

need_cmd() { command -v "$1" >/dev/null 2>&1 || { echo -e "${RED}❌ Требуется $1${NC}"; exit 1; }; }

# 0) Pre-flight
need_cmd docker
docker compose version >/dev/null 2>&1 || { echo -e "${RED}❌ Требуется Docker Compose v2${NC}"; exit 1; }

if [ ! -f ".env" ]; then
  echo -e "${YELLOW}Создаю .env из .env.sample${NC}"
  cp .env.sample .env
fi

# 1) Build & run stack (bound to localhost for reverse proxy)
echo -e "${GREEN}🔧 Сборка и запуск контейнеров...${NC}"
docker compose up --build -d

echo -e "${GREEN}🗄  Применяю миграции...${NC}"
docker compose exec -T backend alembic upgrade head

echo -e "${GREEN}👤 Сидирую первого администратора...${NC}"
docker compose exec -T backend python - <<'PY'
from app.db.session import SessionLocal
from app.db.seed import seed_first_admin
s=SessionLocal(); seed_first_admin(s); s.close()
PY

# 2) Nginx + Certbot
if confirm "Установить и настроить Nginx + Let's Encrypt сертификат?"; then
  # Detect package manager
  if command -v apt-get >/dev/null 2>&1; then
    PKG=apt
  elif command -v dnf >/dev/null 2>&1; then
    PKG=dnf
  else
    echo -e "${RED}⚠️  Неизвестный пакетный менеджер. Установите nginx и certbot вручную.${NC}"
    exit 0
  fi

  # Domain & email input
  read -r -p "Введите домен для фронтенда (например, example.com): " DOMAIN
  if [[ -z "${DOMAIN:-}" ]]; then echo -e "${RED}Домен обязателен${NC}"; exit 1; fi
  read -r -p "Введите e-mail для Let's Encrypt: " LE_EMAIL
  API_DOMAIN="api.${DOMAIN}"

  echo -e "${GREEN}📦 Устанавливаю nginx и certbot...${NC}"
  if [ "$PKG" = "apt" ]; then
    sudo apt-get update -y
    sudo apt-get install -y nginx certbot python3-certbot-nginx
  else
    sudo dnf install -y nginx certbot python3-certbot-nginx
  fi

  # Write nginx site config
  SITE_CONF="/etc/nginx/sites-available/ozon-inventory.conf"
  if [ ! -d "/etc/nginx/sites-available" ]; then
    # RHEL-like single config
    SITE_CONF="/etc/nginx/conf.d/ozon-inventory.conf"
    SITES_ENABLED_DIR="/etc/nginx/conf.d"
  else
    SITES_ENABLED_DIR="/etc/nginx/sites-enabled"
  fi

  TMP_CONF="$(mktemp)"
  cat >"$TMP_CONF" <<NGX
map \$http_upgrade \$connection_upgrade {
    default upgrade;
    ''      close;
}
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

  echo -e "${GREEN}📝 Записываю конфиг Nginx: ${SITE_CONF}${NC}"
  sudo mkdir -p "$(dirname "$SITE_CONF")" "$SITES_ENABLED_DIR"
  sudo cp "$TMP_CONF" "$SITE_CONF"
  if [ -d "/etc/nginx/sites-available" ]; then
    sudo ln -sf "$SITE_CONF" "/etc/nginx/sites-enabled/ozon-inventory.conf"
  fi
  sudo nginx -t
  sudo systemctl enable --now nginx || true
  sudo systemctl reload nginx || sudo systemctl restart nginx

  echo -e "${GREEN}🔐 Получаю сертификаты Let's Encrypt...${NC}"
  sudo certbot --nginx -d "${DOMAIN}" -d "${API_DOMAIN}" --non-interactive --agree-tos -m "${LE_EMAIL}" || {
    echo -e "${YELLOW}⚠️  Автовыдача не удалась. Проверьте DNS A‑записи и повторите: certbot --nginx -d ${DOMAIN} -d ${API_DOMAIN}${NC}"
  }

  echo -e "${GREEN}✅ Готово! Доступы:${NC}\n - https://${DOMAIN} (Frontend)\n - https://${API_DOMAIN} (API)"
else
  echo -e "${YELLOW}Пропущена настройка Nginx/LE. Приложение доступно локально на 127.0.0.1:3000 и :8000${NC}"
fi
