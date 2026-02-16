# backend/app/llm_client.py

import os
from dotenv import load_dotenv

# Try to import Groq client
try:
    from groq import Groq
except ImportError:
    Groq = None  # type: ignore

# Load variables from .env
load_dotenv()

# We'll create the client lazily so the app doesn't crash at import time
_client = None


def get_client():
    """
    Lazily create and return a global Groq client.
    This avoids crashing the app at import time if the key or package is missing.
    """
    global _client
    if _client is None:
        if Groq is None:
            raise RuntimeError(
                "The 'groq' package is not installed.\n"
                "Install it inside your virtualenv with:\n"
                "    pip install groq"
            )
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise RuntimeError(
                "GROQ_API_KEY is not set.\n"
                "Create a .env file in your project root with a line like:\n"
                "    GROQ_API_KEY=gsk_your_real_groq_key_here"
            )
        _client = Groq(api_key=api_key)
    return _client


def call_openai(prompt: str) -> str:
    """
    Sends the prompt to a Groq LLaMA model and returns the reply.
    We keep the function name 'call_openai' so the rest of your code works unchanged.
    """
    try:
        client = get_client()
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",  # free + fast Groq model
            messages=[
                {"role": "user", "content": prompt}
            ],
            max_tokens=700,
            temperature=0.2,
        )
        return response.choices[0].message.content

    except Exception as e:
        print("LLM Error (Groq):", e)
        # Return a readable error string so frontend can show something
        return f"Error contacting LLM: {e}"


# Backwards-compatible alias
def call_llm(prompt: str) -> str:
    return call_openai(prompt)
