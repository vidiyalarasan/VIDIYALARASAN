import requests
import json

API_KEY = "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"
URL = "https://openrouter.ai/api/v1/chat/completions"

headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

while True:
    msg = input("You: ")

    if msg.lower() == "bye":
        print("AI: Bye! Have a great day!")
        break

    payload = {
        "model": "openai/gpt-3.5-turbo",
        "messages": [
            {"role": "user", "content": msg}
        ]
    }

    r = requests.post(URL, headers=headers, json=payload)
    result = r.json()

    print("AI:", result["choices"][0]["message"]["content"])
