"""
漫剧生成器 - 核心生成逻辑
"""
import json
from typing import Optional
from pathlib import Path
from datetime import datetime

from src.parser import ScriptParser, Script
from src.ai_client import AIClientFactory, AIClient
from src.prompt import PromptBuilder
from src.config import Config


class ComicGenerator:
    """漫剧生成器"""
    
    def __init__(self, model: str = "qwen"):
        self.parser = ScriptParser()
        self.ai_client = AIClientFactory.create(model)
        self.prompt_builder = PromptBuilder()
        self.model = model
        self.output_dir = Config.OUTPUT_DIR
    
    def generate(self, script_path: str, generate_images: bool = False) -> dict:
        """生成漫剧
        
        Args:
            script_path: 剧本文件路径
            generate_images: 是否生成图片描述
            
        Returns:
            生成的漫剧内容
        """
        # 解析剧本
        print(f"📖 解析剧本: {script_path}")
        script = self.parser.parse(script_path)
        
        # 生成故事板
        print(f"🎨 生成故事板...")
        storyboard = self._generate_storyboard(script)
        
        # 生成分镜描述
        print(f"📐 生成分镜描述...")
        panels = []
        for scene in script.scenes:
            panel = self._generate_scene_panel(scene)
            panels.append(panel)
        
        # 生成图片描述（可选）
        image_prompts = []
        if generate_images:
            print(f"🖼️ 生成图片描述...")
            for scene in script.scenes:
                prompt = self._generate_image_prompt(scene)
                image_prompts.append(prompt)
        
        # 组装结果
        result = {
            "title": script.title,
            "model": self.model,
            "generated_at": datetime.now().isoformat(),
            "scene_count": len(script.scenes),
            "storyboard": storyboard,
            "panels": panels,
            "image_prompts": image_prompts if generate_images else None
        }
        
        # 保存输出
        self._save_output(result)
        
        print(f"✅ 漫剧生成完成！输出目录: {self.output_dir}")
        return result
    
    def _generate_storyboard(self, script: Script) -> dict:
        """生成完整故事板"""
        prompt = self.prompt_builder.build_storyboard_prompt(script)
        try:
            response = self.ai_client.generate(prompt, max_tokens=4000)
            # 尝试解析 JSON
            return self._parse_json_response(response)
        except Exception as e:
            print(f"⚠️ 故事板生成失败: {str(e)}")
            return {"error": str(e), "raw_response": response if 'response' in dir() else ""}
    
    def _generate_scene_panel(self, scene) -> dict:
        """生成单场景分镜"""
        prompt = self.prompt_builder.build_scene_prompt(scene)
        try:
            response = self.ai_client.generate(prompt, max_tokens=2000)
            return {
                "scene_id": scene.id,
                "scene_title": scene.title,
                **self._parse_json_response(response)
            }
        except Exception as e:
            print(f"⚠️ 场景 {scene.id} 分镜生成失败: {str(e)}")
            return {"scene_id": scene.id, "error": str(e)}
    
    def _generate_image_prompt(self, scene) -> str:
        """生成图片描述"""
        prompt = self.prompt_builder.build_image_prompt(scene)
        try:
            return self.ai_client.generate(prompt, max_tokens=500)
        except Exception as e:
            print(f"⚠️ 图片描述生成失败: {str(e)}")
            return f"Error: {str(e)}"
    
    def _parse_json_response(self, response: str) -> dict:
        """解析 JSON 响应"""
        # 尝试直接解析
        try:
            return json.loads(response)
        except:
            pass
        
        # 尝试提取 JSON 代码块
        import re
        json_match = re.search(r'```(?:json)?\s*(\{.*\})\s*```', response, re.DOTALL)
        if json_match:
            try:
                return json.loads(json_match.group(1))
            except:
                pass
        
        # 返回原始响应
        return {"raw_response": response}
    
    def _save_output(self, result: dict):
        """保存生成结果"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        title_slug = result["title"].replace(" ", "_")[:20]
        
        # 保存 JSON
        json_path = self.output_dir / f"{title_slug}_{timestamp}.json"
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        
        # 保存 Markdown 报告
        md_path = self.output_dir / f"{title_slug}_{timestamp}.md"
        self._save_markdown_report(result, md_path)
    
    def _save_markdown_report(self, result: dict, path: Path):
        """保存 Markdown 报告"""
        lines = [
            f"# {result['title']}\n",
            f"> 生成时间: {result['generated_at']}",
            f"> 使用模型: {result['model']}",
            f"> 场景数量: {result['scene_count']}\n",
            "---\n",
            "## 分镜描述\n",
        ]
        
        for panel in result.get('panels', []):
            lines.append(f"### 场景 {panel.get('scene_id', '?')}: {panel.get('scene_title', '未知')}\n")
            if 'panel_descriptions' in panel:
                for pd in panel['panel_descriptions']:
                    lines.append(f"**分镜 {pd.get('panel', '?')}** ({pd.get('camera_angle', '中景')})")
                    lines.append(f"> {pd.get('description', '无描述')}\n")
            lines.append("---\n")
        
        if result.get('image_prompts'):
            lines.append("## 图片描述词\n")
            for i, prompt in enumerate(result['image_prompts'], 1):
                lines.append(f"### 场景 {i}")
                lines.append(f"```\n{prompt}\n```\n")
        
        with open(path, 'w', encoding='utf-8') as f:
            f.write("\n".join(lines))
