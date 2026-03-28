"""
AI 客户端 - 连接各大国内免费大模型
"""
import os
import json
import requests
from typing import Optional
from abc import ABC, abstractmethod
from src.config import Config


class AIClient(ABC):
    """AI 客户端基类"""
    
    @abstractmethod
    def generate(self, prompt: str, max_tokens: int = 2000) -> str:
        """生成文本"""
        pass


class QwenClient(AIClient):
    """阿里云通义千问客户端"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.endpoint = Config.QWEN_ENDPOINT
    
    def generate(self, prompt: str, max_tokens: int = 2000) -> str:
        """调用通义千问 API"""
        if not self.api_key:
            raise ValueError("QWEN_API_KEY not configured")
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": "qwen-max",
            "messages": [{"role": "user", "content": prompt}],
            "parameters": {"max_tokens": max_tokens}
        }
        
        try:
            response = requests.post(self.endpoint, json=payload, headers=headers, timeout=30)
            response.raise_for_status()
            result = response.json()
            return result['output']['text']
        except Exception as e:
            raise RuntimeError(f"Qwen API error: {str(e)}")


class GLMClient(AIClient):
    """智谱 GLM 客户端"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.endpoint = Config.GLM_ENDPOINT
    
    def generate(self, prompt: str, max_tokens: int = 2000) -> str:
        """调用 GLM API"""
        if not self.api_key:
            raise ValueError("GLM_API_KEY not configured")
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": "glm-4",
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": max_tokens
        }
        
        try:
            response = requests.post(self.endpoint, json=payload, headers=headers, timeout=30)
            response.raise_for_status()
            result = response.json()
            return result['choices'][0]['message']['content']
        except Exception as e:
            raise RuntimeError(f"GLM API error: {str(e)}")


class DeepSeekClient(AIClient):
    """深度求索 DeepSeek 客户端"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.endpoint = Config.DEEPSEEK_ENDPOINT
    
    def generate(self, prompt: str, max_tokens: int = 2000) -> str:
        """调用 DeepSeek API"""
        if not self.api_key:
            raise ValueError("DEEPSEEK_API_KEY not configured")
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": "deepseek-chat",
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": max_tokens
        }
        
        try:
            response = requests.post(self.endpoint, json=payload, headers=headers, timeout=30)
            response.raise_for_status()
            result = response.json()
            return result['choices'][0]['message']['content']
        except Exception as e:
            raise RuntimeError(f"DeepSeek API error: {str(e)}")


class AIClientFactory:
    """AI 客户端工厂"""
    
    @staticmethod
    def create(model: str = "qwen") -> AIClient:
        """创建 AI 客户端"""
        model = model.lower()
        
        if model == "qwen":
            return QwenClient(Config.QWEN_API_KEY)
        elif model == "glm":
            return GLMClient(Config.GLM_API_KEY)
        elif model == "deepseek":
            return DeepSeekClient(Config.DEEPSEEK_API_KEY)
        else:
            raise ValueError(f"Unsupported model: {model}")
