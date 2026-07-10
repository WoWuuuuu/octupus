from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from datetime import datetime
from enum import Enum


class LLMProviderType(Enum):
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    GOOGLE = "google"
    MOCK = "mock"


class ChatRole(Enum):
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"
    TOOL = "tool"


@dataclass
class ChatMessage:
    role: ChatRole
    content: str
    name: Optional[str] = None
    tool_calls: Optional[List[Dict]] = None
    tool_call_id: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        data = {"role": self.role.value, "content": self.content}
        if self.name:
            data["name"] = self.name
        if self.tool_calls:
            data["tool_calls"] = self.tool_calls
        if self.tool_call_id:
            data["tool_call_id"] = self.tool_call_id
        return data


@dataclass
class LLMResponse:
    content: str
    model: str
    provider: str
    usage: Optional[Dict[str, int]] = None
    finish_reason: Optional[str] = None
    tool_calls: Optional[List[Dict]] = None
    error: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "content": self.content,
            "model": self.model,
            "provider": self.provider,
            "usage": self.usage,
            "finish_reason": self.finish_reason,
            "tool_calls": self.tool_calls,
            "error": self.error,
            "timestamp": self.timestamp.isoformat(),
        }


@dataclass
class LLMConfig:
    provider_type: LLMProviderType
    api_key: Optional[str] = None
    base_url: Optional[str] = None
    model: str = "default"
    temperature: float = 0.7
    max_tokens: int = 4096
    timeout_seconds: int = 60
    max_retries: int = 3
    top_p: float = 1.0
    frequency_penalty: float = 0.0
    presence_penalty: float = 0.0
    system_prompt: Optional[str] = None
    environment: Dict[str, str] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "provider_type": self.provider_type.value,
            "api_key": "***" if self.api_key else None,
            "base_url": self.base_url,
            "model": self.model,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            "timeout_seconds": self.timeout_seconds,
            "max_retries": self.max_retries,
            "top_p": self.top_p,
            "frequency_penalty": self.frequency_penalty,
            "presence_penalty": self.presence_penalty,
            "system_prompt": self.system_prompt,
        }


class BaseLLMProvider(ABC):
    def __init__(self, config: LLMConfig):
        self.config = config
        self._client = None
        self._init_client()

    @abstractmethod
    def _init_client(self):
        pass

    @abstractmethod
    def chat(self, messages: List[ChatMessage]) -> LLMResponse:
        pass

    @abstractmethod
    def complete(self, prompt: str) -> LLMResponse:
        pass

    @abstractmethod
    def embeddings(self, text: str) -> List[float]:
        pass

    @abstractmethod
    def health_check(self) -> Dict[str, Any]:
        pass

    def get_config(self) -> LLMConfig:
        return self.config

    def get_provider_name(self) -> str:
        return self.config.provider_type.value


class MockLLMProvider(BaseLLMProvider):
    def _init_client(self):
        self._client = "mock"

    def chat(self, messages: List[ChatMessage]) -> LLMResponse:
        return LLMResponse(
            content="This is a mock response for testing purposes.",
            model=self.config.model,
            provider="mock",
            usage={"prompt_tokens": len(str(messages)), "completion_tokens": 50, "total_tokens": 50},
            finish_reason="stop",
        )

    def complete(self, prompt: str) -> LLMResponse:
        return LLMResponse(
            content="This is a mock completion response.",
            model=self.config.model,
            provider="mock",
            usage={"prompt_tokens": len(prompt), "completion_tokens": 30, "total_tokens": 30},
            finish_reason="stop",
        )

    def embeddings(self, text: str) -> List[float]:
        return [0.1] * 768

    def health_check(self) -> Dict[str, Any]:
        return {"status": "healthy", "provider": "mock"}


class OpenAIProvider(BaseLLMProvider):
    def _init_client(self):
        try:
            import openai
            self._client = openai.OpenAI(
                api_key=self.config.api_key or os.environ.get("OPENAI_API_KEY"),
                base_url=self.config.base_url,
                timeout=self.config.timeout_seconds,
            )
        except ImportError:
            self._client = None

    def chat(self, messages: List[ChatMessage]) -> LLMResponse:
        if not self._client:
            return LLMResponse(
                content="",
                model=self.config.model,
                provider="openai",
                error="openai library not installed",
            )

        try:
            response = self._client.chat.completions.create(
                model=self.config.model,
                messages=[m.to_dict() for m in messages],
                temperature=self.config.temperature,
                max_tokens=self.config.max_tokens,
                top_p=self.config.top_p,
                frequency_penalty=self.config.frequency_penalty,
                presence_penalty=self.config.presence_penalty,
            )

            usage = response.usage
            return LLMResponse(
                content=response.choices[0].message.content or "",
                model=response.model,
                provider="openai",
                usage={
                    "prompt_tokens": usage.prompt_tokens,
                    "completion_tokens": usage.completion_tokens,
                    "total_tokens": usage.total_tokens,
                } if usage else None,
                finish_reason=response.choices[0].finish_reason,
                tool_calls=[tc.to_dict() for tc in response.choices[0].message.tool_calls] if response.choices[0].message.tool_calls else None,
            )
        except Exception as e:
            return LLMResponse(
                content="",
                model=self.config.model,
                provider="openai",
                error=str(e),
            )

    def complete(self, prompt: str) -> LLMResponse:
        messages = [ChatMessage(role=ChatRole.USER, content=prompt)]
        return self.chat(messages)

    def embeddings(self, text: str) -> List[float]:
        if not self._client:
            return []

        try:
            response = self._client.embeddings.create(
                model="text-embedding-3-small",
                input=text,
            )
            return response.data[0].embedding
        except Exception:
            return []

    def health_check(self) -> Dict[str, Any]:
        if not self._client:
            return {"status": "unhealthy", "error": "client not initialized"}

        try:
            self._client.models.list()
            return {"status": "healthy", "provider": "openai"}
        except Exception as e:
            return {"status": "unhealthy", "error": str(e)}


class AnthropicProvider(BaseLLMProvider):
    def _init_client(self):
        try:
            import anthropic
            self._client = anthropic.Anthropic(
                api_key=self.config.api_key or os.environ.get("ANTHROPIC_API_KEY"),
                timeout=self.config.timeout_seconds,
            )
        except ImportError:
            self._client = None

    def chat(self, messages: List[ChatMessage]) -> LLMResponse:
        if not self._client:
            return LLMResponse(
                content="",
                model=self.config.model,
                provider="anthropic",
                error="anthropic library not installed",
            )

        try:
            system_prompt = self.config.system_prompt or ""

            formatted_messages = []
            for msg in messages:
                if msg.role == ChatRole.SYSTEM:
                    system_prompt += msg.content
                else:
                    formatted_messages.append({"role": msg.role.value, "content": msg.content})

            response = self._client.messages.create(
                model=self.config.model or "claude-3-sonnet-20240229",
                messages=formatted_messages,
                system=system_prompt,
                temperature=self.config.temperature,
                max_tokens=self.config.max_tokens,
                top_p=self.config.top_p,
            )

            return LLMResponse(
                content=response.content[0].text if response.content else "",
                model=response.model,
                provider="anthropic",
                usage={
                    "input_tokens": response.usage.input_tokens,
                    "output_tokens": response.usage.output_tokens,
                    "total_tokens": response.usage.input_tokens + response.usage.output_tokens,
                },
                finish_reason=response.stop_reason,
            )
        except Exception as e:
            return LLMResponse(
                content="",
                model=self.config.model,
                provider="anthropic",
                error=str(e),
            )

    def complete(self, prompt: str) -> LLMResponse:
        messages = [ChatMessage(role=ChatRole.USER, content=prompt)]
        return self.chat(messages)

    def embeddings(self, text: str) -> List[float]:
        return [0.1] * 768

    def health_check(self) -> Dict[str, Any]:
        if not self._client:
            return {"status": "unhealthy", "error": "client not initialized"}

        try:
            self._client.models.list()
            return {"status": "healthy", "provider": "anthropic"}
        except Exception as e:
            return {"status": "unhealthy", "error": str(e)}


class GoogleProvider(BaseLLMProvider):
    def _init_client(self):
        try:
            import google.generativeai as genai
            genai.configure(
                api_key=self.config.api_key or os.environ.get("GOOGLE_API_KEY"),
            )
            self._client = genai
        except ImportError:
            self._client = None

    def chat(self, messages: List[ChatMessage]) -> LLMResponse:
        if not self._client:
            return LLMResponse(
                content="",
                model=self.config.model,
                provider="google",
                error="google-generativeai library not installed",
            )

        try:
            model = self._client.GenerativeModel(self.config.model or "gemini-1.5-pro")

            system_prompt = ""
            formatted_messages = []
            for msg in messages:
                if msg.role == ChatRole.SYSTEM:
                    system_prompt = msg.content
                elif msg.role == ChatRole.USER:
                    formatted_messages.append(msg.content)

            response = model.generate_content(
                formatted_messages,
                generation_config={
                    "temperature": self.config.temperature,
                    "max_output_tokens": self.config.max_tokens,
                    "top_p": self.config.top_p,
                },
            )

            return LLMResponse(
                content=response.text,
                model=self.config.model or "gemini-1.5-pro",
                provider="google",
                finish_reason=response.candidates[0].finish_reason if response.candidates else None,
            )
        except Exception as e:
            return LLMResponse(
                content="",
                model=self.config.model,
                provider="google",
                error=str(e),
            )

    def complete(self, prompt: str) -> LLMResponse:
        messages = [ChatMessage(role=ChatRole.USER, content=prompt)]
        return self.chat(messages)

    def embeddings(self, text: str) -> List[float]:
        if not self._client:
            return []

        try:
            model = self._client.GenerativeModel("text-embedding-004")
            response = model.generate_content(text)
            return response.embedding
        except Exception:
            return []

    def health_check(self) -> Dict[str, Any]:
        if not self._client:
            return {"status": "unhealthy", "error": "client not initialized"}

        try:
            self._client.list_models()
            return {"status": "healthy", "provider": "google"}
        except Exception as e:
            return {"status": "unhealthy", "error": str(e)}


class LLMProviderManager:
    def __init__(self):
        self.providers: Dict[str, BaseLLMProvider] = {}
        self.default_provider_id: Optional[str] = None

    def register_provider(self, provider: BaseLLMProvider) -> bool:
        provider_id = provider.get_provider_name()
        if provider_id in self.providers:
            return False
        self.providers[provider_id] = provider
        if not self.default_provider_id:
            self.default_provider_id = provider_id
        return True

    def get_provider(self, provider_id: Optional[str] = None) -> Optional[BaseLLMProvider]:
        if provider_id:
            return self.providers.get(provider_id)
        if self.default_provider_id:
            return self.providers.get(self.default_provider_id)
        return None

    def chat(self, messages: List[ChatMessage], provider_id: Optional[str] = None) -> LLMResponse:
        provider = self.get_provider(provider_id)
        if not provider:
            return LLMResponse(
                content="",
                model="unknown",
                provider="unknown",
                error="No provider available",
            )
        return provider.chat(messages)

    def complete(self, prompt: str, provider_id: Optional[str] = None) -> LLMResponse:
        provider = self.get_provider(provider_id)
        if not provider:
            return LLMResponse(
                content="",
                model="unknown",
                provider="unknown",
                error="No provider available",
            )
        return provider.complete(prompt)

    def embeddings(self, text: str, provider_id: Optional[str] = None) -> List[float]:
        provider = self.get_provider(provider_id)
        if not provider:
            return []
        return provider.embeddings(text)

    def list_providers(self) -> List[Dict[str, Any]]:
        return [
            {
                "id": provider.get_provider_name(),
                "config": provider.get_config().to_dict(),
                "health": provider.health_check(),
            }
            for provider in self.providers.values()
        ]

    def set_default_provider(self, provider_id: str) -> bool:
        if provider_id in self.providers:
            self.default_provider_id = provider_id
            return True
        return False

    def get_health_summary(self) -> Dict[str, Any]:
        health = {}
        for pid, provider in self.providers.items():
            health[pid] = provider.health_check()
        return health

    def create_provider(self, config: LLMConfig) -> BaseLLMProvider:
        provider_map = {
            LLMProviderType.MOCK: MockLLMProvider,
            LLMProviderType.OPENAI: OpenAIProvider,
            LLMProviderType.ANTHROPIC: AnthropicProvider,
            LLMProviderType.GOOGLE: GoogleProvider,
        }

        provider_class = provider_map.get(config.provider_type, MockLLMProvider)
        provider = provider_class(config)
        self.register_provider(provider)
        return provider

    def create_mock_provider(self) -> MockLLMProvider:
        config = LLMConfig(provider_type=LLMProviderType.MOCK)
        return self.create_provider(config)

    def create_openai_provider(self, api_key: Optional[str] = None, model: str = "gpt-4o-mini") -> OpenAIProvider:
        config = LLMConfig(
            provider_type=LLMProviderType.OPENAI,
            api_key=api_key,
            model=model,
        )
        return self.create_provider(config)

    def create_anthropic_provider(self, api_key: Optional[str] = None, model: str = "claude-3-sonnet-20240229") -> AnthropicProvider:
        config = LLMConfig(
            provider_type=LLMProviderType.ANTHROPIC,
            api_key=api_key,
            model=model,
        )
        return self.create_provider(config)

    def create_google_provider(self, api_key: Optional[str] = None, model: str = "gemini-1.5-pro") -> GoogleProvider:
        config = LLMConfig(
            provider_type=LLMProviderType.GOOGLE,
            api_key=api_key,
            model=model,
        )
        return self.create_provider(config)


import os