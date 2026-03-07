from interwiews.providers.base import AIProvider


def get_ai_provider() -> AIProvider:
    from interwiews.core.configuration import conf

    provider_name = conf.ai.provider.lower()

    match provider_name:
        case "openai":
            from interwiews.providers.openai import OpenAIProvider

            return OpenAIProvider(
                api_key=conf.ai.api_key,
                model=conf.ai.model or "gpt-4o-mini",
            )
        case "anthropic":
            from interwiews.providers.anthropic import AnthropicProvider

            return AnthropicProvider(
                api_key=conf.ai.api_key,
                model=conf.ai.model or "claude-haiku-4-5-20251001",
            )
        case "ollama":
            from interwiews.providers.ollama import OllamaProvider

            return OllamaProvider(
                base_url=conf.ai.base_url or "http://localhost:11434",
                model=conf.ai.model or "llama3",
            )
        case _:
            raise ValueError(f"Unknown AI provider: {provider_name!r}. Supported values: openai, anthropic, ollama")
