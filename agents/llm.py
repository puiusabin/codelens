# agents/llm.py
from config import load_config

_DEFAULT_MODELS = {
    "ollama": "gemma2",
    "openai": "gpt-4o",
    "anthropic": "claude-sonnet-4-6",
}


def _get_config() -> tuple[str, str, str | None]:
    config = load_config()
    backend = config.get("ai_backend", "ollama")
    model = config.get("ai_model", _DEFAULT_MODELS.get(backend, "gemma2"))
    api_key = config.get("ai_api_key")
    return backend, model, api_key


def chat(system_prompt: str, user_content: str) -> str:
    backend, model, api_key = _get_config()
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_content},
    ]

    if backend == "ollama":
        import ollama
        response = ollama.chat(model=model, messages=messages)
        return response["message"]["content"]

    if backend == "openai":
        from openai import OpenAI
        client = OpenAI(api_key=api_key)
        response = client.chat.completions.create(model=model, messages=messages)
        return response.choices[0].message.content

    if backend == "anthropic":
        import anthropic
        client = anthropic.Anthropic(api_key=api_key)
        response = client.messages.create(
            model=model,
            max_tokens=8192,
            system=system_prompt,
            messages=[{"role": "user", "content": user_content}],
        )
        return response.content[0].text

    raise ValueError(f"Unknown backend: {backend!r}")


def chat_messages(messages: list[dict]) -> str:
    backend, model, api_key = _get_config()

    if backend == "ollama":
        import ollama
        response = ollama.chat(model=model, messages=messages)
        return response["message"]["content"]

    if backend == "openai":
        from openai import OpenAI
        client = OpenAI(api_key=api_key)
        response = client.chat.completions.create(model=model, messages=messages)
        return response.choices[0].message.content

    if backend == "anthropic":
        import anthropic
        client = anthropic.Anthropic(api_key=api_key)
        system = ""
        user_messages = []
        for msg in messages:
            if msg["role"] == "system":
                system = msg["content"]
            else:
                user_messages.append(msg)
        response = client.messages.create(
            model=model,
            max_tokens=8192,
            system=system,
            messages=user_messages,
        )
        return response.content[0].text

    raise ValueError(f"Unknown backend: {backend!r}")
