import os
import requests
from flask import Flask, request

app = Flask(__name__)


TOKEN = os.getenv("BOT_TOKEN")

RENDER_URL = os.getenv("RENDER_EXTERNAL_URL")
TELEGRAM_API_URL = f"https://api.telegram.org/bot{TOKEN}"


@app.route('/')
def home():
    return "Бот активний та працює!", 200


@app.route(f'/{TOKEN}', methods=['POST'])
def webhook():
    data = request.get_json()

    if "message" in data:
        chat_id = data["message"]["chat"]["id"]
        text = data["message"].get("text", "")

        reply = f"Ви сказали: {text}"

        send_message(chat_id, reply)

    return "ok", 200


def send_message(chat_id, text):
    url = f"{TELEGRAM_API_URL}/sendMessage"
    payload = {"chat_id": chat_id, "text": text}
    try:
        requests.post(url, json=payload)
    except Exception as e:
        print(f"Помилка відправки: {e}")


def set_webhook():
    if not TOKEN or not RENDER_URL:
        print("ПОМИЛКА: Перевірте змінні оточення BOT_TOKEN та RENDER_EXTERNAL_URL")
        return

    webhook_url = f"{RENDER_URL}/{TOKEN}"
    url = f"{TELEGRAM_API_URL}/setWebhook?url={webhook_url}"

    response = requests.get(url)
    if response.status_code == 200:
        print(f"Вебхук успішно встановлено: {webhook_url}")
    else:
        print(f"Помилка встановлення вебхука: {response.text}")


if __name__ == '__main__':
    set_webhook()

    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)