import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import hashlib
from datetime import datetime, timedelta
from PIL import Image, ImageTk
import os

# 设置中文字体支持
FONT_FAMILY = ("SimHei", "WenQuanYi Micro Hei", "Heiti TC", "Arial")


class LoginWindow(tk.Tk):
    def __init__(self, login_callback):
        super().__init__()
        self.title("酒店住房管理系统 - 登录")
        self.geometry("400x500")  # 增加窗口高度以容纳图片
        self.resizable(False, False)
        self.login_callback = login_callback

        # 确保中文字体正常显示
        self.option_add("*Font", FONT_FAMILY[0])

        # 检查并加载背景图片
        self.background_image = self._load_background_image()

        # 创建主框架
        self._setup_ui()

    def _load_background_image(self):
        """加载并处理背景图片"""
        try:
            # 尝试查找图片文件
            image_path = self._find_image_path("1.jpg")
            if image_path:
                # 加载并调整图片大小
                img = Image.open(image_path)
                img = img.resize((400, 180), Image.Resampling.LANCZOS)  # 调整图片大小
                return ImageTk.PhotoImage(img)
            else:
                print("背景图片未找到，使用默认样式")
                return None
        except Exception as e:
            print(f"加载图片时出错: {e}")
            return None

    def _find_image_path(self, filename):
        """查找图片文件路径"""
        # 检查当前目录
        if os.path.exists(filename) and os.path.isfile(filename):
            return filename

        # 检查images子目录
        images_dir = os.path.join(os.getcwd(), "images")
        if os.path.exists(images_dir) and os.path.isdir(images_dir):
            image_path = os.path.join(images_dir, filename)
            if os.path.exists(image_path) and os.path.isfile(image_path):
                return image_path

        return None

    def _setup_ui(self):
        """设置用户界面"""
        # 创建主样式
        style = ttk.Style()
        style.configure("TFrame", background="#f0f0f0")
        style.configure("TLabel", background="#f0f0f0", font=(FONT_FAMILY[0], 10))
        style.configure("TButton", font=(FONT_FAMILY[0], 10, "bold"))
        style.configure("Title.TLabel", font=(FONT_FAMILY[0], 18, "bold"), foreground="#2c3e50")
        style.configure("Footer.TLabel", font=(FONT_FAMILY[0], 9), foreground="#7f8c8d")

        # 创建主框架
        main_frame = ttk.Frame(self, padding="20 20 20 20")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # 顶部图片区域
        if self.background_image:
            image_frame = ttk.Frame(main_frame)
            image_frame.pack(fill=tk.X, pady=(0, 15))

            image_label = ttk.Label(image_frame, image=self.background_image)
            image_label.image = self.background_image  # 保持引用
            image_label.pack()

        # 系统标题
        title_frame = ttk.Frame(main_frame)
        title_frame.pack(fill=tk.X, pady=(10, 20))

        ttk.Label(
            title_frame,
            text="酒店住房管理系统",
            style="Title.TLabel"
        ).pack()

        # 登录表单框架 - 使用圆角设计
        form_frame = ttk.Frame(main_frame, padding="20 20 20 20", relief="solid")
        form_frame.pack(fill=tk.BOTH, expand=True)

        # 用户名输入框
        ttk.Label(form_frame, text="用户名:").grid(column=0, row=0, sticky=tk.W, pady=10)
        self.username_var = tk.StringVar()
        username_entry = ttk.Entry(
            form_frame,
            textvariable=self.username_var,
            width=25,
            font=(FONT_FAMILY[0], 10)
        )
        username_entry.grid(column=1, row=0, pady=10, padx=(10, 0))
        username_entry.focus()  # 自动聚焦用户名输入框

        # 密码输入框
        ttk.Label(form_frame, text="密码:").grid(column=0, row=1, sticky=tk.W, pady=10)
        self.password_var = tk.StringVar()
        password_entry = ttk.Entry(
            form_frame,
            textvariable=self.password_var,
            show="*",
            width=25,
            font=(FONT_FAMILY[0], 10)
        )
        password_entry.grid(column=1, row=1, pady=10, padx=(10, 0))

        # 用户类型选择
        ttk.Label(form_frame, text="用户类型:").grid(column=0, row=2, sticky=tk.W, pady=10)
        self.user_type = tk.StringVar(value="frontdesk")

        radio_frame = ttk.Frame(form_frame)
        radio_frame.grid(column=1, row=2, pady=10, sticky=tk.W)

        frontdesk_radio = ttk.Radiobutton(
            radio_frame,
            text="前台",
            variable=self.user_type,
            value="frontdesk"
        )
        frontdesk_radio.pack(side=tk.LEFT, padx=(0, 20))

        admin_radio = ttk.Radiobutton(
            radio_frame,
            text="管理员",
            variable=self.user_type,
            value="admin"
        )
        admin_radio.pack(side=tk.LEFT)

        # 登录按钮
        button_frame = ttk.Frame(form_frame)
        button_frame.grid(column=0, row=3, columnspan=2, pady=20)

        # 自定义按钮样式
        style.configure(
            "Modern.TButton",
            font=(FONT_FAMILY[0], 11, "bold"),
            foreground="white",
            background="#3498db",
            padding=8,
            width=15
        )

        # 按钮悬停效果
        self.bind("<Enter>",
                  lambda e: e.widget.configure(background="#2980b9") if isinstance(e.widget, tk.Button) else None)
        self.bind("<Leave>",
                  lambda e: e.widget.configure(background="#3498db") if isinstance(e.widget, tk.Button) else None)

        login_button = tk.Button(
            button_frame,
            text="登录",
            command=self.login,
            font=(FONT_FAMILY[0], 11, "bold"),
            bg="#3498db",
            fg="white",
            activebackground="#2980b9",
            relief=tk.FLAT,
            padx=20,
            pady=8
        )
        login_button.pack()

        # 版权信息
        footer_frame = ttk.Frame(main_frame)
        footer_frame.pack(fill=tk.X, pady=(10, 0))

        ttk.Label(
            footer_frame,
            text="© 2025 酒店住房管理系统",
            style="Footer.TLabel"
        ).pack()

    def login(self):
        """处理登录逻辑"""
        username = self.username_var.get()
        password = self.password_var.get()
        user_type = self.user_type.get()

        if not username or not password:
            messagebox.showerror("错误", "用户名和密码不能为空")
            return

        # 连接数据库验证用户
        try:
            conn = sqlite3.connect('hotel.db')
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM users WHERE username = ? AND password_hash = ?",
                (username, self.hash_password(password))
            )
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
        except Exception as e:
            messagebox.showerror("数据库错误", f"登录验证失败: {str(e)}")

    def hash_password(self, password):
        """哈希密码"""
        return hashlib.sha256(password.encode()).hexdigest()

