import json
from typing import Optional, Dict, Any, List
from config import config

try:
    from openai import OpenAI
except ImportError:
    OpenAI = None

class LLMClient:
    """
    Unified LLM Client that supports OpenAI, Ollama (via OpenAI compatible endpoint), and Mock mode.
    """
    def __init__(self):
        self.provider = config.llm_provider
        self.model = config.llm_model
        self.client = None

        if self.provider in ["openai", "ollama"]:
            if OpenAI is None:
                raise ImportError("openai package is required for OpenAI and Ollama providers. Run: pip install openai")
            
            if self.provider == "openai":
                # For OpenAI, use provided key and base URL (if any)
                api_key = config.openai_api_key
                if not api_key:
                    # Some compatible endpoints don't need a real key, but OpenAI sdk requires something
                    api_key = "dummy-key-if-not-set"
                
                self.client = OpenAI(
                    api_key=api_key,
                    base_url=config.openai_base_url
                )
            elif self.provider == "ollama":
                # Ollama exposes an OpenAI compatible API at /v1
                base_url = config.ollama_base_url
                if not base_url.endswith("/v1"):
                    base_url = f"{base_url.rstrip('/')}/v1"
                
                self.client = OpenAI(
                    api_key="ollama", # Key is ignored by Ollama
                    base_url=base_url
                )

    def chat(
        self, 
        prompt: str, 
        system_prompt: str = "You are a helpful AI assistant.", 
        json_mode: bool = False,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        model_override: Optional[str] = None
    ) -> str:
        """
        Send a chat completion request to the configured LLM provider.
        Supports dynamic parameter overrides (the Spice pattern).
        """
        if self.provider == "mock":
            return self._mock_chat(prompt, json_mode)
            
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt}
        ]

        kwargs = {
            "model": model_override or self.model,
            "messages": messages,
        }
        
        if temperature is not None:
            kwargs["temperature"] = temperature
            
        if max_tokens is not None:
            kwargs["max_tokens"] = max_tokens

        # Handle JSON mode if requested and supported
        if json_mode:
            kwargs["response_format"] = {"type": "json_object"}

        try:
            response = self.client.chat.completions.create(**kwargs)
            return response.choices[0].message.content
        except Exception as e:
            print(f"[LLMClient] Error calling {self.provider} API: {e}")
            raise  # Do not fallback here if we want strict failure handling

    def _mock_chat(self, prompt: str, json_mode: bool) -> str:
        """Mock implementation for testing and fallback."""
        if json_mode:
            return json.dumps({
                "reasoning": "Mock evaluation complete. Selected the first available option based on mock criteria.",
                "confidence": 0.95,
                "selected_option_id": "option_1"
            })
        return f"Mock response to: {prompt[:50]}..."

# Global instance for easy importing
llm = LLMClient()
