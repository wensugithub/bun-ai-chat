# 🤖 AI Chat Web App

一个基于 **Gradio + GPT API** 的轻量级 AI 聊天应用，支持多轮对话与上下文记忆。

---

## 🌐 在线体验

👉 点击访问：
**🔗 https://你的用户名-你的space名.hf.space**

> ⚠️ 如果加载较慢，是因为免费部署环境冷启动（正常现象）

---

## ✨ 功能特点

* 💬 多轮对话（支持上下文记忆）
* ⚡ 响应快速（基于轻量模型）
* 🧠 类 ChatGPT 交互体验
* 🖥️ 简洁 Web UI（Gradio）
* ☁️ 云端部署（无需本地运行）

---

## 🧱 技术栈

* Python
* Gradio（前端 UI）
* OpenAI API / GitHub Models
* HuggingFace Spaces（部署）

---

## 🚀 本地运行

### 1️⃣ 克隆项目

```bash
git clone https://github.com/你的用户名/你的仓库名.git
cd 你的仓库名
```

---

### 2️⃣ 安装依赖

```bash
pip install -r requirements.txt
```

---

### 3️⃣ 配置环境变量

```bash
export GITHUB_API_KEY=你的key   # Mac/Linux
set GITHUB_API_KEY=你的key      # Windows
```

---

### 4️⃣ 启动项目

```bash
python app.py
```

打开浏览器访问：

```text
http://127.0.0.1:7860
```

---

## 📁 项目结构

```text
.
├── app.py              # 主程序
├── requirements.txt    # 依赖
├── README.md           # 项目说明
```

---

## ⚙️ 核心逻辑说明

* 使用 `gr.State` 管理对话历史
* 每次请求将 `history` 发送给模型，实现上下文记忆
* 返回结果同步更新 UI 和状态

---

## 🧩 后续优化方向

* 🔄 流式输出（Streaming）
* 🎭 System Prompt（自定义 AI 人设）
* 🧹 上下文裁剪（防止 token 爆炸）
* 🌍 多模型切换
* 💾 聊天记录持久化（数据库）

---

## 📌 项目说明

这是一个用于学习和实践 AI 应用开发的项目，重点在于：

* 理解大模型 API 调用方式
* 掌握 Web UI 快速搭建（Gradio）
* 完成从本地开发 → 云部署 的完整流程

---

## 🙌 致谢

感谢开源社区提供的工具与平台支持。

---

## ⭐ 如果这个项目对你有帮助

欢迎点个 Star ⭐
