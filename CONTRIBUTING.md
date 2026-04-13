# 贡献指南

感谢你对 AI Comix 的兴趣！

## 开发环境

```bash
git clone https://github.com/xiaju-blip/ai-comic-generator.git
cd ai-comic-generator
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## 运行测试

```bash
pytest tests/
```

## 提交 PR

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

## 代码规范

- 使用 Python 3.10+
- 遵循 PEP 8 风格
- 添加类型注解
- 编写单元测试

## 许可证

MIT License
