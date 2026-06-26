import requests
from .core.config import settings
from .core.logger import logger


GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"


def call_openai(prompt: str):

    headers = {
        "Authorization": f"Bearer {settings.GROQ_API_KEY}",
        "Content-Type": "application/json",
    }

    payload = {
        "model": "llama-3.3-70b-versatile",
        "messages": [
            {
                "role": "user",
                "content": prompt
            }
        ],
        "temperature": 0.5,
    }

    try:

        response = requests.post(
            GROQ_URL,
            headers=headers,
            json=payload,
            timeout=60
        )

        if response.status_code != 200:

            logger.error(
                f"GROQ API ERROR: {response.text}"
            )

            response.raise_for_status()

        data = response.json()

        return data["choices"][0]["message"]["content"]

    except Exception as e:

        logger.exception(
            f"LLM CALL FAILED: {str(e)}"
        )

        raise Exception(
            "AI service temporarily unavailable."
        )