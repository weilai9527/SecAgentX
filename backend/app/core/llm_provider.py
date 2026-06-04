"""Unified LLM provider - adapted from OpenCode ai_service."""
import os
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional


class LLMError(Exception):
    pass


class BaseLLMProvider(ABC):
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.model_name = config.get("model_name", "")
        self.api_key = config.get("api_key", "")
        self.base_url = config.get("base_url", "")

    @abstractmethod
    def generate(self, prompt: str, system: Optional[str] = None, **kwargs) -> str:
        pass


class LocalLLMProvider(BaseLLMProvider):
    def generate(self, prompt: str, system: Optional[str] = None, **kwargs) -> str:
        import random
        responses = [
            "这是一个本地模拟的安全分析响应。",
            "当前使用本地模式，请配置真实模型 API 以获得分析结果。",
        ]
        return random.choice(responses)


class OpenAIProvider(BaseLLMProvider):
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        try:
            from openai import OpenAI
        except ImportError:
            raise LLMError("未安装 openai 库")
        api_key = os.environ.get("OPENAI_API_KEY") or self.api_key
        base_url = os.environ.get("OPENAI_BASE_URL") or self.base_url or "https://api.openai.com/v1"
        if not api_key:
            raise LLMError("OpenAI API key 未配置")
        self.client = OpenAI(api_key=api_key, base_url=base_url)

    def generate(self, prompt: str, system: Optional[str] = None, **kwargs) -> str:
        system = system or "你是一个专业的网络安全分析师，用中文回答。"
        model = kwargs.get("model") or self.model_name or "gpt-4o"
        response = self.client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": prompt},
            ],
            temperature=kwargs.get("temperature", 0.3),
            max_tokens=kwargs.get("max_tokens", 2048),
            stream=False,
        )
        return response.choices[0].message.content


class AnthropicProvider(BaseLLMProvider):
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        try:
            import anthropic
        except ImportError:
            raise LLMError("未安装 anthropic 库")
        api_key = os.environ.get("ANTHROPIC_API_KEY") or self.api_key
        if not api_key:
            raise LLMError("Anthropic API key 未配置")
        self.client = anthropic.Anthropic(api_key=api_key)

    def generate(self, prompt: str, system: Optional[str] = None, **kwargs) -> str:
        system = system or "你是一个专业的网络安全分析师，用中文回答。"
        model = kwargs.get("model") or self.model_name or "claude-3-haiku-20240307"
        response = self.client.messages.create(
            model=model,
            max_tokens=kwargs.get("max_tokens", 2048),
            system=system,
            messages=[{"role": "user", "content": prompt}],
        )
        return response.content[0].text


class DeepSeekProvider(BaseLLMProvider):
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        try:
            from openai import OpenAI
        except ImportError:
            raise LLMError("未安装 openai 库")
        api_key = os.environ.get("DEEPSEEK_API_KEY") or self.api_key
        base_url = os.environ.get("DEEPSEEK_BASE_URL") or self.base_url or "https://api.deepseek.com"
        if not api_key:
            raise LLMError("DeepSeek API key 未配置")
        self.client = OpenAI(api_key=api_key, base_url=base_url)
        self.model_name = config.get("model_name", "deepseek-v4-flash")

    def generate(self, prompt: str, system: Optional[str] = None, **kwargs) -> str:
        system = system or "你是一个专业的网络安全分析师，用中文回答。"
        model = kwargs.get("model") or self.model_name
        params = {
            "model": model,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": prompt},
            ],
            "temperature": kwargs.get("temperature", 0.3),
            "max_tokens": kwargs.get("max_tokens", 2048),
            "stream": False,
        }
        if model == "deepseek-v4-pro":
            params["extra_body"] = {"thinking": {"type": "enabled"}}
            params["reasoning_effort"] = "high"
        try:
            response = self.client.chat.completions.create(**params)
        except TypeError as te:
            if "reasoning_effort" in str(te):
                params.pop("reasoning_effort", None)
                params.setdefault("extra_body", {}).pop("reasoning_effort", None)
                response = self.client.chat.completions.create(**params)
            else:
                raise
        return response.choices[0].message.content


class OllamaProvider(BaseLLMProvider):
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.base_url = os.environ.get("OLLAMA_BASE_URL") or self.base_url or "http://localhost:11434"

    def generate(self, prompt: str, system: Optional[str] = None, **kwargs) -> str:
        import requests
        system = system or "你是一个专业的网络安全分析师，用中文回答。"
        model = kwargs.get("model") or self.model_name or "llama2"
        response = requests.post(
            f"{self.base_url}/api/chat",
            json={
                "model": model,
                "messages": [
                    {"role": "system", "content": system},
                    {"role": "user", "content": prompt},
                ],
                "stream": False,
            },
            timeout=120,
        )
        if response.status_code != 200:
            raise LLMError(f"Ollama 请求失败: {response.status_code}")
        return response.json().get("message", {}).get("content", "")


class LLMProviderFactory:
    @staticmethod
    def create(config: Dict[str, Any]) -> BaseLLMProvider:
        model_type = config.get("type", "local").lower()
        if model_type == "local":
            return LocalLLMProvider(config)
        if model_type == "openai":
            return OpenAIProvider(config)
        if model_type == "anthropic":
            return AnthropicProvider(config)
        if model_type == "deepseek":
            return DeepSeekProvider(config)
        if model_type == "ollama":
            return OllamaProvider(config)
        raise LLMError(f"不支持的模型类型: {model_type}")


_provider: Optional[BaseLLMProvider] = None


def get_llm_provider(config: Optional[Dict[str, Any]] = None) -> BaseLLMProvider:
    global _provider
    if config is not None:
        _provider = LLMProviderFactory.create(config)
    if _provider is None:
        from app.core.config import DEFAULT_LLM_CONFIG
        _provider = LLMProviderFactory.create(DEFAULT_LLM_CONFIG)
    return _provider
