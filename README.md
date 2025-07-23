# 视频转微信表情包工具 (Video to WeChat Emoji)

一个基于 FastAPI 和 Google Gemini AI 的智能视频转微信表情包工具，能够自动分析视频内容并生成多个表情包选项。

## 🌟 功能特色

- **智能分析**: 使用 Google Gemini AI 分析视频内容，识别关键时刻和表情
- **自动裁剪**: 智能缩放和裁剪，保留主要内容的同时转换为方形格式
- **多选项生成**: 一次上传可生成 多 个不同的表情包选项
- **文字叠加**: 自动添加合适的中文文字描述
- **格式优化**: 输出符合微信表情包标准的视频格式
- **Web界面**: 简洁易用的网页操作界面

## 🚀 快速开始

### 环境要求

- Python 3.8+
- FFmpeg (用于视频处理)
- Google Gemini API Key

### 安装步骤

1. **克隆项目**
   ```bash
   git clone https://github.com/yourusername/video-to-wechat-emoji.git
   cd video-to-wechat-emoji
   ```

2. **安装依赖**
   ```bash
   pip install -r requirements.txt
   ```

3. **安装 FFmpeg**
   - Windows: 从 [FFmpeg官网](https://ffmpeg.org/download.html) 下载并添加到系统PATH
   - macOS: `brew install ffmpeg`
   - Linux: `sudo apt install ffmpeg`

4. **配置环境变量**
   
   创建 `.env` 文件：
   ```bash
   GOOGLE_API_KEY=your_google_gemini_api_key_here
   GEMINI_MODEL_NAME=gemini-2.5-flash
   ```

5. **运行应用**
   ```bash
   python main.py
   ```
   
   访问 http://localhost:8000 开始使用

## 📖 使用说明

1. **上传视频**: 点击选择视频文件（支持所有gemini模型可读的视频格式，已测试mp4可以）
2. **输入描述**: 输入想要的表情包描述或情绪关键词
3. **生成表情包**: 点击处理按钮，AI 将自动分析并生成多个选项
4. **下载结果**: 选择喜欢的表情包下载使用（也可在/results文件夹中找到）

## 🛠 技术架构

- **后端**: FastAPI + Python
- **AI分析**: Google Gemini 1.5 Flash
- **视频处理**: FFmpeg
- **前端**: HTML + JavaScript
- **文件存储**: 本地文件系统

## 📁 项目结构

```
video-to-wechat-emoji/
├── main.py              # 主程序文件
├── requirements.txt     # Python依赖
├── .env.example        # 环境变量示例
├── static/             # 静态文件
│   └── index.html      # Web界面
├── uploads/            # 临时上传文件夹
├── results/            # 生成结果文件夹
├── README.md           # 说明文档
├── LICENSE             # 开源许可证
├── .gitignore          # Git忽略文件
└── CHANGELOG.md        # 版本更新日志
```

## ⚙️ 配置说明

### 环境变量

- `GOOGLE_API_KEY`: Google Gemini API密钥（必需）
- `GEMINI_MODEL_NAME`: 使用的Gemini模型名称（可选，默认：gemini-2.5-flash）

### API限制

- 支持的视频格式: MP4
- 最大视频时长: 建议 5 分钟以内
- 输出格式: 400x400 到 500x500 像素的方形视频
- 表情包时长: 最多 5 秒

## 🔧 开发指南

### 本地开发

```bash
# 安装开发依赖
pip install -r requirements.txt

# 启动开发服务器
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 核心功能

- `generate_ai_instructions()`: AI分析视频内容
- `fix_time_format()`: 时间格式修复
- `run_ffmpeg_command()`: FFmpeg命令执行
- `get_video_dimensions()`: 获取视频尺寸

## 🤝 贡献指南

欢迎提交 Issue 和 Pull Request！

1. Fork 本项目
2. 创建新的功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

## 📝 许可证

本项目基于 MIT 许可证开源 - 查看 [LICENSE](LICENSE) 文件了解详情

## ⚠️ 免责声明

- 请确保上传的视频内容符合相关法律法规
- 生成的表情包仅供个人学习和娱乐使用
- 请遵守微信平台的使用条款

## 🙏 致谢

- [Google Gemini AI](https://ai.google.dev/) - 提供强大的AI分析能力
- [FFmpeg](https://ffmpeg.org/) - 专业的视频处理工具
- [FastAPI](https://fastapi.tiangolo.com/) - 现代化的Web框架

## 📞 联系方式

如有问题或建议，请通过以下方式联系：

- 提交 [GitHub Issue](https://github.com/yourusername/video-to-wechat-emoji/issues)
- 发送邮件到: your.email@example.com

---

⭐ 如果这个项目对您有帮助，请给个 Star 支持一下！
