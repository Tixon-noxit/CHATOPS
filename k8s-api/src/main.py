import os
import sqlite3

from flask import Flask, request, jsonify, abort, g
import random
import requests
from datetime import datetime
from contextlib import closing
from prometheus_api_client import PrometheusConnect

app = Flask(__name__)
app.config['DATABASE'] = 'chat_bot.db'

# Конфигурация
API_KEYS = ["secret_key_123", "another_secret_key_456"]
TELEGRAM_TOKEN = '7107706287:AAGVQV9gWCVyo3zpKkNrMoVdsBpVTh4nbrM'
PROMETHEUS_URL = 'http://localhost:9090'  # URL вашего Prometheus

# Инициализация клиента Prometheus
prometheus = PrometheusConnect(url=PROMETHEUS_URL, disable_ssl=True)


# Функции для работы с БД
def get_db():
    if not hasattr(g, 'sqlite_db'):
        g.sqlite_db = sqlite3.connect(app.config['DATABASE'])
        g.sqlite_db.row_factory = sqlite3.Row
    return g.sqlite_db


def init_db():
    with closing(get_db()) as db:
        # Создаем таблицу, если ее нет
        db.execute("""
        CREATE TABLE IF NOT EXISTS chats (
            chat_id TEXT PRIMARY KEY,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)
        db.commit()


@app.teardown_appcontext
def close_db(error):
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()


def add_chat_id_to_db(chat_id):
    db = get_db()
    try:
        db.execute("INSERT INTO chats (chat_id) VALUES (?)", (str(chat_id),))
        db.commit()
        return True
    except sqlite3.IntegrityError:
        return False  # Уже существует


def remove_chat_id_from_db(chat_id):
    db = get_db()
    db.execute("DELETE FROM chats WHERE chat_id = ?", (str(chat_id),))
    db.commit()
    return db.total_changes > 0


def get_all_chat_ids_from_db():
    db = get_db()
    cur = db.execute("SELECT chat_id FROM chats")
    return [row['chat_id'] for row in cur.fetchall()]


# Создаем файл БД при первом запуске
if not os.path.exists(app.config['DATABASE']):
    with app.app_context():
        init_db()


# Middleware для проверки авторизации
@app.before_request
def check_auth():
    protected_endpoints = ['status', 'rollback', 'scale', 'webhook',
                           'add_chat_id', 'send_alert', 'get_chat_ids',
                           'remove_chat_id']
    if request.endpoint in protected_endpoints:
        auth_header = request.headers.get('Authorization')
        if not auth_header or auth_header.split()[-1] not in API_KEYS:
            abort(401, description="Unauthorized: Invalid API key")


# Функция отправки в Telegram
def send_telegram_message(chat_id, message):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": message,
        "parse_mode": "Markdown"
    }
    try:
        response = requests.post(url, json=payload)
        return response.json()
    except Exception as e:
        print(f"Telegram send error to {chat_id}: {str(e)}")
        return None


# Генерация мок-данных
def generate_cpu_data():
    cores = random.randint(1, 16)
    return [{
        "loaded": random.randint(1, 100),
        "cores": cores
    } for _ in range(1)]


def generate_ram_data():
    max_ram = random.choice([4096, 8192, 16384, 32768])
    return {
        "used": random.randint(1024, max_ram - 1024),
        "max": max_ram
    }


# Новые функции для работы с Prometheus
def get_cpu_usage():
    query = '100 - (avg by(instance) (rate(node_cpu_seconds_total{mode="idle"}[5m])) * 100)'
    result = prometheus.custom_query(query)
    return {item['metric']['instance']: float(item['value'][1]) for item in result}


def get_ram_usage():
    query = 'node_memory_MemTotal_bytes - node_memory_MemAvailable_bytes'
    result = prometheus.custom_query(query)
    return {item['metric']['instance']: float(item['value'][1]) / (1024 * 1024) for item in result}  # в MB


def get_ram_total():
    query = 'node_memory_MemTotal_bytes'
    result = prometheus.custom_query(query)
    return {item['metric']['instance']: float(item['value'][1]) / (1024 * 1024) for item in result}  # в MB


# Эндпоинты мониторинга
@app.route('/api/status', methods=['GET'])
def status():
    data = request.get_json()
    chat_id = data.get('chat_id') if data else None

    # # Генерация данных
    # cpu_data = generate_cpu_data()
    # ram_data = generate_ram_data()
    #
    # # Определение статусных эмодзи
    # cpu_emoji = "🔥" if cpu_data[0]['loaded'] > 80 else "✅" if cpu_data[0]['loaded'] < 30 else "⚠️"
    # ram_emoji = "🔥" if (ram_data['used'] / ram_data['max']) > 0.8 else "✅" if (ram_data['used'] / ram_data[
    #     'max']) < 0.3 else "⚠️"
    #
    # # Форматирование сообщения
    # alert_msg = (
    #     "📊 *System Status Report*\n\n"
    #     f"🕒 *Time*: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
    #     f"{cpu_emoji} *CPU Usage*\n"
    #     f"• Load: {cpu_data[0]['loaded']}%\n"
    #     f"• Cores: {cpu_data[0]['cores']}\n\n"
    #     f"{ram_emoji} *Memory Usage*\n"
    #     f"• Used: {ram_data['used']} MB\n"
    #     f"• Total: {ram_data['max']} MB\n"
    #     f"• Usage: {round((ram_data['used'] / ram_data['max']) * 100, 1)}%"
    # )
    #
    # send_telegram_message(chat_id, alert_msg)
    #
    # return jsonify({
    #     "cpu": cpu_data,
    #     "ram": ram_data,
    #     "status": "success",
    #     "timestamp": datetime.now().isoformat()
    # })
    try:
        # Получаем данные из Prometheus
        cpu_usage = get_cpu_usage()
        ram_used = get_ram_usage()
        ram_total = get_ram_total()

        # Формируем сообщение
        message = "📊 *System Status Report*\n\n"
        message += f"🕒 *Time*: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"

        for instance in cpu_usage.keys():
            cpu_load = cpu_usage[instance]
            ram_usage = ram_used[instance]
            ram_total_mb = ram_total[instance]
            ram_percent = (ram_usage / ram_total_mb) * 100

            cpu_emoji = "🔥" if cpu_load > 80 else "✅" if cpu_load < 30 else "⚠️"
            ram_emoji = "🔥" if ram_percent > 80 else "✅" if ram_percent < 30 else "⚠️"

            message += f"🖥 *{instance}*\n"
            message += f"{cpu_emoji} *CPU*: {cpu_load:.1f}%\n"
            message += f"{ram_emoji} *RAM*: {ram_usage:.1f}/{ram_total_mb:.1f} MB ({ram_percent:.1f}%)\n\n"

        # Отправляем сообщение
        if chat_id:
            send_telegram_message(chat_id, message)

        return jsonify({
            "status": "success",
            "cpu": cpu_usage,
            "ram_used": ram_used,
            "ram_total": ram_total
        })

    except Exception as e:
        error_msg = f"⚠️ Error getting status from Prometheus: {str(e)}"
        if chat_id:
            send_telegram_message(chat_id, error_msg)
        return jsonify({"error": str(e)}), 500


@app.route('/api/rollback', methods=['POST'])
def rollback():
    alert_msg = (
        "🔄 *Rollback initiated*\n\n"
        f"*Time*: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        "*Service*: Main Application"
    )

    # Отправка всем зарегистрированным чатам
    for chat_id in get_all_chat_ids_from_db():
        send_telegram_message(chat_id, alert_msg)

    return jsonify({
        "status": "success",
        "message": "Rollback completed",
        "version": f"1.0.{random.randint(1, 10)}"
    })


@app.route('/api/scale', methods=['POST'])
def scale():
    if not request.is_json:
        abort(415, description="Content-Type must be application/json")

    data = request.get_json()
    instances = data.get('instances', 1)

    alert_msg = (
        "⚖️ *Scaling event*\n\n"
        f"*Time*: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        f"*Action*: Scaled to {instances} instances\n"
        f"*Service*: {data.get('service', 'Unknown')}"
    )

    for chat_id in get_all_chat_ids_from_db():
        send_telegram_message(chat_id, alert_msg)

    return jsonify({
        "status": "success",
        "message": f"Scaled to {instances} instances",
        "instances": instances
    })


# Эндпоинты управления чатами
@app.route('/api/telegram/add_chat_id', methods=['POST'])
def add_chat_id():
    data = request.get_json()

    if not data or 'chat_id' not in data:
        return jsonify({"error": "chat_id is required"}), 400

    chat_id = str(data['chat_id'])

    if add_chat_id_to_db(chat_id):
        confirmation_msg = (
            "✅ *Registration successful*\n\n"
            "Your chat ID has been registered for alerts.\n"
            f"*Chat ID*: `{chat_id}`\n"
            f"*Time*: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        )
        send_telegram_message(chat_id, confirmation_msg)
        return jsonify({
            "status": "success",
            "chat_id": chat_id,
            "total_chats": len(get_all_chat_ids_from_db())
        })
    else:
        return jsonify({
            "status": "error",
            "message": "Chat ID already exists"
        }), 409


@app.route('/api/telegram/remove_chat_id', methods=['POST'])
def remove_chat_id():
    data = request.get_json()

    if not data or 'chat_id' not in data:
        return jsonify({"error": "chat_id is required"}), 400

    chat_id = str(data['chat_id'])
    if remove_chat_id_from_db(chat_id):
        return jsonify({
            "status": "success",
            "message": f"Chat ID {chat_id} removed",
            "total_chats": len(get_all_chat_ids_from_db())
        })
    else:
        return jsonify({
            "status": "error",
            "message": f"Chat ID {chat_id} not found"
        }), 404


@app.route('/api/telegram/send_alert', methods=['POST'])
def send_alert():
    data = request.get_json()

    if not data or 'message' not in data:
        return jsonify({"error": "message is required"}), 400

    message = data['message']
    alert_type = data.get('alert_type', 'info')

    icon = {
        'critical': '🚨',
        'warning': '⚠️',
        'info': 'ℹ️',
        'success': '✅'
    }.get(alert_type, '🔔')

    formatted_msg = (
        f"{icon} *{alert_type.upper()} ALERT*\n\n"
        f"{message}\n\n"
        f"*Time*: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    )

    results = {}
    chat_ids = get_all_chat_ids_from_db()
    for chat_id in chat_ids:
        response = send_telegram_message(chat_id, formatted_msg)
        results[chat_id] = "success" if response else "failed"

    return jsonify({
        "status": "completed",
        "results": results,
        "success_count": sum(1 for r in results.values() if r == "success"),
        "total_chats": len(chat_ids)
    })


@app.route('/api/telegram/chat_ids', methods=['GET'])
def get_chat_ids():
    return jsonify({
        "chat_ids": get_all_chat_ids_from_db(),
        "count": len(get_all_chat_ids_from_db())
    })


# Вебхук для внешних сервисов
@app.route('/api/webhook', methods=['POST'])
def webhook():
    try:
        data = request.get_json()

        alert_type = data.get('alert_type', 'info')
        service_name = data.get('service_name', 'Unknown')
        message = data.get('message', 'No details provided')

        alert_msg = (
            f"{'🚨' if alert_type == 'critical' else '⚠️'} *{alert_type.upper()}*\n\n"
            f"*Service*: {service_name}\n"
            f"*Message*: {message}\n\n"
            f"*Time*: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        )

        results = {}
        chat_ids = get_all_chat_ids_from_db()
        for chat_id in chat_ids:
            response = send_telegram_message(chat_id, alert_msg)
            results[chat_id] = "success" if response else "failed"

        return jsonify({
            "status": "alert_sent",
            "results": results,
            "success_count": sum(1 for r in results.values() if r == "success"),
            "total_chats": len(chat_ids)
        }), 200

    except Exception as e:
        error_msg = f"⚠️ Webhook processing error: {str(e)}"
        print(error_msg)
        # Отправка ошибки администратору
        admin_chat_ids = get_all_chat_ids_from_db()
        for chat_id in admin_chat_ids:
            send_telegram_message(chat_id, error_msg)
        return jsonify({"error": str(e)}), 500


# Обработчики ошибок
@app.errorhandler(401)
def unauthorized(error):
    return jsonify({
        "status": "error",
        "message": error.description
    }), 401


@app.errorhandler(415)
def unsupported_media_type(error):
    return jsonify({
        "status": "error",
        "message": error.description
    }), 415


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
