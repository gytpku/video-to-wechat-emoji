# GitHub 上传指南

## 📋 上传前准备

### 1. 检查文件结构
确保您的项目包含以下文件：
```
video-to-wechat-emoji/
├── main.py              ✅ 主程序
├── requirements.txt     ✅ 依赖列表
├── README.md           ✅ 项目说明
├── LICENSE             ✅ 开源许可
├── .gitignore          ✅ 忽略文件配置
├── .env.example        ✅ 环境变量示例
├── CHANGELOG.md        ✅ 版本日志
├── static/
│   └── index.html      ✅ Web界面
├── uploads/            📁 (空文件夹，会被git忽略)
└── results/            📁 (空文件夹，会被git忽略)
```

### 2. 清理敏感信息
- ✅ 删除或移动 `.env` 文件（包含真实API密钥）
- ✅ 清空 `uploads/` 和 `results/` 文件夹
- ✅ 删除测试视频和生成的表情包
- ✅ 检查代码中是否有硬编码的密钥或私人信息

## 🚀 GitHub上传步骤

### 步骤1: 安装Git（如果还没有）
- Windows: 下载 [Git for Windows](https://git-scm.com/download/win)
- 验证安装: 在命令行运行 `git --version`

### 步骤2: 创建GitHub仓库
1. 登录 [GitHub](https://github.com)
2. 点击右上角 "+" → "New repository"
3. 填写仓库信息：
   - **Repository name**: `video-to-wechat-emoji`
   - **Description**: `🎬 智能视频转微信表情包工具 - AI驱动的视频分析与表情包生成`
   - **Visibility**: 选择 Public（公开）
   - ❌ **不要** 勾选 "Initialize this repository with a README"
4. 点击 "Create repository"

### 步骤3: 本地Git初始化和上传

打开命令行（PowerShell或CMD），切换到项目目录：

```bash
# 切换到项目目录
cd c:\AItrials\video_to_whchat_emoji2

# 初始化Git仓库
git init

# 配置Git用户信息（如果是第一次使用）
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"

# 添加所有文件到暂存区
git add .

# 查看状态，确认要提交的文件
git status

# 提交文件
git commit -m "🎉 Initial commit: 视频转微信表情包工具 v1.0.0

✨ 功能特色:
- Google Gemini AI 智能视频分析
- 自动裁剪和缩放
- 多选项表情包生成
- Web用户界面
- 智能文字叠加

🔧 技术栈:
- FastAPI + Python
- FFmpeg 视频处理
- Google Gemini API
- HTML/JavaScript前端"

# 添加远程仓库（替换为您的GitHub用户名）
git remote add origin https://github.com/YOUR_USERNAME/video-to-wechat-emoji.git

# 推送到GitHub
git push -u origin main
```

### 步骤4: 验证上传
1. 刷新GitHub页面，确认文件已上传
2. 检查README.md是否正确显示
3. 确认所有必要文件都已包含

## 🎯 完善GitHub仓库

### 添加标签（Tags）
为您的项目添加主题标签，提高可发现性：
```
video-processing, wechat-emoji, ai, gemini, fastapi, python, ffmpeg, emoji-generator, video-to-gif, automation, chinese
```

在GitHub仓库页面：
1. 点击设置（Settings）
2. 向下滚动到 "Topics" 部分
3. 添加相关标签

### 设置仓库描述
在仓库主页点击齿轮图标，添加描述：
```
🎬 智能视频转微信表情包工具 - 基于Google Gemini AI的视频分析与表情包生成器
```

### 创建Release
1. 点击仓库页面右侧的 "Releases"
2. 点击 "Create a new release"
3. 填写信息：
   - **Tag version**: `v1.0.0`
   - **Release title**: `🎉 v1.0.0 - 初始版本发布`
   - **Description**: 复制CHANGELOG.md中的内容
4. 点击 "Publish release"

## 📢 推广您的项目

### 社交媒体分享
- 在技术社区分享（如掘金、CSDN、知乎）
- 微信技术群分享
- 朋友圈展示

### README优化建议
- 添加效果展示GIF
- 包含实际使用截图
- 提供在线演示链接（如果有）

### 维护建议
- 定期回复Issues
- 处理Pull Requests
- 更新文档和功能
- 发布新版本

## 🔧 故障排除

### 常见问题
1. **推送失败**: 检查网络连接和GitHub访问
2. **文件过大**: 确认.gitignore正确配置
3. **权限问题**: 确认GitHub用户名和密码正确

### 有用的Git命令
```bash
# 查看提交历史
git log --oneline

# 查看当前状态
git status

# 撤销最后一次提交（保留修改）
git reset --soft HEAD~1

# 强制推送（谨慎使用）
git push --force-with-lease
```

## 🎉 恭喜！

您的项目现在已经成功开源到GitHub！记得：
- ⭐ 给自己的项目点个Star
- 📝 持续维护和更新
- 🤝 欢迎社区贡献
- 📢 分享给更多人使用
