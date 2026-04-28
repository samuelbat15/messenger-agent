from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import PlainTextResponse
import httpx
import os
from anthropic import Anthropic

app = FastAPI(title="Messenger Agent")
client = Anthropic()

FB_VERIFY_TOKEN = os.environ["FB_VERIFY_TOKEN"]
FB_PAGE_TOKEN = os.environ["FB_PAGE_TOKEN"]


@app.get("/webhook")
async def verify(hub_mode: str = None, hub_challenge: str = None, hub_verify_token: str = None):
    if hub_mode == "subscribe" and hub_verify_token == FB_VERIFY_TOKEN:
        return PlainTextResponse(hub_challenge)
    raise HTTPException(status_code=403)


@app.post("/webhook")
async def webhook(request: Request):
    body = await request.json()
    for entry in body.get("entry", []):
        for event in entry.get("messaging", []):
            sender_id = event["sender"]["id"]
            text = event.get("message", {}).get("text", "")
            if text:
                reply = await generate_reply(text)
                await send_message(sender_id, reply)
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


async def send_message(recipient_id: str, text: str):
    async with httpx.AsyncClient() as http:
        await http.post(
            "https://graph.facebook.com/v21.0/me/messages",
            params={"access_token": FB_PAGE_TOKEN},
            json={"recipient": {"id": recipient_id}, "message": {"text": text}},
        )
