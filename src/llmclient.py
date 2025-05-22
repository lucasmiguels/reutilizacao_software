from openai import OpenAI
import requests


LLM_PROVIDERS = {}

def llm_provider(name: str):
    def wrapper(cls):
        LLM_PROVIDERS[name.lower()] = cls()
        return cls
    return wrapper


@llm_provider("openai")
class OpenAILLM:
    def build(self, api_key: str, base_url: str, model: str, temperature: float, **kwargs):
        client = OpenAI(api_key=api_key, base_url=base_url)

        def call(prompt: str) -> str:
            response = client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                temperature=temperature
            )
            return response.choices[0].message.content.strip()

        return call


@llm_provider("ollama")
class OllamaLLM:
    def build(self, model: str, host: str = "http://localhost:11434", **kwargs):
        def call(prompt: str) -> str:
            response = requests.post(
                f"{host}/api/chat",
                json={
                    "model": model,
                    "messages": [{"role": "user", "content": prompt}],
                    "stream": False
                }
            )
            response.raise_for_status()
            return response.json()["message"]["content"].strip()

        return call

@llm_provider("stub")
class StubLLM:
    def build(self, **kwargs):
        def call(prompt: str) -> str:
            print(f"[STUB] Prompt: {prompt[:80]}...")
            return "Inválido"
        return call


def get_llm_call_fn(provider: str, **kwargs):
    provider = provider.lower()
    if provider not in LLM_PROVIDERS:
        raise ValueError(f"LLM provider '{provider}' não registrado.")
    factory = LLM_PROVIDERS[provider]
    return factory.build(**kwargs)