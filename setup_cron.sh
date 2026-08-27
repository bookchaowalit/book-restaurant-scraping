#!/usr/bin/env bash
# Weekly Wongnai collector for book-restaurant-scraping.
set -euo pipefail

PROJECT_DIR="$(cd "$(dirname "$0")" && pwd)"
CRON_TAG="# book-restaurant-scraping-feeds"
LOCK_FILE="${PROJECT_DIR}/data/restaurants.lock"
LOG_FILE="${PROJECT_DIR}/data/logs/cron.log"

ensure_venv() {
    if [ ! -x "${PROJECT_DIR}/.venv/bin/python" ]; then
        python3 -m venv "${PROJECT_DIR}/.venv"
        "${PROJECT_DIR}/.venv/bin/pip" install -r "${PROJECT_DIR}/requirements.txt"
    fi
}

python_bin() {
    if [ -x "${PROJECT_DIR}/.venv/bin/python" ]; then
        echo "${PROJECT_DIR}/.venv/bin/python"
    else
        command -v python3
    fi
}

install_cron() {
    ensure_venv
    mkdir -p "${PROJECT_DIR}/data/logs" "${PROJECT_DIR}/data/exported"
    crontab -l 2>/dev/null | grep -v "${CRON_TAG}" | crontab - 2>/dev/null || true
    PYTHON="$(python_bin)"
    (crontab -l 2>/dev/null || true; echo "15 0 * * 0 cd ${PROJECT_DIR} && flock -n ${LOCK_FILE} ${PYTHON} scripts/run_restaurants.py --max-pages 3 --min-rows 20 >> ${LOG_FILE} 2>&1 ${CRON_TAG}") | crontab -
    echo "Cron installed weekly Sunday 00:15"
    echo "Python: ${PYTHON}"
}

remove_cron() {
    crontab -l 2>/dev/null | grep -v "${CRON_TAG}" | crontab - 2>/dev/null || true
    echo "Cron removed"
}

show_status() {
    if crontab -l 2>/dev/null | grep -q "${CRON_TAG}"; then
        crontab -l | grep "${CRON_TAG}"
        echo "Status: ACTIVE"
    else
        echo "Status: NOT INSTALLED"
    fi
}

case "${1:-}" in
    install) install_cron ;;
    remove) remove_cron ;;
    status) show_status ;;
    *) echo "Usage: $0 {install|remove|status}"; exit 1 ;;
esac
