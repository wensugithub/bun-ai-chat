#huggingface gradio integration 的示例代码，展示了如何使用gradio创建一个简单的界面来与模型进行交互。
#hugginface是一个提供预训练模型的平台，gradio是一个用于快速创建交互式界面的库。通过这个示例代码，用户可以输入文本并与模型进行交互，展示了如何使用gradio来构建一个简单的界面。

# import gradio as gr
# import numpy as np
# import cv2

# def reverse_text(text):
#     return text[::-1]
# def helloPerson(name):
#     return f"Hello {name}!"

# iface = gr.Interface(fn=helloPerson, inputs="text", outputs="text")

# def reverse_and_count(text):
#     reverse_text = text[::-1]
#     length = len(text)
#     return reverse_text, length

# iface = gr.Interface(fn=reverse_and_count, 
#                      inputs="text", 
#                      outputs=["text", "number"], 
#                      title="文本处理工具", 
#                      description="テキストを逆にして、文字数を数えるツールです。",
#                      examples=[["你好，世界！"], ["Gradio是一个很棒的库！"]])


#功能实现 - 图片灰度化
# def convert_to_grayscale(image):
#     """将上传的图片转换为灰度图像"""
#     print("DEBUG: convert_to_grayscale called", type(image))
#     if image is None:
#         return None
    
#     # 如果是PIL Image对象，直接转换
#     if hasattr(image, 'convert'):
#         gray_image = image.convert("L")
#         return gray_image
    
#     # 如果是numpy数组
#     if isinstance(image, np.ndarray):
#         gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
#         return gray_image
    
#     return image

# 创建Gradio界面
# iface = gr.Interface(
#     fn=convert_to_grayscale,
#     inputs=gr.Image(type="pil", label="上传图片"),
#     outputs=gr.Image(type="pil", label="灰度化后的图片"),
#     title="图片灰度化工具",
#     description="上传一张图片，自动转换为灰度图像",
#     examples=[]
# )

# if __name__ == "__main__":
#     print("启动 Gradio 应用...")
#     iface.launch(debug=True)

#■背景 
#   vscode上使用gradio的web界面 
# ■目标
#  1.创建gradio聊天界面，支持用户与ai模型交互
#  2.AI模型需要免费版的，我目前有github free key
#  3.管理聊天记录，维护对话上下文
#  4.处理不同格式的历史消息，确保兼容性
#  5.提供api秘钥验证和错误处理机制
#  6.支持自定义示例问题
import gradio as gr
from openai import OpenAI
import os
from datetime import date, datetime
from zoneinfo import ZoneInfo
import json
import re
import requests


# =========================================
# 🔧 1. 基础配置
# =========================================

# OpenAI 客户端（使用 GitHub Key）
client = OpenAI(
    api_key=os.getenv("GITHUB_API_KEY"),
    base_url="https://models.inference.ai.azure.com"
)

# 每日 token 使用上限（防止爆额度）
DAILY_LIMIT = 80000

# 本地存储文件
USAGE_FILE = "usage.json"

# 城市映射：中文 → (英文, 国家代码)
CITY_MAP = {
    "沈阳": ("Shenyang", "cn"),
    "大连": ("Dalian", "cn"),
    "东京": ("Tokyo", "jp"),
    "千叶": ("Chiba", "jp")
}


# =========================================
# 📊 2. 全局使用量管理
# =========================================

# 当前使用情况（内存中）
global_usage = {
    "date": str(date.today()),
    "total": 0
}


def load_usage():
    """
    从本地文件加载 usage 数据
    👉 用于页面刷新时恢复状态
    """
    global global_usage
    try:
        with open(USAGE_FILE, "r") as f:
            global_usage = json.load(f)
        print("✅ usage 已加载")
    except Exception:
        print("⚠️ usage 文件不存在，使用默认值")


def save_usage():
    """
    保存 usage 到本地文件
    """
    with open(USAGE_FILE, "w") as f:
        json.dump(global_usage, f)


def reset_if_new_day():
    """
    跨天自动重置 usage
    """
    today = str(date.today())
    if global_usage["date"] != today:
        global_usage["date"] = today
        global_usage["total"] = 0
        save_usage()


def get_usage_text():
    """
    返回 UI 显示用的 usage 文本
    """
    return f"📊 今日已用: {global_usage['total']} / {DAILY_LIMIT}"


# 初始化加载
load_usage()


# =========================================
# 🧠 3. 本地功能（不走 AI）
# =========================================

def handle_local_time(user_input):
    """
    本地处理：时间查询
    """
    if "几点" in user_input or "时间" in user_input:
        now = datetime.now(ZoneInfo("Asia/Shanghai")).strftime("%Y-%m-%d %H:%M:%S")
        return f"现在时间是：{now}"
    return None


def handle_local_date(user_input):
    """
    本地处理：日期查询
    """
    if "今天" in user_input:
        now = datetime.now(ZoneInfo("Asia/Shanghai"))
        return now.strftime("今天是：%Y年%m月%d日 %A")
    return None


def extract_city(text):
    """
    从用户输入中提取城市
    👉 用正则匹配支持的城市
    """
    match = re.search(r"(沈阳|大连|东京|千叶)", text)
    return match.group(1) if match else "沈阳"


def get_weather(city):
    """
    调用天气 API 获取天气信息
    """
    api_key = "bbd980a2b4a0e23220fb37ef137e9bf6"

    city_info = CITY_MAP.get(city)
    if not city_info:
        return f"❌ 不支持的城市：{city}"

    city_en, country = city_info

    url = (
        f"https://api.openweathermap.org/data/2.5/weather"
        f"?q={city_en},{country}&appid={api_key}&units=metric&lang=zh_cn"
    )

    try:
        res = requests.get(url).json()

        # API 错误处理
        if res.get("cod") != 200:
            return f"❌ 获取天气失败：{res.get('message')}"

        temp = res["main"]["temp"]
        desc = res["weather"][0]["description"]
        humidity = res["main"]["humidity"]
        wind = res["wind"]["speed"]

        return f"{city}天气：{desc}，气温 {temp}℃，湿度 {humidity}%，风速 {wind} m/s"

    except Exception as e:
        return f"❌ 请求失败：{e}"


def handle_weather(user_input):
    """
    本地处理：天气查询
    """
    if "天气" in user_input:
        city = extract_city(user_input)
        return get_weather(city)
    return None


# =========================================
# 🤖 4. AI 调用逻辑
# =========================================

def call_ai(history):
    """
    调用大模型生成回复
    """
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=history,
        temperature=0.7
    )

    reply = response.choices[0].message.content

    # token 统计
    total_tokens = response.usage.total_tokens
    global_usage["total"] += total_tokens
    save_usage()

    return reply


# =========================================
# 💬 5. 主聊天函数（核心入口）
# =========================================

def chat(user_input, history):
    """
    核心聊天逻辑：
    1. 本地功能优先
    2. 再调用 AI
    3. 管理上下文 & usage
    """
    global global_usage

    if history is None:
        history = []

    try:
        # 1️⃣ 跨天重置
        reset_if_new_day()

        # 2️⃣ 本地功能优先（节省 token）
        for handler in [handle_local_time, handle_local_date, handle_weather]:
            result = handler(user_input)
            if result:
                return update_history(history, user_input, result)

        # 3️⃣ 超限拦截
        if global_usage["total"] >= DAILY_LIMIT:
            return update_history(
                history,
                user_input,
                "⚠️ 今日 token 已达上限，已停止调用模型"
            )

        # 4️⃣ 加入用户消息
        history.append({"role": "user", "content": user_input})

        # 5️⃣ 截断历史（防止太长）
        MAX_HISTORY = 20
        history[:] = history[-MAX_HISTORY:]

        # 6️⃣ 调用 AI
        reply = call_ai(history)

        # 7️⃣ 使用量提醒
        if global_usage["total"] > DAILY_LIMIT * 0.5:
            reply += "\n\n⚠️ 已使用超过50%额度"

        # 8️⃣ 加入 AI 回复
        history.append({"role": "assistant", "content": reply})

        return "", history, get_usage_text()

    except Exception as e:
        return handle_error(e, history)


def update_history(history, user_input, reply):
    """
    统一处理 history 更新（避免重复代码）
    """
    history.append({"role": "user", "content": user_input})
    history.append({"role": "assistant", "content": reply})
    return "", history, get_usage_text()


def handle_error(e, history):
    """
    统一异常处理
    """
    msg = str(e)

    if "429" in msg or "quota" in msg:
        reply = "🚫 已触发平台额度限制"
    else:
        reply = f"❌ 错误: {msg}"

    history.append({"role": "assistant", "content": reply})
    return "", history, get_usage_text()


# =========================================
# 🖥️ 6. UI 层（Gradio）
# =========================================

def clear():
    """
    清空聊天记录
    """
    return [], []


examples = [
    "帮我写一个Python冒泡排序",
    "解释一下什么是REST API",
    "用日语介绍自己",
    "24点：3 7 8 9"
]


with gr.Blocks() as demo:

    gr.Markdown("# 🤖 BUN AI Chat")

    chatbot = gr.Chatbot()
    usage_text = gr.Markdown(get_usage_text())

    msg = gr.Textbox(placeholder="输入你的问题...")

    with gr.Row():
        send = gr.Button("发送")
        clear_btn = gr.Button("清空")

    gr.Examples(examples, inputs=msg)

    state = gr.State([])

    # 发送
    send.click(chat, inputs=[msg, state], outputs=[msg, chatbot, usage_text])

    # 回车发送
    msg.submit(chat, inputs=[msg, state], outputs=[msg, chatbot, usage_text])

    # 清空
    clear_btn.click(clear, outputs=[chatbot, state])

    # 页面加载时刷新 usage
    demo.load(fn=get_usage_text, outputs=usage_text)


demo.launch()

