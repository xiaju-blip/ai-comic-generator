#!/usr/bin/env python3
"""
AI Comix - 漫剧一键生成器
连接国内免费大模型，根据剧本一键制作漫剧
"""
import sys
import argparse
from pathlib import Path

from src.config import Config
from src.generator import ComicGenerator
from rich.console import Console
from rich.theme import Theme

# 自定义主题
custom_theme = Theme({
    "info": "cyan",
    "warning": "yellow",
    "error": "red bold",
    "success": "green bold",
})
console = Console(theme=custom_theme)


def parse_args():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(
        description="🎬 AI Comix - 漫剧一键生成器",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python src/main.py --script examples/simple_story.txt
  python src/main.py --script examples/simple_story.txt --model glm
  python src/main.py --script examples/simple_story.txt --generate-images
        """
    )
    
    parser.add_argument(
        "--script", "-s",
        required=True,
        help="剧本文件路径 (支持 .txt 和 .json)"
    )
    
    parser.add_argument(
        "--model", "-m",
        default="qwen",
        choices=["qwen", "glm", "spark", "deepseek"],
        help="使用的 AI 模型 (默认: qwen)"
    )
    
    parser.add_argument(
        "--generate-images", "-g",
        action="store_true",
        help="生成图片描述词"
    )
    
    parser.add_argument(
        "--output", "-o",
        default="./output",
        help="输出目录 (默认: ./output)"
    )
    
    parser.add_argument(
        "--list-models",
        action="store_true",
        help="列出支持的 AI 模型"
    )
    
    return parser.parse_args()


def list_models():
    """列出支持的模型"""
    console.print("\n[bold]支持的 AI 模型:[/bold]\n")
    for key, info in Config.AVAILABLE_MODELS.items():
        console.print(f"  • [info]{key}[/info] - {info['provider']}: {info['name']}")
    console.print()


def main():
    """主函数"""
    args = parse_args()
    
    # 列出模型
    if args.list_models:
        list_models()
        return
    
    # 检查脚本文件
    script_path = Path(args.script)
    if not script_path.exists():
        console.print(f"[error]错误: 剧本文件不存在: {args.script}[/error]")
        sys.exit(1)
    
    # 设置输出目录
    Config.OUTPUT_DIR = Path(args.output)
    Config.OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    # 打印欢迎信息
    console.print("\n[bold cyan]🎬 AI Comix - 漫剧生成器[/bold cyan]")
    console.print(f"[info]剧本: {args.script}[/info]")
    console.print(f"[info]模型: {args.model}[/info]")
    console.print(f"[info]输出: {Config.OUTPUT_DIR}[/info]\n")
    
    # 检查 API 配置
    api_key_status = {
        "qwen": bool(Config.QWEN_API_KEY),
        "glm": bool(Config.GLM_API_KEY),
        "deepseek": bool(Config.DEEPSEEK_API_KEY),
        "spark": bool(Config.SPARK_API_KEY),
    }
    
    if not api_key_status.get(args.model):
        console.print(f"[warning]⚠️ 警告: {args.model.upper()}_API_KEY 未配置![/warning]")
        console.print("[info]请在 .env 文件中配置 API Key，或使用 --list-models 查看可用模型[/info]\n")
    
    # 生成漫剧
    try:
        generator = ComicGenerator(model=args.model)
        result = generator.generate(
            script_path=str(script_path),
            generate_images=args.generate_images
        )
        
        # 打印结果
        console.print(f"\n[success]✅ 漫剧生成完成![/success]")
        console.print(f"[info]场景数: {result['scene_count']}[/info]")
        console.print(f"[info]输出文件: {Config.OUTPUT_DIR}/[/info]\n")
        
    except Exception as e:
        console.print(f"[error]错误: {str(e)}[/error]")
        sys.exit(1)


if __name__ == "__main__":
    main()
