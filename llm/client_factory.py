from functools import lru_cache

from langchain_ollama import ChatOllama

from config.ollama_settings import load_ollama_settings


_settings = load_ollama_settings()

llm_config = {
    "model": _settings.model,
    "temperature": _settings.temperature,
    "num_predict": _settings.num_predict,
}


@lru_cache(maxsize=16)
def get_llm_client(model_name: str, isjson: bool = False) -> ChatOllama:
    return ChatOllama(
        base_url=_settings.base_url,
        **{
            **llm_config,
            "model": model_name,
        },
        format="json" if isjson else "",
    )

