"""
Prompt 模板 - 生成各类漫剧内容
"""

COMIC_SYSTEM_PROMPT = """你是一位专业的漫画编剧和分镜师。请根据剧本生成专业的漫剧内容。"""

COMIC_SCENE_PROMPT = """根据以下剧本场景，生成漫画分镜描述：

{scene_info}

请生成以下内容（JSON格式）：
{{
  "scene_title": "场景标题",
  "panel_descriptions": [
    {{
      "panel": 1,
      "description": "分镜描述（包含角色动作、表情、场景细节）",
      "camera_angle": "镜头角度（如：远景、中景、近景、特写）",
      "emotion": "整体情绪"
    }}
  ],
  "dialogue_bubbles": [
    {{
      "panel": 1,
      "character": "角色名",
      "text": "对话内容",
      "bubble_style": "对话框样式（如：普通、思考、喊叫、耳语）"
    }}
  ],
  "narration": "旁白/解说文字"
}}
"""

COMIC_CHARACTER_PROMPT = """根据以下角色描述，生成角色设定卡：

{character_info}

请生成角色设定（JSON格式）：
{{
  "name": "角色名",
  "appearance": "外貌描述",
  "personality": "性格特点",
  "signature_pose": "招牌动作/姿势",
  "color_palette": "配色方案（如：主色调、次色调）"
}}
"""

COMIC_STORYBOARD_PROMPT = """根据以下剧本，生成完整的故事板：

{story_info}

请生成完整故事板（JSON格式，包含所有场景的分镜描述和对话框）："""

IMAGE_PROMPT_TEMPLATE = """请为以下漫剧场景生成图片描述词（用于 AI 绘图）：

场景：{scene}
角色：{characters}
对话：{dialogues}
风格：{style}

请生成详细的图片生成 Prompt（英文，越详细越好）："""


class PromptBuilder:
    """Prompt 构建器"""
    
    def __init__(self, system_prompt: str = COMIC_SYSTEM_PROMPT):
        self.system_prompt = system_prompt
    
    def build_scene_prompt(self, scene) -> str:
        """构建场景分镜 Prompt"""
        # 提取对话信息
        dialogues = "\n".join(
            f"{d.character}: {d.text}" for d in scene.dialogues
        ) if scene.dialogues else "无对话"
        
        scene_info = f"""
场景编号: {scene.id}
场景标题: {scene.title}
场景设定: {scene.setting}
场景描述: {scene.description}
对话内容:
{dialogues}
"""
        return COMIC_SCENE_PROMPT.format(scene_info=scene_info)
    
    def build_storyboard_prompt(self, script) -> str:
        """构建完整故事板 Prompt"""
        # 收集所有场景信息
        scenes_info = []
        for scene in script.scenes:
            dialogues = "\n".join(
                f"- {d.character}: {d.text}" for d in scene.dialogues
            ) if scene.dialogues else "（无对话）"
            
            scenes_info.append(f"""
=== 场景 {scene.id}: {scene.title} ===
设定: {scene.setting}
描述: {scene.description}
对话:
{dialogues}
""")
        
        story_info = f"""
漫剧标题: {script.title}
总场景数: {len(script.scenes)}

{'='*40}
场景列表:
{'='*40}
{"".join(scenes_info)}
"""
        return COMIC_STORYBOARD_PROMPT.format(story_info=story_info)
    
    def build_image_prompt(self, scene, style: str = "日系漫画") -> str:
        """构建图片生成 Prompt"""
        characters = list(set(d.character for d in scene.dialogues)) if scene.dialogues else []
        dialogues = "\n".join(
            f"{d.character}: {d.text}" for d in scene.dialogues
        ) if scene.dialogues else ""
        
        return IMAGE_PROMPT_TEMPLATE.format(
            scene=scene.title,
            characters=", ".join(characters),
            dialogues=dialogues,
            style=style
        )
