import requests


class OllamaChat:
    def __init__(self, model: str, url: str):
        self.model = model
        self.url = url
        self.messages = []  # conversation history

    def ask(self, user_text: str) -> str:
        # add user message to history
        self.messages.append({
            "role": "user",
            "content": user_text
        })

        payload = {
            "model": self.model,
            "messages": self.messages,
            "stream": False
        }

        response = requests.post(self.url, json=payload, timeout=120)
        response.raise_for_status()

        data = response.json()

        # expected shape:
        # {
        #   "message": {
        #       "role": "assistant",
        #       "content": "..."
        #   }
        # }
        message = data.get("message", {})
        content = message.get("content", "").strip()

        if content:
            # add assistant reply to history
            self.messages.append({
                "role": "assistant",
                "content": content
            })
            return content

        # fallback if something weird comes back
        return str(data)