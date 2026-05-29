import json

from app.core.llm import LocalLLM


class Planner:

    def __init__(self):
        self.llm = LocalLLM()

    def create_plan(self, user_request):

        prompt = f"""
You are Jarvis Planner.

User Request:

{user_request}

Available Agents:

- website
- coding
- file
- browser
- device

Return ONLY JSON.

Example:

{{
    "agent":"website"
}}
"""

        response = self.llm.ask(prompt)

        try:
            return json.loads(response)
        except:
            return {
                "agent": "unknown"
            }