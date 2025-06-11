import os

from openai import OpenAI

from dotenv import load_dotenv

# Go up one directory to load the shared root-level .env
env_path = os.path.join(os.path.dirname(__file__), "../.env")
load_dotenv(dotenv_path=env_path)

class OpenAIClient:
    _client = None

    @classmethod
    def get_client(cls) -> OpenAI:
        if cls._client is None:
            cls._client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])
        return cls._client

    @classmethod
    def call(cls, prompt: str, model: str = "gpt-4o", retries: int = 2, temperature: float = 0.0) -> str | None:
        client = cls.get_client()
        for attempt in range(retries):
            try:
                response = client.chat.completions.create(
                    model=model,
                    temperature=temperature,
                    messages=[
                        {"role": "system", "content": "You are a precise linguistic assistant."},
                        {"role": "user", "content": prompt}
                    ]
                )
                return response.choices[0].message.content.strip()
            except Exception as e:
                print(f"[Attempt {attempt+1}] OpenAI API error: {e}")
                time.sleep(1)
        return None