# ChatOps Bot for Kubernetes Incident Management 🤖⚡

Telegram-бот для быстрого реагирования на инциденты в Kubernetes-кластере. Позволяет управлять сервисами через чат без доступа к `kubectl`.

[![CI](https://github.com/yourname/chatops-bot/actions/workflows/test.yaml/badge.svg)](https://github.com/yourname/chatops-bot/actions)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

## 🔥 Возможности

- **Основные команды:**
  - `/status` — показать метрики сервиса (Grafana/Prometheus)
  - `/rollback <версия>` — откатить деплой (Helm/ArgoCD)
  - `/scale <сервис> +N` — масштабировать реплики
  - `/restart <pod>` — перезапустить под

- **Безопасность:**
  - Подтверждение опасных операций
  - RBAC через Kubernetes ServiceAccount
  - Логирование всех действий

- **Интеграции:**
  - Prometheus/Alertmanager → автоматические алерты в Telegram
  - N8N → low-code сценарии (авто-откат при 5xx ошибках)
  - LLM (опционально) → анализ логов на естественном языке

## 🚀 Быстрый старт

### Требования
- Kubernetes 1.20+
- Python 3.10+ (или Go 1.18+ для Go-версии)
- Telegram API-ключ

### Установка
```bash
# Клонировать репозиторий
git clone https://github.com/Tixon-noxit/CHATOPS.git
cd CHATOPS

# Установить зависимости (Python)
pip install -r backend/requirements.txt

# Запустить в dev-режиме
cp .env.example .env
export $(cat .env | xargs)
python backend/src/main.py
