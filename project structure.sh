chatops-bot/  
├── .github/                  # GitHub Actions (CI/CD)  
│   ├── workflows/  
│   │   ├── test.yaml         # Unit + Integration tests  
│   │   ├── deploy-prod.yaml  # Deploy to production  
│   │   └── deploy-staging.yaml  
├── backend/                  # Основная логика бота  
│   ├── src/  
│   │   ├── commands/         # Обработчики команд  
│   │   │   ├── status.py     # /status → Prometheus  
│   │   │   ├── rollback.py   # /rollback → Helm  
│   │   │   └── scale.py      # /scale → k8s API  
│   │   ├── core/  
│   │   │   ├── bot.py        # Инициализация Telegram-бота  
│   │   │   ├── k8s.py        # Kubernetes API client  
│   │   │   └── auth.py       # RBAC + проверка доступа  
│   │   ├── models/           # Pydantic/DTO  
│   │   │   └── alerts.py     # Модель алерта (Alertmanager)  
│   │   ├── utils/            # Вспомогательные функции  
│   │   │   └── logging.py    # Логирование действий  
│   │   └── main.py           # FastAPI/Flask entrypoint  
│   ├── tests/                # Юнит-тесты  
│   │   ├── test_commands/  
│   │   └── test_k8s_integration/  
│   ├── Dockerfile            # Сборка образа  
│   └── requirements.txt      # Python-зависимости  
├── n8n/                      # Low-code automation  
│   ├── workflows/  
│   │   ├── alert-handler.json  # Триггер на алерт → бот  
│   │   └── auto-rollback.json  # Автооткат при критической ошибке  
│   └── Dockerfile            # (Опционально)  
├── manifests/                # Kubernetes-манифесты  
│   ├── backend/  
│   │   ├── deployment.yaml  
│   │   └── service.yaml  
│   ├── n8n/  
│   │   └── deployment.yaml  
│   └── rbac/                 # Права для бота в k8s  
│       └── bot-serviceaccount.yaml  
├── docs/                     # Документация  
│   ├── commands.md           # Список команд  
│   └── setup-guide.md        # Развертывание  
├── .env.example              # Переменные окружения  
├── .gitignore  
├── Makefile                  # Упрощение команд (test, deploy)  
└── README.md                 # Общее описание + quick start  