"""
单元测试
"""
import pytest
import json
import tempfile
from pathlib import Path
from src.parser import ScriptParser, Script, Scene, Dialogue


@pytest.fixture
def parser():
    return ScriptParser()


@pytest.fixture
def sample_script_txt():
    """生成测试用 txt 剧本"""
    content = """# 场景1: 清晨的公园
[清晨，公园里樱花盛开]

小明: 今天的天气真好啊！
小红: 是啊，一起跑步吧！

# 场景2: 下棋
[下午，棋馆里]

老王: 这一步妙啊！
老李: 承让承让！
"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as f:
        f.write(content)
        return f.name


@pytest.fixture
def sample_script_json():
    """生成测试用 JSON 剧本"""
    data = {
        "title": "春天的故事",
        "scenes": [
            {
                "id": 1,
                "title": "公园",
                "setting": "公园",
                "description": "樱花盛开",
                "dialogues": [
                    {"character": "小明", "text": "天气真好", "emotion": "happy"}
                ]
            }
        ]
    }
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False, encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False)
        return f.name


class TestScriptParser:
    """剧本解析器测试"""
    
    def test_parse_txt(self, parser, sample_script_txt):
        """测试解析文本格式"""
        script = parser.parse(sample_script_txt)
        
        assert isinstance(script, Script)
        assert script.scenes is not None
        assert len(script.scenes) == 2
        
        scene1 = script.scenes[0]
        assert scene1.id == 1
        assert "公园" in scene1.title
        assert len(scene1.dialogues) == 2
        
    def test_parse_json(self, parser, sample_script_json):
        """测试解析 JSON 格式"""
        script = parser.parse(sample_script_json)
        
        assert isinstance(script, Script)
        assert script.title == "春天的故事"
        assert len(script.scenes) == 1
        
        dialogue = script.scenes[0].dialogues[0]
        assert dialogue.character == "小明"
        assert dialogue.emotion == "happy"
    
    def test_to_dict(self, parser, sample_script_txt):
        """测试转换为字典"""
        script = parser.parse(sample_script_txt)
        result = parser.to_dict(script)
        
        assert "title" in result
        assert "scenes" in result
        assert len(result["scenes"]) == 2


class TestPromptBuilder:
    """Prompt 构建器测试"""
    
    def test_scene_prompt(self):
        from src.prompt import PromptBuilder
        
        builder = PromptBuilder()
        scene = Scene(
            id=1, title="公园", setting="樱花公园",
            description="樱花盛开", dialogues=[
                Dialogue(character="小明", text="你好")
            ]
        )
        
        prompt = builder.build_scene_prompt(scene)
        assert "场景编号: 1" in prompt
        assert "小明" in prompt
    
    def test_storyboard_prompt(self):
        from src.prompt import PromptBuilder
        
        builder = PromptBuilder()
        script = Script(
            title="测试",
            scenes=[Scene(
                id=1, title="A", setting="B",
                description="C", dialogues=[]
            )]
        )
        
        prompt = builder.build_storyboard_prompt(script)
        assert "测试" in prompt
        assert "场景 1" in prompt


class TestConfig:
    """配置测试"""
    
    def test_available_models(self):
        from src.config import Config
        
        assert "qwen" in Config.AVAILABLE_MODELS
        assert "glm" in Config.AVAILABLE_MODELS
        assert "deepseek" in Config.AVAILABLE_MODELS
    
    def test_output_dir(self):
        from src.config import Config
        
        assert Config.OUTPUT_DIR.exists()
