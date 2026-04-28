import os
import time
import httpx
from anthropic import Anthropic

BOT_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
ANTHROPIC_API_KEY = os.environ["ANTHROPIC_API_KEY"]
TELEGRAM_API = f"https://api.telegram.org/bot{BOT_TOKEN}"

client = Anthropic(api_key=ANTHROPIC_API_KEY)
offset = 0


def get_updates():
    global offset
    r = httpx.get(f"{TELEGRAM_API}/getUpdates", params={"offset": offset, "timeout": 30})
    return r.json().get("result", [])


def send_message(chat_id, text):
    httpx.post(f"{TELEGRAM_API}/sendMessage", json={"chat_id": chat_id, "text": text})


def generate_reply(text):
    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=300,
        system=(
            "Tu es un assistant pour une PME locale. "
            "Réponds de façon concise, chaleureuse et professionnelle. "
            "Pour les réservations, demande : nom, date, heure, nombre de personnes."
        ),
        messages=[{"role": "user", "content": text}],
    )
    return response.content[0].text


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
