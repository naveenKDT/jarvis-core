import requests
import time


class LocalLLM:

    def __init__(self):
        self.url = "http://localhost:11434/api/chat"

    def ask(self, prompt):

        print("\n")
        print("=" * 60)
        print("[JARVIS] Sending request to Llama")
        print("=" * 60)

        start_time = time.time()

        payload = {
            "model": "llama3.1:8b",
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "stream": False
        }

        response = requests.post(
            self.url,
            json=payload,
            timeout=300
        )

        response.raise_for_status()

        data = response.json()

        elapsed = time.time() - start_time

        print(f"[JARVIS] Response received in {elapsed:.2f} seconds")

        return data["message"]["content"]