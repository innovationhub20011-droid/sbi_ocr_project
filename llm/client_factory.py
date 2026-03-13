from functools import lru_cache

from langchain_ollama import ChatOllama

from config.ollama_settings import load_ollama_settings


_settings = load_ollama_settings()

_base_llm_config = {
    "temperature": _settings.temperature,
    "num_predict": _settings.num_predict,
    "repeat_penalty": _settings.repeat_penalty,
    "repeat_last_n": _settings.repeat_last_n,
}

if _settings.base_url:
    _base_llm_config["base_url"] = _settings.base_url


@lru_cache(maxsize=16)
def get_json_client(model_name: str) -> ChatOllama:
    return ChatOllama(
        **{
            **_base_llm_config,
            "model": model_name,
        },
        format="json"
    )


@lru_cache(maxsize=16)
def get_raw_client(model_name: str) -> ChatOllama:
    return ChatOllama(
        **{
            **_base_llm_config,
            "model": model_name,
            "num_predict": _settings.raw_num_predict,
        }
    )
