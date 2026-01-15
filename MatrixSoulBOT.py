import os
import requests
from flask import Flask, request

app = Flask(__name__)

TOKEN = os.getenv("BOT_TOKEN")
RENDER_URL = os.getenv("RENDER_EXTERNAL_URL")
TELEGRAM_API_URL = f"https://api.telegram.org/bot{TOKEN}"
CHANNEL_ID = "@your_channel_username"

user_states = {}

@app.route('/')
def home():
    return "OK", 200

@app.route(f'/{TOKEN}', methods=['POST'])
def webhook():
    data = request.get_json()
    if "message" in data:
        handle_message(data["message"])
    elif "callback_query" in data:
        handle_callback(data["callback_query"])
    return "ok", 200

def handle_message(message):
    chat_id = message["chat"]["id"]
    user_id = message["from"]["id"]
    text = message.get("text", "")

    if text == "/start":
        if check_sub(user_id):
            ask_birthday(chat_id)
        else:
            show_sub_menu(chat_id)
    elif user_states.get(chat_id) == "wait_date":
        user_states[chat_id] = {"date": text}
        show_calc_options(chat_id)

def handle_callback(callback):
    chat_id = callback["message"]["chat"]["id"]
    user_id = callback["from"]["id"]
    data = callback["data"]

    if data == "verify_sub":
        if check_sub(user_id):
            ask_birthday(chat_id)
        else:
            send_text(chat_id, "Ви не підписалися ❌")
    elif data == "free_calc":
        date = user_states.get(chat_id, {}).get("date", "Unknown")
        send_text(chat_id, f"Ваш результат для {date}: ...")
        show_share(chat_id)

def check_sub(user_id):
    url = f"{TELEGRAM_API_URL}/getChatMember?chat_id={CHANNEL_ID}&user_id={user_id}"
    try:
        r = requests.get(url).json()
        return r.get("ok") and r["result"]["status"] in ["member", "administrator", "creator"]
    except:
        return False

def show_sub_menu(chat_id):
    kb = {
        "inline_keyboard": [
            [{"text": "Підписатися", "url": f"https://t.me/{CHANNEL_ID[1:]}"}],
            [{"text": "Перевірити ✅", "callback_data": "verify_sub"}]
        ]
    }
    send_text(chat_id, "Підпишіться на канал для доступу:", kb)

def ask_birthday(chat_id):
    user_states[chat_id] = "wait_date"
    send_text(chat_id, "Введіть дату народження (ДД.ММ.РРРР):")

def show_calc_options(chat_id):
    kb = {
        "inline_keyboard": [
            [{"text": "Безкоштовний", "callback_data": "free_calc"}],
            [{"text": "Повний (Платний)", "url": "https://t.me/admin_username"}]
        ]
    }
    send_text(chat_id, "Оберіть тип розрахунку:", kb)

def show_share(chat_id):
    kb = {
        "inline_keyboard": [[{"text": "Поділитися 🚀", "url": "https://t.me/share/url?url=t.me/bot_user&text=Check this!"}]]
    }
    send_text(chat_id, "Поділіться результатом з другом:", kb)

def send_text(chat_id, text, markup=None):
    payload = {"chat_id": chat_id, "text": text}
    if markup: payload["reply_markup"] = markup
    requests.post(f"{TELEGRAM_API_URL}/sendMessage", json=payload)

def set_webhook():
    requests.get(f"{TELEGRAM_API_URL}/setWebhook?url={RENDER_URL}/{TOKEN}")

if __name__ == '__main__':
    set_webhook()
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))