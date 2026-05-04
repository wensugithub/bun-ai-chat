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
from datetime import date

# ========= 配置 =========
client = OpenAI(
    api_key=os.getenv("GITHUB_API_KEY"),
    base_url="https://models.inference.ai.azure.com"
)

# 👉 每日上限（自己定一个安全值）
DAILY_LIMIT = 80000

# ========= 聊天函数 =========
def chat(user_input, history, usage_state):
    try:
        if history is None:
            history = []

        # ========= 跨天重置 =========
        today = str(date.today())
        if usage_state["date"] != today:
            usage_state["date"] = today
            usage_state["daily_total"] = 0

        # ========= 超限直接拦截 =========
        if usage_state["daily_total"] >= DAILY_LIMIT:
            history.append({
                "role": "assistant",
                "content": "⚠️ 今日 token 已达上限，已停止调用模型"
            })
            return "", history, usage_state, f"📊 今日已用: {usage_state['daily_total']} / {DAILY_LIMIT}"

        # 1️⃣ 先把用户输入加入历史（新版格式）
        history.append({
            "role": "user",
            "content": user_input
        })

        # 2️⃣. 👉 在这里截断（关键位置）
        if len(history) > 20:
            del history[:-20]

        # 2️⃣ 调用模型（直接用 history）
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=history,
            temperature=0.7
        )

        reply = response.choices[0].message.content

        # ========= token统计 =========
        usage = response.usage
        total_tokens = usage.total_tokens

        usage_state["daily_total"] += total_tokens

        # ========= 接近上限提醒 =========
        warning = ""
        if usage_state["daily_total"] > DAILY_LIMIT * 0.5:
            warning = "\n\n⚠️ 已使用超过50%额度"

        # 3️⃣ 把AI回复加入历史
        history.append({
            "role": "assistant",
            "content": reply + warning
        })

        return "", history, usage_state, f"📊 今日已用: {usage_state['daily_total']} / {DAILY_LIMIT}"

    except Exception as e:
        error_msg = str(e)

         # 👉 捕获额度 / 限流错误
        if "429" in error_msg or "quota" in error_msg or "limit" in error_msg:
            reply = "🚫 已触发平台额度限制，请稍后再试"
        else:
            reply = f"❌ 错误: {error_msg}"

        history.append({
            "role": "assistant",
            "content": reply
        })
        return "", history, usage_state, f"📊 今日已用: {usage_state['daily_total']} / {DAILY_LIMIT}"


# ========= 清空 =========
def clear():
    return [], [], {"date": str(date.today()), "daily_total": 0}, f"📊 今日已用: 0 / {DAILY_LIMIT}"


# ========= 示例问题 =========
examples = [
    "帮我写一个Python冒泡排序",
    "解释一下什么是REST API",
    "用日语介绍自己",
    "24点：3 7 8 9"
]

# ========= UI =========
with gr.Blocks() as demo:
    #标题
    gr.Markdown("# 🤖 BUN AI Chat")

    #聊天框
    chatbot = gr.Chatbot()

    usage_text = gr.Markdown(f"📊 今日已用: 0 / {DAILY_LIMIT}")

    #用户输入框
    msg = gr.Textbox(placeholder="输入你的问题...")

    #横向排列两个按钮
    with gr.Row():
        send = gr.Button("发送")
        clear_btn = gr.Button("清空")

    #点击示例 → 自动填入输入框
    gr.Examples(examples, inputs=msg)

    # 状态（保存聊天记录）
    state = gr.State([])

    # 用量记录
    usage_state = gr.State({
        "date": str(date.today()),
        "daily_total": 0
    })

    # 发送消息
    send.click(chat, inputs=[msg, state, usage_state], outputs=[msg, chatbot, usage_state, usage_text])

    # 回车发送（推荐加）
    msg.submit(
        chat,
        inputs=[msg, state, usage_state],
        outputs=[msg, chatbot, usage_state, usage_text]
    )

    # 清空
    clear_btn.click(clear, outputs=[chatbot, state, usage_state, usage_text])

demo.launch()