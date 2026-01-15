import os
import requests
from flask import Flask, request

app = Flask(__name__)

TOKEN = os.getenv("BOT_TOKEN")
RENDER_URL = os.getenv("RENDER_EXTERNAL_URL")
API_URL = f"https://api.telegram.org/bot{TOKEN}"

user_states = {}


@app.route('/')
def home():
    return "OK", 200


@app.route(f'/{TOKEN}', methods=['POST'])
def webhook():
    data = request.get_json()
    if not data:
        return "ok", 200

    if "message" in data:
        m = data["message"]
        cid = m["chat"]["id"]
        txt = m.get("text", "")

        if txt == "/start":
            user_states[cid] = "waiting_date"
            send_text(cid, "Привіт! 🔮 Введи дату народження (наприклад: 15.05.1995):")
        elif user_states.get(cid) == "waiting_date":
            user_states[cid] = {"date": txt}
            show_options(cid)

    elif "callback_query" in data:
        handle_callback(data["callback_query"])

    return "ok", 200


def handle_callback(cb):
    cid = cb["message"]["chat"]["id"]
    if cb["data"] == "free_calc":
        u = user_states.get(cid, {})
        d = u.get("date", "---")
        send_text(cid, f"✨ Результат для {d}: Ви маєте потужну енергію!")
        show_share(cid)


def show_options(cid):
    kb = {"inline_keyboard": [
        [{"text": "Безкоштовний", "callback_data": "free_calc"}],
        [{"text": "Платний", "url": "https://t.me/your_admin"}]
    ]}
    send_text(cid, "Обери тип:", kb)


def show_share(cid):
    kb = {"inline_keyboard": [
        [{"text": "Поділитися 🚀", "url": "https://t.me/share/url?url=t.me/MatrixSoulBot&text=Дізнайся долю!"}]
    ]}
    send_text(cid, "Сподобалось?", kb)


def send_text(cid, txt, kb=None):
    if not TOKEN: return
    p = {"chat_id": cid, "text": txt}
    if kb: p["reply_markup"] = kb
    requests.post(f"{API_URL}/sendMessage", json=p)


def set_webhook():
    if TOKEN and RENDER_URL:
        requests.get(f"{API_URL}/setWebhook?url={RENDER_URL}/{TOKEN}")


if __name__ == '__main__':
    set_webhook()
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))