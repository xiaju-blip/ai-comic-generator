"""
剧本解析器 - 解析剧本格式
"""
import re
import json
from pathlib import Path
from typing import List, Dict, Optional
from dataclasses import dataclass, asdict


@dataclass
class Dialogue:
    """对话"""
    character: str
    text: str
    emotion: str = "neutral"


@dataclass
class Scene:
    """场景"""
    id: int
    title: str
    setting: str
    description: str
    dialogues: List[Dialogue]


@dataclass
class Script:
    """完整剧本"""
    title: str
    scenes: List[Scene]


class ScriptParser:
    """剧本解析器"""
    
    def __init__(self):
        self.scene_pattern = re.compile(r'^#\s*场景\s*(\d+)[:：]\s*(.+)$')
        self.setting_pattern = re.compile(r'^\[(.+)\]$')
        self.dialogue_pattern = re.compile(r'^([^:：]+)[:：]\s*(.+)$')
    
    def parse(self, script_path: str) -> Script:
        """解析剧本文件"""
        path = Path(script_path)
        if path.suffix == '.json':
            return self._parse_json(path)
        return self._parse_text(path)
    
    def _parse_json(self, path: Path) -> Script:
        """解析 JSON 格式"""
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        scenes = []
        for s in data.get('scenes', []):
            dialogues = [
                Dialogue(
                    character=d['character'],
                    text=d['text'],
                    emotion=d.get('emotion', 'neutral')
                )
                for d in s.get('dialogues', [])
            ]
            scenes.append(Scene(
                id=s['id'],
                title=s.get('title', ''),
                setting=s.get('setting', ''),
                description=s.get('description', ''),
                dialogues=dialogues
            ))
        
        return Script(title=data.get('title', '未命名'), scenes=scenes)
    
    def _parse_text(self, path: Path) -> Script:
        """解析文本格式"""
        with open(path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        scenes = []
        current_scene = None
        current_setting = ""
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # 匹配场景标题
            scene_match = self.scene_pattern.match(line)
            if scene_match:
                if current_scene:
                    scenes.append(current_scene)
                scene_id = len(scenes) + 1
                title = scene_match.group(2)
                current_scene = Scene(
                    id=scene_id,
                    title=title,
                    setting="",
                    description="",
                    dialogues=[]
                )
                continue
            
            # 匹配场景描述
            setting_match = self.setting_pattern.match(line)
            if setting_match and current_scene:
                current_setting = setting_match.group(1)
                current_scene.setting = current_setting
                continue
            
            # 匹配对话
            dialogue_match = self.dialogue_pattern.match(line)
            if dialogue_match and current_scene:
                character = dialogue_match.group(1).strip()
                text = dialogue_match.group(2).strip()
                current_scene.dialogues.append(Dialogue(
                    character=character,
                    text=text,
                    emotion="neutral"
                ))
                continue
        
        # 添加最后一个场景
        if current_scene:
            scenes.append(current_scene)
        
        # 提取标题（从第一个非空行）
        title = "漫剧故事"
        return Script(title=title, scenes=scenes)
    
    def to_dict(self, script: Script) -> dict:
        """转换为字典"""
        return {
            "title": script.title,
            "scenes": [
                {
                    "id": s.id,
                    "title": s.title,
                    "setting": s.setting,
                    "description": s.description,
                    "dialogues": [
                        {"character": d.character, "text": d.text, "emotion": d.emotion}
                        for d in s.dialogues
                    ]
                }
                for s in script.scenes
            ]
        }
