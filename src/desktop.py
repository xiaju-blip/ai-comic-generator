#!/usr/bin/env python3
"""
AI Comix - 桌面版漫剧生成器
带 GUI 的桌面应用
"""
import sys
import json
import threading
from pathlib import Path
from datetime import datetime

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTextEdit, QPushButton, QLabel, QComboBox, QGroupBox,
    QFileDialog, QMessageBox, QProgressBar, QSplitter, QListWidget,
    QListWidgetItem, QTabWidget, QFrame
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QFont, QIcon, QColor, QPalette

from src.parser import ScriptParser
from src.generator import ComicGenerator
from src.config import Config


class GeneratorThread(QThread):
    """后台生成线程"""
    progress = pyqtSignal(str)
    finished = pyqtSignal(dict)
    error = pyqtSignal(str)
    
    def __init__(self, script_text: str, model: str, generate_images: bool):
        super().__init__()
        self.script_text = script_text
        self.model = model
        self.generate_images = generate_images
    
    def run(self):
        try:
            # 保存临时脚本文件
            temp_path = Path("/tmp/temp_script.txt")
            temp_path.write_text(self.script_text, encoding='utf-8')
            
            self.progress.emit("📖 解析剧本...")
            generator = ComicGenerator(model=self.model)
            
            self.progress.emit("🎨 生成漫剧内容...")
            result = generator.generate(
                script_path=str(temp_path),
                generate_images=self.generate_images
            )
            
            self.progress.emit("✅ 生成完成！")
            self.finished.emit(result)
            
        except Exception as e:
            self.error.emit(str(e))


class ComicViewer(QFrame):
    """漫剧预览器"""
    
    def __init__(self):
        super().__init__()
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout(self)
        
        # 标题
        self.title_label = QLabel("漫剧预览")
        self.title_label.setFont(QFont("Arial", 16, QFont.Bold))
        layout.addWidget(self.title_label)
        
        # 场景列表
        self.scene_list = QListWidget()
        self.scene_list.itemClicked.connect(self.on_scene_selected)
        layout.addWidget(QLabel("场景列表:"))
        layout.addWidget(self.scene_list)
        
        # 分镜内容
        self.content_text = QTextEdit()
        self.content_text.setReadOnly(True)
        self.content_text.setFont(QFont("Arial", 11))
        layout.addWidget(QLabel("分镜内容:"))
        layout.addWidget(self.content_text)
    
    def load_result(self, result: dict):
        """加载生成结果"""
        self.result = result
        self.title_label.setText(f"📚 {result.get('title', '漫剧')}")
        
        # 清空并填充场景列表
        self.scene_list.clear()
        for panel in result.get('panels', []):
            item = QListWidgetItem(f"场景 {panel.get('scene_id', '?')}: {panel.get('scene_title', '未知')}")
            item.setData(Qt.UserRole, panel)
            self.scene_list.addItem(item)
        
        if self.scene_list.count() > 0:
            self.scene_list.setCurrentRow(0)
            self.on_scene_selected(self.scene_list.item(0))
    
    def on_scene_selected(self, item):
        """选中场景"""
        panel = item.data(Qt.UserRole)
        
        content = f"### 场景 {panel.get('scene_id', '?')}: {panel.get('scene_title', '未知')}\n\n"
        
        if 'panel_descriptions' in panel:
            content += "**分镜描述:**\n\n"
            for pd in panel['panel_descriptions']:
                content += f"- **分镜 {pd.get('panel', '?')}** ({pd.get('camera_angle', '中景')})\n"
                content += f"  {pd.get('description', '')}\n\n"
        
        if 'dialogue_bubbles' in panel:
            content += "\n**对话:**\n\n"
            for db in panel['dialogue_bubbles']:
                content += f"- {db.get('character', '?')}: {db.get('text', '')}\n"
        
        self.content_text.setMarkdown(content)


class MainWindow(QMainWindow):
    """主窗口"""
    
    def __init__(self):
        super().__init__()
        self.parser = ScriptParser()
        self.init_ui()
    
    def init_ui(self):
        self.setWindowTitle("🎬 AI Comix - 漫剧一键生成器")
        self.setGeometry(100, 100, 1200, 800)
        
        # 主窗口部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        
        # 左侧：输入区域
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        
        # 剧本输入区
        script_group = QGroupBox("📝 剧本输入")
        script_layout = QVBoxLayout(script_group)
        
        # 工具栏
        toolbar = QHBoxLayout()
        self.load_btn = QPushButton("📂 打开文件")
        self.load_btn.clicked.connect(self.load_script)
        self.clear_btn = QPushButton("🗑️ 清空")
        self.clear_btn.clicked.connect(self.clear_script)
        toolbar.addWidget(self.load_btn)
        toolbar.addWidget(self.clear_btn)
        toolbar.addStretch()
        script_layout.addLayout(toolbar)
        
        # 剧本文本框
        self.script_text = QTextEdit()
        self.script_text.setFont(QFont("Arial", 11))
        self.script_text.setPlaceholderText("""# 场景1: 开场
[春日午后，樱花树下]

小明: 今天的天气真好啊！
小红: 是啊，一起跑步吧！

# 场景2: ...
[场景描述]

角色: 对白内容
""")
        script_layout.addWidget(self.script_text)
        
        left_layout.addWidget(script_group)
        
        # 配置区
        config_group = QGroupBox("⚙️ 配置")
        config_layout = QVBoxLayout(config_group)
        
        # 模型选择
        model_row = QHBoxLayout()
        model_row.addWidget(QLabel("AI 模型:"))
        self.model_combo = QComboBox()
        self.model_combo.addItems(["qwen", "glm", "deepseek"])
        self.model_combo.setToolTip("选择要使用的 AI 模型\n• qwen: 通义千问\n• glm: 智谱 GLM\n• deepseek: 深度求索")
        model_row.addWidget(self.model_combo)
        model_row.addStretch()
        config_layout.addLayout(model_row)
        
        # 选项
        self.gen_images_cb = QPushButton("🖼️ 生成图片描述")
        self.gen_images_cb.setCheckable(True)
        self.gen_images_cb.setChecked(True)
        config_layout.addWidget(self.gen_images_cb)
        
        left_layout.addWidget(config_group)
        
        # 生成按钮
        self.generate_btn = QPushButton("🚀 一键生成漫剧")
        self.generate_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                font-size: 16px;
                font-weight: bold;
                padding: 15px;
                border-radius: 8px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:disabled {
                background-color: #cccccc;
            }
        """)
        self.generate_btn.clicked.connect(self.generate_comic)
        left_layout.addWidget(self.generate_btn)
        
        # 进度条
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 0)  # 不确定进度
        self.progress_bar.setVisible(False)
        left_layout.addWidget(self.progress_bar)
        
        # 状态栏
        self.status_label = QLabel("就绪")
        self.status_label.setStyleSheet("color: #666;")
        left_layout.addWidget(self.status_label)
        
        # 右侧：预览区域
        right_panel = QTabWidget()
        
        # 预览标签页
        self.preview_viewer = ComicViewer()
        right_panel.addTab(self.preview_viewer, "📖 漫剧预览")
        
        # JSON 标签页
        self.json_text = QTextEdit()
        self.json_text.setReadOnly(True)
        self.json_text.setFont(QFont("Courier", 10))
        right_panel.addTab(self.json_text, "📄 JSON 输出")
        
        # 帮助标签页
        help_text = QTextEdit()
        help_text.setReadOnly(True)
        help_text.setMarkdown("""
# 🎬 AI Comix 使用说明

## 剧本格式

### 基础格式

```
# 场景1: 场景标题
[场景描述，环境设定]

角色名: 对话内容
角色名: 对话内容

# 场景2: 下一个场景
[场景描述]

角色名: 对话内容
```

### 示例

```
# 场景1: 相遇
[春日午后，樱花树下]

小明: 今天的天气真好啊！
小红: 是啊，一起跑步吧！

# 场景2: 冒险开始
[两人决定一起探索]

小明: 我们一起做个项目吧！
小红: 好啊！
```

## 支持的 AI 模型

| 模型 | 提供商 | 免费额度 |
|------|--------|----------|
| qwen | 阿里云 | 100万 tokens |
| glm | 智谱 | 400万 tokens |
| deepseek | 深度求索 | 100万 tokens |

## 配置 API Key

1. 复制 `.env.example` 为 `.env`
2. 填入你的 API Key
3. 重启应用

## 快捷键

- `Ctrl+O`: 打开文件
- `Ctrl+Enter`: 生成漫剧
""")
        right_panel.addTab(help_text, "❓ 帮助")
        
        # 分割器
        splitter = QSplitter(Qt.Horizontal)
        splitter.addWidget(left_panel)
        splitter.addWidget(right_panel)
        splitter.setSizes([400, 800])
        
        main_layout.addWidget(splitter)
        
        # 设置样式
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f5f5f5;
            }
            QGroupBox {
                font-weight: bold;
                border: 2px solid #ddd;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
            QTextEdit {
                border: 1px solid #ddd;
                border-radius: 4px;
                padding: 5px;
            }
            QPushButton {
                padding: 8px 16px;
                border-radius: 4px;
            }
        """)
    
    def load_script(self):
        """加载剧本文件"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "打开剧本文件", "", "文本文件 (*.txt);;JSON 文件 (*.json);;所有文件 (*)"
        )
        if file_path:
            try:
                content = Path(file_path).read_text(encoding='utf-8')
                self.script_text.setPlainText(content)
                self.status_label.setText(f"已加载: {Path(file_path).name}")
            except Exception as e:
                QMessageBox.critical(self, "错误", f"无法加载文件: {str(e)}")
    
    def clear_script(self):
        """清空剧本"""
        self.script_text.clear()
        self.status_label.setText("已清空")
    
    def generate_comic(self):
        """生成漫剧"""
        script = self.script_text.toPlainText().strip()
        if not script:
            QMessageBox.warning(self, "提示", "请先输入剧本内容！")
            return
        
        model = self.model_combo.currentText()
        generate_images = self.gen_images_cb.isChecked()
        
        # 禁用按钮，显示进度
        self.generate_btn.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.status_label.setText("正在生成...")
        
        # 启动后台线程
        self.thread = GeneratorThread(script, model, generate_images)
        self.thread.progress.connect(self.on_progress)
        self.thread.finished.connect(self.on_finished)
        self.thread.error.connect(self.on_error)
        self.thread.start()
    
    def on_progress(self, msg: str):
        """进度更新"""
        self.status_label.setText(msg)
    
    def on_finished(self, result: dict):
        """生成完成"""
        self.generate_btn.setEnabled(True)
        self.progress_bar.setVisible(False)
        self.status_label.setText("✅ 生成完成！")
        
        # 更新预览
        self.preview_viewer.load_result(result)
        
        # 更新 JSON
        self.json_text.setPlainText(json.dumps(result, ensure_ascii=False, indent=2))
        
        QMessageBox.information(self, "完成", f"漫剧生成完成！\n场景数: {result.get('scene_count', 0)}")
    
    def on_error(self, error: str):
        """生成错误"""
        self.generate_btn.setEnabled(True)
        self.progress_bar.setVisible(False)
        self.status_label.setText("❌ 生成失败")
        
        QMessageBox.critical(self, "错误", f"生成失败: {error}")


def main():
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
