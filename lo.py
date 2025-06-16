import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import hashlib
from datetime import datetime, timedelta
from tkinter import *
from PIL import Image, ImageTk


# ==== LoginWindow ====
class LoginWindow(tk.Tk):
    def __init__(self, login_callback):
        super().__init__()
        self.title("酒店住房管理系统 - 登录")
        self.geometry("400x300")
        self.resizable(False, False)
        self.login_callback = login_callback

        # 加载背景图片
        try:
            # 尝试加载背景图片
            background_image = Image.open("1.jpg")
            # 调整图片大小以适应窗口
            background_image = background_image.resize((400, 300), Image.ANTIALIAS)
            self.background_photo = ImageTk.PhotoImage(background_image)

            # 创建背景标签
            background_label = tk.Label(self, image=self.background_photo)
            background_label.place(x=0, y=0, relwidth=1, relheight=1)

            # 设置透明背景
            self.configure(bg='white')
        except Exception as e:
            # 如果图片加载失败，使用默认背景色
            self.configure(bg="#f0f0f0")

        # 创建主框架...
        # 以下代码保持不变...
        style = ttk.Style()
        style.configure("TFrame", background="#f0f0f0")
        style.configure("TLabel", background="#f0f0f0", font=("Arial", 10))
        style.configure("TButton", font=("Arial", 10, "bold"))
        style.configure("Title.TLabel", font=("Arial", 18, "bold"), foreground="#2c3e50")
        style.configure("Footer.TLabel", font=("Arial", 9), foreground="#7f8c8d")
        # 主框架居中放置
        frame = ttk.Frame(self, padding="30 30 30 30", relief="solid")
        frame.place(relx=0.5, rely=0.5, anchor="center")
        # 系统标题，使用更大更突出的字体
        ttk.Label(frame, text="酒店住房管理系统", style="Title.TLabel").grid(
            column=0, row=0, columnspan=2, pady=20)

        # 用户名输入框，增加内边距和高度
        ttk.Label(frame, text="用户名:").grid(column=0, row=1, sticky=tk.W, pady=8)
        self.username_var = tk.StringVar()
        username_entry = ttk.Entry(frame, textvariable=self.username_var, width=25, font=("Arial", 10))
        username_entry.grid(column=1, row=1, pady=8, padx=(5, 0))
        username_entry.focus()  # 自动聚焦用户名输入框

        # 密码输入框
        ttk.Label(frame, text="密码:").grid(column=0, row=2, sticky=tk.W, pady=8)
        self.password_var = tk.StringVar()
        ttk.Entry(frame, textvariable=self.password_var, show="*", width=25, font=("Arial", 10)).grid(
            column=1, row=2, pady=8, padx=(5, 0))

        # 用户类型选择，使用更美观的单选按钮布局
        ttk.Label(frame, text="用户类型:").grid(column=0, row=3, sticky=tk.W, pady=8)
        self.user_type = tk.StringVar(value="frontdesk")

        # 创建单选按钮框架使按钮居中
        radio_frame = ttk.Frame(frame)
        radio_frame.grid(column=1, row=3, pady=8)

        ttk.Radiobutton(radio_frame, text="前台", variable=self.user_type,
                        value="frontdesk").pack(side=tk.LEFT, padx=(0, 20))
        ttk.Radiobutton(radio_frame, text="管理员", variable=self.user_type,
                        value="admin").pack(side=tk.LEFT)

        # 登录按钮，使用更现代的样式，并居中放置
        style.configure("Login.TButton", font=("Arial", 11, "bold"), background="#3498db")
        login_button = ttk.Button(frame, text="登录", command=self.login, width=15, style="Login.TButton")
        login_button.grid(column=0, row=4, columnspan=2, pady=20)

        # 自定义按钮颜色和悬停效果
        login_button_frame = ttk.Frame(frame)
        login_button_frame.grid(column=0, row=4, columnspan=2, pady=20)

        login_btn = tk.Button(login_button_frame, text="登录", command=self.login,
                              width=15, font=("Arial", 11, "bold"),
                              bg="#3498db", fg="white", activebackground="#2980b9",
                              relief=tk.RAISED, borderwidth=1)
        login_btn.pack()

        # 版权信息，使用更精致的字体
        ttk.Label(self, text="© 2025 酒店住房管理系统", style="Footer.TLabel").place(relx=0.5, rely=0.95,
                                                                                     anchor="center")

    def login(self):
        username = self.username_var.get()
        password = self.password_var.get()
        user_type = self.user_type.get()

        if not username or not password:
            messagebox.showerror("错误", "用户名和密码不能为空")
            return

        conn = sqlite3.connect('hotel.db')
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username = ? AND password_hash = ?",
                       (username, self.hash_password(password)))
        user = cursor.fetchone()
        conn.close()

        if user:
            if (user_type == "admin" and user[3] == "admin") or (
                    user_type == "frontdesk" and user[3] in ["admin", "frontdesk"]):
                self.login_callback({
                    'user_id': user[0],
                    'username': user[1],
                    'role': user[3]
                })
                self.destroy()
            else:
                messagebox.showerror("错误", "权限不足，无法登录该系统")
        else:
            messagebox.showerror("错误", "用户名或密码错误")

    def hash_password(self, password):
        return hashlib.sha256(password.encode()).hexdigest()

