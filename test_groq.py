import httpx, os
r = httpx.post(
    "https://api.groq.com/openai/v1/chat/completions",
    headers={"Authorization": f"Bearer {os.environ['GROQ_API_KEY']}"},
    json={"model": "llama-3.3-70b-versatile", "max_tokens": 50,
          "messages": [{"role": "user", "content": "Dis bonjour en 5 mots"}]},
    timeout=10,
)
print(r.json()["choices"][0]["message"]["content"])
