"""
配置管理模块
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# 加载 .env 文件
load_dotenv()

class Config:
    """全局配置"""
    
    # API Keys
    QWEN_API_KEY = os.getenv("QWEN_API_KEY", "")
    GLM_API_KEY = os.getenv("GLM_API_KEY", "")
    SPARK_APP_ID = os.getenv("SPARK_APP_ID", "")
    SPARK_API_KEY = os.getenv("SPARK_API_KEY", "")
    SPARK_API_SECRET = os.getenv("SPARK_API_SECRET", "")
    DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", "")
    
    # 默认模型
    DEFAULT_MODEL = os.getenv("DEFAULT_MODEL", "qwen")
    
    # 输出目录
    OUTPUT_DIR = Path(os.getenv("OUTPUT_DIR", "./output"))
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    # 模型端点
    QWEN_ENDPOINT = "https://dashscope.aliyuncs.com/api/v1/services/aigc/text-generation/generation"
    GLM_ENDPOINT = "https://open.bigmodel.cn/api/paas/v4/chat/completions"
    SPARK_ENDPOINT = "wss://spark-api.xf-yun.com/v3.5/chat"
    DEEPSEEK_ENDPOINT = "https://api.deepseek.com/chat/completions"
    
    # 模型列表
    AVAILABLE_MODELS = {
        "qwen": {"name": "qwen-max", "provider": "阿里云"},
        "glm": {"name": "glm-4", "provider": "智谱"},
        "spark": {"name": "spark-3.5", "provider": "讯飞"},
        "deepseek": {"name": "deepseek-chat", "provider": "深度求索"},
    }
