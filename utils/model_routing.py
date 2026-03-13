import os
from typing import Dict

# Explicit endpoint-to-model-env routing from main.py.
# Values are ENV variable names so model names stay configurable in .env.
ENDPOINT_MODEL_ENV: Dict[str, str] = {
    # Document extraction endpoints
    "/extract/pan": "OLLAMA_MODEL",
    "/extract/aadhaar": "OLLAMA_MODEL",
    "/extract/loan": "OLLAMA_MODEL",
    "/extract/passport": "OLLAMA_MODEL",
    "/extract/driving-license": "OLLAMA_MODEL",
    "/extract/voter-id": "OLLAMA_MODEL",
    "/extract/text/handwritten_text": "OLLAMA_MODEL",
    "/extract/text/digital_text": "OLLAMA_MODEL_TEXT_EXTRACTION",
    "/extract/text/miscellaneous_text": "OLLAMA_MODEL_TEXT_EXTRACTION",
    "/extract/account-opening/page1": "OLLAMA_MODEL",
    "/extract/account-opening/page2": "OLLAMA_MODEL",

    # Retrieval endpoints (no model call today, listed for completeness)
    "/retrieve/pan/all": "OLLAMA_MODEL",
    "/retrieve/aadhaar/all": "OLLAMA_MODEL",
    "/retrieve/text/handwritten_text/all": "OLLAMA_MODEL",
    "/retrieve/text/digital_text/all": "OLLAMA_MODEL_TEXT_EXTRACTION",
    "/retrieve/text/miscellaneous_text/all": "OLLAMA_MODEL_TEXT_EXTRACTION",
}


def get_model_for_endpoint(api_endpoint: str, default_model: str) -> str:
    """Return endpoint-specific model if configured, otherwise fallback to default model."""
    env_name = ENDPOINT_MODEL_ENV.get(api_endpoint)
    if not env_name:
        return default_model

    model_name = os.getenv(env_name, "").strip()
    return model_name or default_model
