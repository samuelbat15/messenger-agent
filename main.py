from fastapi import FastAPI, Request
from anthropic import Anthropic
import httpx
import os

app = FastAPI(title="Telegram Agent")
client = Anthropic()

BOT_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
TELEGRAM_API = f"https://api.telegram.org/bot{BOT_TOKEN}"


@app.post("/webhook")
async def webhook(request: Request):
    body = await request.json()
    message = body.get("message", {})
    chat_id = message.get("chat", {}).get("id")
    text = message.get("text", "")
    if chat_id and text:
        reply = await generate_reply(text)
        await send_message(chat_id, reply)
    return {"status": "ok"}


async def generate_reply(user_message: str) -> str:
    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=300,
        system=(
            "Tu es un assistant pour une PME locale. "
            "Réponds de façon concise, chaleureuse et professionnelle. "
            "Pour les réservations, demande : nom, date, heure, nombre de personnes."
        ),
        messages=[{"role": "user", "content": user_message}],
    )
    return response.content[0].text


async def send_message(chat_id: int, text: str):
    async with httpx.AsyncClient() as http:
        await http.post(
            f"{TELEGRAM_API}/sendMessage",
            json={"chat_id": chat_id, "text": text},
        )


@app.on_event("startup")
async def set_webhook():
    url = os.environ.get("WEBHOOK_URL", "")
    if url:
        async with httpx.AsyncClient() as http:
            await http.post(
                f"{TELEGRAM_API}/setWebhook",
                json={"url": f"{url}/webhook"},
            )
