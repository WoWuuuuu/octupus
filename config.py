import os
from typing import Optional, Dict, Any

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

class OctopusConfig:
    """
    Global configuration for Octopus.
    Loads from config/application.yml, and allows overriding via environment variables.
    """
    def __init__(self):
        self._load_yaml_config()
        
        # Override with Environment Variables if they exist (Spring Boot style)
        # We check the same ENV vars we used before, providing backward compatibility
        self.llm_provider = os.getenv("OCTOPUS_LLM_PROVIDER", self.llm_provider).lower()
        self.llm_model = os.getenv("OCTOPUS_LLM_MODEL", self.llm_model)
        
        env_openai_key = os.getenv("OCTOPUS_OPENAI_API_KEY")
        if env_openai_key:
            self.openai_api_key = env_openai_key
            
        env_openai_base = os.getenv("OCTOPUS_OPENAI_BASE_URL")
        if env_openai_base:
            self.openai_base_url = env_openai_base
            
        env_ollama_base = os.getenv("OCTOPUS_OLLAMA_BASE_URL")
        if env_ollama_base:
            self.ollama_base_url = env_ollama_base

    def _load_yaml_config(self):
        # Default values
        self.llm_provider = "mock"
        self.llm_model = "gpt-4o"
        self.openai_api_key: Optional[str] = None
        self.openai_base_url: Optional[str] = None
        self.ollama_base_url = "http://localhost:11434"
        
        yaml_path = os.path.join(os.path.dirname(__file__), "config", "application.yml")
        
        try:
            import yaml
            if os.path.exists(yaml_path):
                with open(yaml_path, 'r', encoding='utf-8') as f:
                    yaml_data = yaml.safe_load(f) or {}
                    
                llm_config = yaml_data.get("llm", {})
                self.llm_provider = llm_config.get("provider", self.llm_provider)
                self.llm_model = llm_config.get("model", self.llm_model)
                
                openai_config = llm_config.get("openai", {})
                self.openai_api_key = openai_config.get("api_key", self.openai_api_key)
                self.openai_base_url = openai_config.get("base_url", self.openai_base_url)
                
                ollama_config = llm_config.get("ollama", {})
                self.ollama_base_url = ollama_config.get("base_url", self.ollama_base_url)
        except ImportError:
            print("Warning: pyyaml is not installed. Using default config. Please run 'pip install pyyaml'")
        except Exception as e:
            print(f"Warning: Failed to load {yaml_path}: {e}")

    @classmethod
    def reload(cls) -> "OctopusConfig":
        """Reload configuration."""
        return cls()

    def print_config(self):
        """Print the current configuration (hiding sensitive info)."""
        print("=== Octopus Configuration (YAML Loaded) ===")
        print(f"LLM Provider:   {self.llm_provider}")
        print(f"LLM Model:      {self.llm_model}")
        if self.llm_provider == "openai":
            key_preview = f"{self.openai_api_key[:6]}...{self.openai_api_key[-4:]}" if self.openai_api_key and len(self.openai_api_key) > 10 else "Not Set or Too Short"
            print(f"OpenAI BaseURL: {self.openai_base_url or 'Default (https://api.openai.com/v1)'}")
            print(f"OpenAI API Key: {key_preview}")
        elif self.llm_provider == "ollama":
            print(f"Ollama BaseURL: {self.ollama_base_url}")
        print("=========================================")

# Global instance
config = OctopusConfig()
