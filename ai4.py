import os
import requests
import json
import time
import tkinter as tk
from tkinter import scrolledtext, messagebox, ttk
import threading
import random


class ChatApp:
    def __init__(self):
        # 配置参数
        self.API_KEY = "sk-8fb04c5cba064b03a78d3dabe4f45bfd"  # 从 https://platform.deepseek.com 获取
        self.MODEL = "deepseek-chat"  # 模型名称
        self.API_URL = "https://api.deepseek.com/v1/chat/completions"

        # 初始化对话历史
        self.conversation_history = [
            {"role": "system",
             "content": "你是一个酒店老板，趾高气昂，不允许员工休息。而我是一名前台管理员，忙碌了半天，准备歇一下，这时你来了，准备和我对话。"}
        ]

        # 头像ASCII艺术
        self.USER_AVATAR = "👨‍💼"
        self.BOSS_AVATAR = "👔"

        # 打字动画相关状态
        self.TYPING_INDICATOR = ["•   ", "• • ", "• • •"]
        self.typing_animation_index = 0
        self.typing_animation_id = None
        self.typing_line_index = None  # 记录打字指示器的位置
        self.animation_running = False  # 动画运行状态标志

        # 主窗口对象
        self.root = None
        self.chat_text = None
        self.entry = None
        self.input_prompt = "老板在等着你开口对话... \n"

    def optimize_api_request(self, prompt):
        """优化API请求参数以加快响应"""
        headers = {
            "Authorization": f"Bearer {self.API_KEY}",
            "Content-Type": "application/json"
        }

        # 添加用户新消息到历史
        self.conversation_history.append({"role": "user", "content": prompt})

        payload = {
            "model": self.MODEL,
            "messages": self.conversation_history,
            "temperature": 0.5,  # 降低温度值，减少随机性，加快生成
            "max_tokens": 800,  # 限制最大生成token数
            "top_p": 0.8,  # 降低top_p值
            "frequency_penalty": 0.2,  # 添加频率惩罚，减少重复
            "presence_penalty": 0.1  # 添加存在惩罚，促进新内容
        }

        try:
            # 设置请求超时时间
            response = requests.post(self.API_URL, headers=headers, json=payload, timeout=15)
            response.raise_for_status()

            result = response.json()
            ai_reply = result['choices'][0]['message']['content'].strip()

            # 添加AI回复到历史
            self.conversation_history.append({"role": "assistant", "content": ai_reply})

            return ai_reply

        except requests.exceptions.Timeout:
            return "请求超时，请稍后再试"
        except Exception as e:
            return f"请求出错: {str(e)}"

    def animate_typing_indicator(self):
        """动画效果：更新打字指示器"""
        if not self.animation_running or self.typing_line_index is None:
            return

        try:
            # 更新打字指示器
            self.chat_text.config(state=tk.NORMAL)

            # 获取当前行的完整文本
            current_line = self.chat_text.get(f"{self.typing_line_index}.0", f"{self.typing_line_index}.end")

            # 检查是否包含动画标记
            if f"{self.BOSS_AVATAR} 老板正在思考" in current_line:
                # 找到动画文本的起始位置
                start_pos = current_line.find("老板正在思考") + len("老板正在思考") + 1

                # 只删除动画部分的文本（保留"老板正在思考"）
                self.chat_text.delete(f"{self.typing_line_index}.{start_pos}", f"{self.typing_line_index}.end")

                # 添加新的动画文本
                self.typing_animation_index = (self.typing_animation_index + 1) % len(self.TYPING_INDICATOR)
                self.chat_text.insert(f"{self.typing_line_index}.{start_pos}",
                                      self.TYPING_INDICATOR[self.typing_animation_index])

                self.chat_text.see(tk.END)

            self.chat_text.config(state=tk.DISABLED)

        except tk.TclError as e:
            # 处理文本索引异常
            print(f"动画更新错误: {e}")
            self.stop_typing_animation()
            return

        # 继续动画
        if self.animation_running:
            self.typing_animation_id = self.root.after(300, self.animate_typing_indicator)

    def start_typing_animation(self):
        """启动打字动画（带状态管理）"""
        # 停止现有动画
        self.stop_typing_animation()

        try:
            self.animation_running = True
            self.chat_text.config(state=tk.NORMAL)

            # 记录当前的行数
            self.typing_line_index = self.chat_text.index(tk.END + "-1c").split('.')[0]

            # 插入动画文本
            self.chat_text.insert(tk.END, f"{self.BOSS_AVATAR} 老板正在思考 {self.TYPING_INDICATOR[0]}\n")
            self.chat_text.see(tk.END)
            self.chat_text.config(state=tk.DISABLED)

            # 启动动画
            self.typing_animation_id = self.root.after(300, self.animate_typing_indicator)

        except Exception as e:
            print(f"动画启动错误: {e}")
            self.stop_typing_animation()

    def stop_typing_animation(self):
        """停止打字动画（完整清理）"""
        self.animation_running = False
        if self.typing_animation_id:
            self.root.after_cancel(self.typing_animation_id)
            self.typing_animation_id = None

        # 安全删除动画行
        if self.typing_line_index:
            try:
                # 只删除动画行，不影响其他内容
                self.chat_text.config(state=tk.NORMAL)
                self.chat_text.delete(f"{self.typing_line_index}.0", f"{self.typing_line_index}.end+1c")
                self.chat_text.config(state=tk.DISABLED)
            except tk.TclError:
                # 处理已删除的情况
                pass
            finally:
                self.typing_line_index = None

    def print_slowly(self, text, is_user=False):
        """模拟逐字打印效果到文本框，支持颜色区分"""
        if not self.chat_text.winfo_exists():  # 防止窗口关闭后的异常
            return

        self.chat_text.config(state=tk.NORMAL)

        # 根据发送者选择正确的标签和头像
        tag = "user" if is_user else "boss"
        avatar = self.USER_AVATAR if is_user else self.BOSS_AVATAR

        # 添加头像和消息前缀
        self.chat_text.insert(tk.END, f"{avatar} ", tag)

        # 逐字打印消息内容
        for char in text:
            if not self.chat_text.winfo_exists():  # 实时检查窗口状态
                return
            self.chat_text.insert(tk.END, char, tag)
            self.chat_text.see(tk.END)
            self.chat_text.update_idletasks()  # 轻量级刷新，避免卡顿
            # 随机打字速度，增加真实感
            time.sleep(0.01 + random.random() * 0.02)

        # 添加时间戳
        timestamp = time.strftime("%H:%M", time.localtime())
        self.chat_text.insert(tk.END, f"  <{timestamp}>", "timestamp")
        self.chat_text.insert(tk.END, "\n\n")  # 添加额外空行增强可读性
        self.chat_text.config(state=tk.DISABLED)

    def send_message(self):
        """发送用户消息并获取AI回复（带状态保护）"""
        if self.animation_running:
            return

        user_input = self.entry.get().strip()

        # 检查是否退出
        if user_input.lower() in ["退出", "exit"]:
            self.on_closing()
            return

        if not user_input:
            messagebox.showinfo("提示", "请输入有效内容...")
            return

        # 显示用户消息
        self.chat_text.config(state=tk.NORMAL)
        self.print_slowly(user_input, is_user=True)
        self.chat_text.see(tk.END)
        self.chat_text.config(state=tk.DISABLED)
        self.entry.delete(0, tk.END)

        # 清空输入提示
        self.set_input_prompt("")

        # 显示带动画效果的加载提示
        self.start_typing_animation()

        # 启动线程处理API请求，避免界面卡顿
        threading.Thread(
            target=lambda: self.process_ai_response(user_input),
            daemon=True
        ).start()

    def process_ai_response(self, user_input):
        """在后台线程处理AI响应"""
        try:
            response = self.optimize_api_request(user_input)
        except Exception as e:
            response = f"系统错误: {str(e)}"
            print(f"API请求异常: {e}")

        # 在主线程更新UI
        if self.root.winfo_exists():  # 检查窗口是否存在
            self.root.after(0, lambda: self.update_chat(response))

    def update_chat(self, response):
        """更新聊天界面显示AI回复"""
        if not self.root.winfo_exists():  # 检查窗口状态
            return

        # 停止动画
        self.stop_typing_animation()

        # 检查是否退出
        if response.lower() in ["退出", "exit", "quit"]:
            self.on_closing()
            return

        # 显示AI回复
        self.print_slowly(response, is_user=False)

    def set_input_prompt(self, prompt):
        """设置输入框提示信息"""
        if not self.entry.winfo_exists():
            return
        self.entry.delete(0, tk.END)
        self.entry.insert(0, prompt)
        self.entry.config(fg="gray")  # 提示文字设为灰色

    def on_entry_focus(self, event):
        """输入框获得焦点时清除提示"""
        if not self.entry.winfo_exists():
            return
        if self.entry.get() == self.input_prompt:
            self.entry.delete(0, tk.END)
            self.entry.config(fg="black")  # 输入文字设为黑色

    def on_entry_blur(self, event):
        """输入框失去焦点时显示提示"""
        if not self.entry.winfo_exists():
            return
        if not self.entry.get():
            self.set_input_prompt(self.input_prompt)

    def create_ui(self):
        """创建应用程序界面"""
        # 创建主窗口
        self.root = tk.Tk()
        self.root.title("AI模拟聊天界面")
        self.root.geometry("850x700")
        self.root.resizable(True, True)
        self.root.configure(bg="#f0f2f5")  # 更现代的背景色

        # 顶部标题栏
        header_frame = tk.Frame(self.root, bg="#3498db", height=60)
        header_frame.pack(fill=tk.X)

        title_label = tk.Label(
            header_frame,
            text="AI模拟黑心老板",
            font=("SimHei", 18, "bold"),
            bg="#3498db",
            fg="white"
        )
        title_label.pack(pady=10)

        # 聊天文本框优化
        chat_frame = tk.Frame(self.root, padx=20, pady=20, bg="#f0f2f5")
        chat_frame.pack(fill=tk.BOTH, expand=True)

        self.chat_text = scrolledtext.ScrolledText(
            chat_frame,
            wrap=tk.WORD,
            font=("SimHei", 12),
            bg="#f8f9fa",
            bd=0,
            relief=tk.FLAT,
            padx=15,
            pady=15,
            selectbackground="#a8d1ff",
            insertbackground="#555555"
        )
        self.chat_text.pack(fill=tk.BOTH, expand=True)
        self.chat_text.config(state=tk.DISABLED)

        # 添加边框效果
        chat_text_wrapper = tk.Frame(chat_frame, bd=1, relief=tk.SOLID, bg="#d9d9d9")
        chat_text_wrapper.pack(fill=tk.BOTH, expand=True)
        chat_text_wrapper.place(in_=chat_frame, x=20, y=20, relwidth=1.0, relheight=1.0, anchor="nw")
        chat_text_wrapper.lower(self.chat_text)  # 将边框放在文本框后面

        # 优化文本标签样式
        self.chat_text.tag_configure("user", foreground="#3498db", lmargin1=40, lmargin2=40, font=("SimHei", 11))
        self.chat_text.tag_configure("boss", foreground="#e74c3c", lmargin1=40, lmargin2=40, font=("SimHei", 11))
        self.chat_text.tag_configure("timestamp", foreground="#999999", font=("SimHei", 9))
        self.chat_text.tag_configure("welcome", foreground="#555555", justify="center")

        # 添加分隔线
        def add_divider():
            self.chat_text.config(state=tk.NORMAL)
            self.chat_text.insert(tk.END, "\n\n" + "─" * 60 + "\n\n", "welcome")
            self.chat_text.config(state=tk.DISABLED)

        # 显示欢迎信息（优化格式）
        welcome_text = "=" * 50 + "\n AI 模拟黑心老板 - 高级聊天界面\n" + "=" * 50 + "\n\n"
        welcome_text += "ps: 输入内容开始聊天，输入 '退出' 或 'exit' 结束对话\n"
        welcome_text += "tip: 支持128K超长上下文，可进行复杂对话\n" + "-" * 50 + "\n\n"
        welcome_text += "劳累了半天的你，这会终于没人了，刚准备喝口水歇歇，这时，老板来了...\n" + "-" * 50 + "\n\n"

        self.chat_text.config(state=tk.NORMAL)
        self.chat_text.insert(tk.END, welcome_text, "welcome")
        add_divider()
        self.chat_text.see(tk.END)
        self.chat_text.config(state=tk.DISABLED)

        # 输入框和发送按钮优化
        input_frame = tk.Frame(self.root, padx=20, pady=15, bg="#f0f2f5")
        input_frame.pack(fill=tk.X)

        # 创建一个更现代的输入框容器
        entry_container = tk.Frame(input_frame, bg="white", bd=1, relief=tk.SOLID, highlightthickness=0)
        entry_container.pack(fill=tk.X, expand=True, padx=(0, 10), pady=5)

        self.entry = tk.Entry(
            entry_container,
            font=("SimHei", 12),
            bd=0,
            bg="white",
            relief=tk.FLAT,
            insertbackground="#3498db",
            highlightthickness=0
        )
        self.entry.pack(fill=tk.X, expand=True, padx=10, pady=8)
        self.set_input_prompt(self.input_prompt)

        # 绑定焦点事件
        self.entry.bind("<FocusIn>", self.on_entry_focus)
        self.entry.bind("<FocusOut>", self.on_entry_blur)

        # 优化发送按钮样式
        send_button = tk.Button(
            input_frame,
            text="发送",
            font=("SimHei", 12, "bold"),
            command=self.send_message,
            width=8,
            height=1,
            bg="#3498db",
            fg="white",
            activebackground="#2980b9",
            relief=tk.FLAT,
            bd=0,
            cursor="hand2",
            highlightthickness=0
        )
        send_button.pack(side=tk.RIGHT, pady=5, padx=(0, 5))

        # 添加按钮悬停效果
        def on_enter(e):
            send_button['background'] = '#2980b9'

        def on_leave(e):
            send_button['background'] = '#3498db'

        send_button.bind("<Enter>", on_enter)
        send_button.bind("<Leave>", on_leave)

        # 绑定回车键发送消息
        self.entry.bind("<Return>", lambda event: self.send_message())

        # 底部状态栏
        status_frame = tk.Frame(self.root, bg="#e9e9e9", height=25)
        status_frame.pack(fill=tk.X, side=tk.BOTTOM)

        status_label = tk.Label(
            status_frame,
            text="已连接到DeepSeek API | 按回车发送消息",
            font=("SimHei", 9),
            bg="#e9e9e9",
            fg="#555555"
        )
        status_label.pack(side=tk.LEFT, padx=15, pady=5)

        # 窗口关闭事件处理
        def on_closing():
            self.stop_typing_animation()

            if messagebox.askokcancel("退出" or "exit", "确定要结束对话吗?"):
                self.root.destroy()

        self.root.protocol("WM_DELETE_WINDOW", on_closing)

    def start(self):
        """启动应用程序"""
        self.create_ui()
        self.root.mainloop()


# 程序入口
def start():
    app = ChatApp()
    app.start()