
chatops-bot/
├── .github/                  # GitHub Actions (CI/CD)  
│   ├── workflows/  
│   │   ├── test.yaml         # Unit + Integration tests  
│   │   ├── deploy-prod.yaml  # Deploy to production  
│   │   └── deploy-staging.yaml  
├── backend/                      # Kotlin бот (Gradle)
│   ├── build.gradle.kts
│   ├── src/
│   │   ├── main/kotlin/com/yourcompany/bot/
│   │   │   ├── commands/         # Обработчики команд Telegram
│   │   │   │   ├── StatusCommand.kt  # → /status (вызов Flask API)
│   │   │   │   └── ...            
│   │   │   ├── api/              # Клиент для Flask API
│   │   │   │   ├── K8sApiClient.kt # HTTP-клиент
│   │   │   │   └── models/       # DTO для API
│   │   │   └── core/
│   │   │       ├── BotMain.kt     # Инициализация бота
│   │   │       └── Config.kt      # Загрузка конфигов
│   │   └── resources/
│   │       ├── application.conf  # Конфиг бота
│   │       └── api-endpoints.conf # URL Flask API
│   ├── Dockerfile                # Сборка Kotlin-образа
│   └── gradle/
├── k8s-api/                      # Flask микросервис
│   ├── src/
│   │   ├── app.py                # FastAPI/Flask entrypoint
│   │   ├── routes/
│   │   │   ├── k8s_status.py     # /api/v1/status
│   │   │   └── k8s_rollback.py   # /api/v1/rollback
│   │   ├── core/
│   │   │   ├── k8s_client.py     # Обертка для kubectl/helm
│   │   │   └── auth.py           # API-ключи
│   │   └── requirements.txt
│   ├── Dockerfile                # Сборка Python-образа
│   └── tests/
├── manifests/
│   ├── backend/                  # Для Kotlin бота
│   ├── k8s-api/                  # Для Flask API
│   │   ├── deployment.yaml
│   │   ├── service.yaml
│   │   └── ingress.yaml          # Если нужно внешнее API
│   └── rbac/
│       ├── bot-serviceaccount.yaml # Только для Flask API
│       └── api-serviceaccount.yaml  
├── docs/                     # Документация  
│   ├── commands.md           # Список команд  
│   └── setup-guide.md        # Развертывание  
├── .env.example              # Переменные окружения  
├── .gitignore  
├── Makefile                  # Упрощение команд (test, deploy)  
└── README.md                 # Общее описание + quick start  