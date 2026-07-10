import pytest
from core.llm_provider import (
    LLMProviderType,
    ChatRole,
    ChatMessage,
    LLMResponse,
    LLMConfig,
    BaseLLMProvider,
    MockLLMProvider,
    OpenAIProvider,
    AnthropicProvider,
    GoogleProvider,
    LLMProviderManager,
)


class TestLLMProviderType:
    def test_values(self):
        assert LLMProviderType.OPENAI.value == "openai"
        assert LLMProviderType.ANTHROPIC.value == "anthropic"
        assert LLMProviderType.GOOGLE.value == "google"
        assert LLMProviderType.MOCK.value == "mock"


class TestChatRole:
    def test_values(self):
        assert ChatRole.SYSTEM.value == "system"
        assert ChatRole.USER.value == "user"
        assert ChatRole.ASSISTANT.value == "assistant"
        assert ChatRole.TOOL.value == "tool"


class TestChatMessage:
    def test_to_dict(self):
        msg = ChatMessage(
            role=ChatRole.USER,
            content="Hello",
            name="test_user",
            tool_calls=[{"id": "1", "function": {"name": "tool"}}],
            tool_call_id="call_1",
        )
        data = msg.to_dict()
        assert data["role"] == "user"
        assert data["content"] == "Hello"
        assert data["name"] == "test_user"
        assert data["tool_calls"] == [{"id": "1", "function": {"name": "tool"}}]
        assert data["tool_call_id"] == "call_1"

    def test_to_dict_minimal(self):
        msg = ChatMessage(role=ChatRole.SYSTEM, content="System prompt")
        data = msg.to_dict()
        assert data["role"] == "system"
        assert data["content"] == "System prompt"
        assert "name" not in data


class TestLLMResponse:
    def test_to_dict(self):
        response = LLMResponse(
            content="Response content",
            model="test-model",
            provider="openai",
            usage={"prompt_tokens": 10, "completion_tokens": 20, "total_tokens": 30},
            finish_reason="stop",
            tool_calls=[{"id": "1", "function": {"name": "tool"}}],
            error=None,
        )
        data = response.to_dict()
        assert data["content"] == "Response content"
        assert data["model"] == "test-model"
        assert data["provider"] == "openai"
        assert data["usage"] == {"prompt_tokens": 10, "completion_tokens": 20, "total_tokens": 30}
        assert data["finish_reason"] == "stop"
        assert data["error"] is None
        assert "timestamp" in data


class TestLLMConfig:
    def test_to_dict(self):
        config = LLMConfig(
            provider_type=LLMProviderType.OPENAI,
            api_key="secret_key",
            base_url="https://api.example.com",
            model="gpt-4o-mini",
            temperature=0.7,
            max_tokens=4096,
            timeout_seconds=60,
            max_retries=3,
            top_p=1.0,
            frequency_penalty=0.0,
            presence_penalty=0.0,
            system_prompt="You are a helpful assistant",
        )
        data = config.to_dict()
        assert data["provider_type"] == "openai"
        assert data["api_key"] == "***"
        assert data["model"] == "gpt-4o-mini"
        assert data["temperature"] == 0.7

    def test_default_values(self):
        config = LLMConfig(provider_type=LLMProviderType.MOCK)
        assert config.temperature == 0.7
        assert config.max_tokens == 4096
        assert config.timeout_seconds == 60


class TestMockLLMProvider:
    def test_init(self):
        config = LLMConfig(provider_type=LLMProviderType.MOCK)
        provider = MockLLMProvider(config)
        assert provider.get_provider_name() == "mock"

    def test_chat(self):
        config = LLMConfig(provider_type=LLMProviderType.MOCK)
        provider = MockLLMProvider(config)
        messages = [ChatMessage(role=ChatRole.USER, content="Hello")]
        response = provider.chat(messages)
        assert response.content == "This is a mock response for testing purposes."
        assert response.model == "default"
        assert response.provider == "mock"
        assert response.usage is not None

    def test_complete(self):
        config = LLMConfig(provider_type=LLMProviderType.MOCK)
        provider = MockLLMProvider(config)
        response = provider.complete("Complete this")
        assert response.content == "This is a mock completion response."

    def test_embeddings(self):
        config = LLMConfig(provider_type=LLMProviderType.MOCK)
        provider = MockLLMProvider(config)
        embeddings = provider.embeddings("test text")
        assert len(embeddings) == 768

    def test_health_check(self):
        config = LLMConfig(provider_type=LLMProviderType.MOCK)
        provider = MockLLMProvider(config)
        health = provider.health_check()
        assert health["status"] == "healthy"
        assert health["provider"] == "mock"


class TestOpenAIProvider:
    def test_init_with_api_key(self):
        config = LLMConfig(provider_type=LLMProviderType.OPENAI, api_key="test_key")
        provider = OpenAIProvider(config)
        assert provider.get_provider_name() == "openai"

    def test_health_check_failure(self):
        config = LLMConfig(provider_type=LLMProviderType.OPENAI, api_key="invalid_key")
        provider = OpenAIProvider(config)
        health = provider.health_check()
        assert health["status"] == "unhealthy"

    def test_complete(self):
        config = LLMConfig(provider_type=LLMProviderType.OPENAI, api_key="test_key")
        provider = OpenAIProvider(config)
        response = provider.complete("Test")
        assert response.error is not None


class TestAnthropicProvider:
    def test_init_without_library(self):
        config = LLMConfig(provider_type=LLMProviderType.ANTHROPIC)
        provider = AnthropicProvider(config)
        assert provider._client is None

    def test_chat_without_client(self):
        config = LLMConfig(provider_type=LLMProviderType.ANTHROPIC)
        provider = AnthropicProvider(config)
        messages = [ChatMessage(role=ChatRole.USER, content="Hello")]
        response = provider.chat(messages)
        assert response.error == "anthropic library not installed"

    def test_embeddings(self):
        config = LLMConfig(provider_type=LLMProviderType.ANTHROPIC)
        provider = AnthropicProvider(config)
        embeddings = provider.embeddings("test")
        assert len(embeddings) == 768


class TestGoogleProvider:
    def test_init_without_library(self):
        config = LLMConfig(provider_type=LLMProviderType.GOOGLE)
        provider = GoogleProvider(config)
        assert provider._client is None

    def test_chat_without_client(self):
        config = LLMConfig(provider_type=LLMProviderType.GOOGLE)
        provider = GoogleProvider(config)
        messages = [ChatMessage(role=ChatRole.USER, content="Hello")]
        response = provider.chat(messages)
        assert response.error == "google-generativeai library not installed"


class TestLLMProviderManager:
    def test_init(self):
        manager = LLMProviderManager()
        assert len(manager.providers) == 0
        assert manager.default_provider_id is None

    def test_register_provider(self):
        manager = LLMProviderManager()
        config = LLMConfig(provider_type=LLMProviderType.MOCK)
        provider = MockLLMProvider(config)
        result = manager.register_provider(provider)
        assert result is True
        assert "mock" in manager.providers
        assert manager.default_provider_id == "mock"

    def test_register_duplicate_provider(self):
        manager = LLMProviderManager()
        config = LLMConfig(provider_type=LLMProviderType.MOCK)
        provider1 = MockLLMProvider(config)
        provider2 = MockLLMProvider(config)
        manager.register_provider(provider1)
        result = manager.register_provider(provider2)
        assert result is False

    def test_get_provider(self):
        manager = LLMProviderManager()
        config = LLMConfig(provider_type=LLMProviderType.MOCK)
        provider = MockLLMProvider(config)
        manager.register_provider(provider)

        retrieved = manager.get_provider("mock")
        assert retrieved is not None
        assert retrieved.get_provider_name() == "mock"

    def test_get_default_provider(self):
        manager = LLMProviderManager()
        config = LLMConfig(provider_type=LLMProviderType.MOCK)
        provider = MockLLMProvider(config)
        manager.register_provider(provider)

        default = manager.get_provider()
        assert default is not None

    def test_get_provider_not_found(self):
        manager = LLMProviderManager()
        result = manager.get_provider("nonexistent")
        assert result is None

    def test_chat(self):
        manager = LLMProviderManager()
        config = LLMConfig(provider_type=LLMProviderType.MOCK)
        manager.create_provider(config)

        messages = [ChatMessage(role=ChatRole.USER, content="Hello")]
        response = manager.chat(messages)
        assert response.content is not None

    def test_complete(self):
        manager = LLMProviderManager()
        manager.create_mock_provider()

        response = manager.complete("Test prompt")
        assert response.content is not None

    def test_embeddings(self):
        manager = LLMProviderManager()
        manager.create_mock_provider()

        embeddings = manager.embeddings("test")
        assert len(embeddings) > 0

    def test_list_providers(self):
        manager = LLMProviderManager()
        manager.create_mock_provider()

        providers = manager.list_providers()
        assert len(providers) == 1
        assert providers[0]["id"] == "mock"

    def test_set_default_provider(self):
        manager = LLMProviderManager()
        manager.create_mock_provider()

        result = manager.set_default_provider("mock")
        assert result is True

        result = manager.set_default_provider("nonexistent")
        assert result is False

    def test_get_health_summary(self):
        manager = LLMProviderManager()
        manager.create_mock_provider()

        health = manager.get_health_summary()
        assert "mock" in health
        assert health["mock"]["status"] == "healthy"

    def test_create_mock_provider(self):
        manager = LLMProviderManager()
        provider = manager.create_mock_provider()
        assert isinstance(provider, MockLLMProvider)
        assert "mock" in manager.providers

    def test_create_openai_provider(self):
        manager = LLMProviderManager()
        provider = manager.create_openai_provider(api_key="test_key")
        assert isinstance(provider, OpenAIProvider)
        assert "openai" in manager.providers

    def test_create_anthropic_provider(self):
        manager = LLMProviderManager()
        provider = manager.create_anthropic_provider(api_key="test_key")
        assert isinstance(provider, AnthropicProvider)
        assert "anthropic" in manager.providers

    def test_create_google_provider(self):
        manager = LLMProviderManager()
        provider = manager.create_google_provider(api_key="test_key")
        assert isinstance(provider, GoogleProvider)
        assert "google" in manager.providers