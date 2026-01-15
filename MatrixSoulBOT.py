import os
import requests
from flask import Flask, request

app = Flask(__name__)

TOKEN = os.getenv("BOT_TOKEN")
RENDER_URL = os.getenv("RENDER_EXTERNAL_URL")
API_URL = f"https://api.telegram.org/bot{TOKEN}"

user_states = {}

def reduce_to_22(n):
    while n > 22:
        n = sum(int(d) for d in str(n))
    return n

def calculate_matrix(date_str):
    try:
        parts = date_str.replace('.', ' ').replace('/', ' ').split()
        if len(parts) != 3: return None
        day = reduce_to_22(int(parts[0]))
        month = reduce_to_22(int(parts[1]))
        year = reduce_to_22(int(parts[2]))
        center = reduce_to_22(day + month + year)
        return {"day": day, "month": month, "year": year, "center": center}
    except:
        return None

@app.route('/')
def home():
    return "OK", 200

@app.route(f'/{TOKEN}', methods=['POST'])
def webhook():
    data = request.get_json()
    if not data or "message" not in data: return "ok", 200
    m = data["message"]
    cid = m["chat"]["id"]
    txt = m.get("text", "")

    if txt == "/start":
        user_states[cid] = "wait_date"
        send_text(cid, "🔮 Вітаю! Я допоможу розрахувати твою Матрицю Долі.\n\nВведи дату народження (наприклад: 15.05.1995):")
    elif user_states.get(cid) == "wait_date":
        matrix = calculate_matrix(txt)
        if matrix:
            user_states[cid] = {"matrix": matrix, "date": txt}
            show_options(cid)
        else:
            send_text(cid, "❌ Неправильний формат. Спробуйте ще раз (ДД.ММ.РРРР):")
    elif "callback_query" in data:
        handle_callback(data["callback_query"])
    return "ok", 200

def handle_callback(cb):
    cid = cb["message"]["chat"]["id"]
    if cb["data"] == "free_calc":
        u = user_states.get(cid, {})
        m = u.get("matrix")
        if m:
            res = (f"✨ Твоя Матриця ({u['date']}):\n\n"
                   f"💎 Особистість: {m['day']} аркан\n"
                   f"🌌 Таланти: {m['month']} аркан\n"
                   f"💰 Карма: {m['year']} аркан\n"
                   f"🎯 Центр: {m['center']} аркан")
            send_text(cid, res)
            show_share(cid)

def show_options(cid):
    kb = {"inline_keyboard": [
        [{"text": "Безкоштовний розрахунок", "callback_data": "free_calc"}],
        [{"text": "Повний розбір (Платний)", "url": "https://t.me/your_admin"}]
    ]}
    send_text(cid, "Оберіть варіант:", kb)

def show_share(cid):
    kb = {"inline_keyboard": [[{"text": "Поділитися 🚀", "url": "https://t.me/share/url?url=t.me/MatrixSoulBot&text=Дізнайся долю!"}]]}
    send_text(cid, "Сподобався результат?", kb)

def send_text(cid, txt, kb=None):
    p = {"chat_id": cid, "text": txt}
    if kb: p["reply_markup"] = kb
    requests.post(f"{API_URL}/sendMessage", json=p)

if __name__ == '__main__':
    if TOKEN and RENDER_URL:
        requests.get(f"{API_URL}/setWebhook?url={RENDER_URL}/{TOKEN}")
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))