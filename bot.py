import os
import time
import httpx

BOT_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
GROQ_API_KEY = os.environ["GROQ_API_KEY"]
TELEGRAM_API = f"https://api.telegram.org/bot{BOT_TOKEN}"
offset = 0


def get_updates():
    global offset
    r = httpx.get(f"{TELEGRAM_API}/getUpdates", params={"offset": offset, "timeout": 30}, timeout=35)
    return r.json().get("result", [])


def send_message(chat_id, text):
    httpx.post(f"{TELEGRAM_API}/sendMessage", json={"chat_id": chat_id, "text": text})


def generate_reply(text):
    r = httpx.post(
        "https://api.groq.com/openai/v1/chat/completions",
        headers={"Authorization": f"Bearer {GROQ_API_KEY}"},
        json={
            "model": "llama-3.3-70b-versatile",
            "max_tokens": 300,
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "Tu es un assistant pour une PME locale. "
                        "Réponds de façon concise, chaleureuse et professionnelle. "
                        "Pour les réservations, demande : nom, date, heure, nombre de personnes."
                    ),
                },
                {"role": "user", "content": text},
            ],
        },
        timeout=15,
    )
    return r.json()["choices"][0]["message"]["content"]


def main():
    global offset
    print("Bot démarré — en attente de messages...")
    while True:
        updates = get_updates()
        for update in updates:
            offset = update["update_id"] + 1
            msg = update.get("message", {})
            chat_id = msg.get("chat", {}).get("id")
            text = msg.get("text", "")
            if chat_id and text:
                print(f"Message reçu: {text}")
                reply = generate_reply(text)
                send_message(chat_id, reply)
                print(f"Répondu: {reply[:60]}...")
        time.sleep(1)


if __name__ == "__main__":
    main()
