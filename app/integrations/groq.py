
import json
import requests

from app.config import settings


class GroqIntegration:
    def __init__(self):
        self.api_key = settings.groq_api_key
        self.base_url = "https://api.groq.com/openai/v1"

        if not self.api_key:
            raise ValueError("GROQ_API_KEY is missing")

    def _chat(
        self,
        messages,
        model=None,
        temperature=0.7,
        max_tokens=3000,
        response_format=None,
    ):
        url = f"{self.base_url}/chat/completions"

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        payload = {
            "model": model or settings.groq_model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }

        if response_format:
            payload["response_format"] = response_format

        try:
            response = requests.post(
                url,
                headers=headers,
                json=payload,
                timeout=120,
            )
            response.raise_for_status()

        except requests.RequestException as error:
            detail = ""
            if error.response is not None:
                detail = error.response.text

            raise RuntimeError(
                f"Groq API request failed: {error}. {detail}"
            ) from error

        data = response.json()

        try:
            return data["choices"][0]["message"]["content"]
        except (KeyError, IndexError, TypeError) as error:
            raise RuntimeError(
                f"Unexpected Groq response: {data}"
            ) from error

    def generate(
        self,
        messages,
        model=None,
        temperature=0.7,
        max_tokens=8192,
    ):
        return self._chat(
            messages=messages,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
        )

    def complete_json(self, system, prompt):
        messages = [
            {"role": "system", "content": system},
            {"role": "user", "content": prompt},
        ]

        content = self._chat(
            messages=messages,
            temperature=0.4,
            max_tokens=8192,
            response_format={"type": "json_object"},
        )

        try:
            result = json.loads(content)
        except json.JSONDecodeError as error:
            raise ValueError(
                f"Groq returned invalid JSON: {content[:1000]}"
            ) from error

        if not isinstance(result, dict):
            raise ValueError("Groq JSON response must be an object")

        return result


# Keep compatibility with existing application agents.
GroqClient = GroqIntegration
