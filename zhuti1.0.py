import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import hashlib
from datetime import datetime, timedelta

import ai4,lo


# ==== 数据库====
def init_db():
    conn = sqlite3.connect('hotel.db')
    cursor = conn.cursor()
    # 创建 users 表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            password_hash TEXT,
            role TEXT
        )
    ''')
    # 默认 admin 账户
    cursor.execute("SELECT COUNT(*) FROM users WHERE role = 'admin'")
    count = cursor.fetchone()[0]
    if count == 0:
        password_hash = hashlib.sha256("admin123".encode()).hexdigest()
        cursor.execute("INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)",
                       ("admin", password_hash, "admin"))
        conn.commit()
    conn.close()
# ==== 结束 ====

# ==== HotelManagementSystem ====
class HotelManagementSystem:
    def __init__(self, root, user):
        self.root = root
        self.root.title("酒店住房管理系统")
        self.root.geometry("1000x600")
        self.current_user = user
        self.conn = sqlite3.connect('hotel.db')
        self.create_tables()
        self.setup_ui()
        self.update_status(f"欢迎，{user['username']} ({user['role']})")

    def hash_password(self, password):
        return hashlib.sha256(password.encode()).hexdigest()

    def create_tables(self):
        conn = sqlite3.connect('hotel.db')
        cursor = conn.cursor()

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS rooms (
                room_number INTEGER PRIMARY KEY,
                room_type TEXT,
                price REAL,
                status TEXT,
                clean_status TEXT
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS customers (
                customer_id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                contact TEXT,
                id_card TEXT,
                points INTEGER DEFAULT 0
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS reservations (
                reservation_id INTEGER PRIMARY KEY AUTOINCREMENT,
                room_number INTEGER,
                customer_id INTEGER,
                check_in_date TEXT,
                check_out_date TEXT,
                status TEXT,
                FOREIGN KEY (room_number) REFERENCES rooms(room_number),
                FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS transactions (
                transaction_id INTEGER PRIMARY KEY AUTOINCREMENT,
                reservation_id INTEGER,
                amount REAL,
                transaction_date TEXT,
                description TEXT,
                FOREIGN KEY (reservation_id) REFERENCES reservations(reservation_id)
            )
        ''')

        conn.commit()
        conn.close()

    def setup_ui(self):
        # 设置窗口风格和主题色
        self.root.configure(bg="#f5f5f5")
        self.root.geometry("1000x980")  # 增大窗口尺寸
        style = ttk.Style()
        style.configure("TFrame", background="#f5f5f5")
        style.configure("TLabel", background="#f5f5f5")
        style.configure("Status.TLabel", background="#f0f0f0", foreground="#555555", font=("Arial", 9))
        style.configure("Header.TLabel", font=("SimHei", 24, "bold"), foreground="#2c3e50")  # 配置标题样式

        # 创建菜单栏并自定义菜单样式
        menubar = tk.Menu(self.root, bg="#ffffff", fg="#333333", activebackground="#3498db",activeforeground="white", relief=tk.FLAT, bd=0)
        self.root.config(menu=menubar)

        # 创建主框架，添加边框和内边距
        main_container = ttk.Frame(self.root, padding=15, borderwidth=2, relief=tk.GROOVE)
        main_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # 欢迎界面部分
        welcome_frame = ttk.Frame(main_container, padding=20)
        welcome_frame.pack(fill=tk.X, pady=(10, 20))

        # 添加酒店图标/logo
        hotel_label = ttk.Label(welcome_frame, text="🏨", font=("Arial", 48), background="#f5f5f5")
        hotel_label.pack(pady=5)

        # 为图标添加点击事件，调用AI函数
        hotel_label.bind("<Button-1>", lambda event: self.call_ai_function())

        # 欢迎标题
        title_label = ttk.Label(welcome_frame, text="欢迎使用酒店住房管理系统", style="Header.TLabel")
        title_label.pack(pady=10)

        # 用户信息
        user_info_frame = ttk.Frame(welcome_frame)
        user_info_frame.pack(pady=10)

        ttk.Label(user_info_frame, text=f"当前用户: {self.current_user['username']}",
                  font=("Arial", 12)).pack()

        role_text = "管理员" if self.current_user['role'] == 'admin' else "前台"
        ttk.Label(user_info_frame, text=f"用户角色: {role_text}",
                  font=("Arial", 12)).pack(pady=5)

        # 功能按钮区域（直接放在欢迎界面下方）
        modules_container = ttk.Frame(main_container, padding=10)
        modules_container.pack(fill=tk.BOTH, expand=True, pady=10)

        # 按钮样式
        button_style = {
            "width": 16,  # 增加按钮宽度
            "height": 2,
            "font": ("Arial", 10, "bold"),
            "bg": "#3498db",
            "fg": "white",
            "activebackground": "#2980b9",
            "activeforeground": "white",
            "relief": tk.RAISED,
            "borderwidth": 1
        }

        # 创建功能模块部分
        # 1. 房间管理模块
        room_frame = ttk.Frame(modules_container, padding=10, borderwidth=1, relief=tk.GROOVE)
        room_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew", ipadx=5, ipady=5)

        ttk.Label(room_frame, text="房间管理", font=("Arial", 12, "bold")).pack(pady=(0, 10))

        tk.Button(room_frame, text="添加房间", command=self.add_room, **button_style).pack(fill=tk.X, pady=3)
        tk.Button(room_frame, text="修改房间信息", command=self.modify_room, **button_style).pack(fill=tk.X, pady=3)
        tk.Button(room_frame, text="查看所有房间", command=self.view_all_rooms, **button_style).pack(fill=tk.X, pady=3)

        # 2. 客户管理模块
        customer_frame = ttk.Frame(modules_container, padding=10, borderwidth=1, relief=tk.GROOVE)
        customer_frame.grid(row=0, column=1, padx=10, pady=10, sticky="nsew", ipadx=5, ipady=5)

        ttk.Label(customer_frame, text="客户管理", font=("Arial", 12, "bold")).pack(pady=(0, 10))

        tk.Button(customer_frame, text="添加客户", command=self.add_customer, **button_style).pack(fill=tk.X, pady=3)
        tk.Button(customer_frame, text="修改客户信息", command=self.modify_customer, **button_style).pack(fill=tk.X,
                                                                                                          pady=3)
        tk.Button(customer_frame, text="查看客户列表", command=self.view_customers, **button_style).pack(fill=tk.X,
                                                                                                         pady=3)

        # 3. 预订管理模块
        reservation_frame = ttk.Frame(modules_container, padding=10, borderwidth=1, relief=tk.GROOVE)
        reservation_frame.grid(row=0, column=2, padx=10, pady=10, sticky="nsew", ipadx=5, ipady=5)

        ttk.Label(reservation_frame, text="预订管理", font=("Arial", 12, "bold")).pack(pady=(0, 10))

        tk.Button(reservation_frame, text="新增预订", command=self.add_reservation, **button_style).pack(fill=tk.X,
                                                                                                         pady=3)
        tk.Button(reservation_frame, text="修改预订", command=self.modify_reservation, **button_style).pack(fill=tk.X,
                                                                                                            pady=3)
        tk.Button(reservation_frame, text="取消预订", command=self.cancel_reservation, **button_style).pack(fill=tk.X,
                                                                                                            pady=3)
        tk.Button(reservation_frame, text="查看预订列表", command=self.view_reservations, **button_style).pack(
            fill=tk.X, pady=3)

        # 4. 入住退房模块
        check_frame = ttk.Frame(modules_container, padding=10, borderwidth=1, relief=tk.GROOVE)
        check_frame.grid(row=1, column=0, padx=10, pady=10, sticky="nsew", ipadx=5, ipady=5)

        ttk.Label(check_frame, text="入住退房", font=("Arial", 12, "bold")).pack(pady=(0, 10))

        tk.Button(check_frame, text="办理入住", command=self.check_in, **button_style).pack(fill=tk.X, pady=3)
        tk.Button(check_frame, text="办理退房", command=self.check_out, **button_style).pack(fill=tk.X, pady=3)

        # 管理员专属模块
        if self.current_user['role'] == 'admin':
            # 5. 财务管理模块
            finance_frame = ttk.Frame(modules_container, padding=10, borderwidth=1, relief=tk.GROOVE)
            finance_frame.grid(row=1, column=1, padx=10, pady=10, sticky="nsew", ipadx=5, ipady=5)

            ttk.Label(finance_frame, text="财务管理", font=("Arial", 12, "bold")).pack(pady=(0, 10))

            tk.Button(finance_frame, text="查看收入统计", command=self.view_finance, **button_style).pack(fill=tk.X,
                                                                                                          pady=3)
            tk.Button(finance_frame, text="添加收费项目", command=self.add_transaction, **button_style).pack(fill=tk.X,
                                                                                                             pady=3)
            tk.Button(finance_frame, text="查看交易记录", command=self.view_transactions, **button_style).pack(
                fill=tk.X, pady=3)

            # 6. 系统管理模块
            system_frame = ttk.Frame(modules_container, padding=10, borderwidth=1, relief=tk.GROOVE)
            system_frame.grid(row=1, column=2, padx=10, pady=10, sticky="nsew", ipadx=5, ipady=5)

            ttk.Label(system_frame, text="系统管理", font=("Arial", 12, "bold")).pack(pady=(0, 10))

            tk.Button(system_frame, text="添加用户", command=self.add_user, **button_style).pack(fill=tk.X, pady=3)
            tk.Button(system_frame, text="修改用户权限", command=self.modify_user, **button_style).pack(fill=tk.X,
                                                                                                        pady=3)
            tk.Button(system_frame, text="查看用户列表", command=self.view_users, **button_style).pack(fill=tk.X,
                                                                                                       pady=3)
        else:
            # 非管理员可以看到的其他功能（保持界面平衡）
            file_frame = ttk.Frame(modules_container, padding=10, borderwidth=1, relief=tk.GROOVE)
            file_frame.grid(row=1, column=1, padx=10, pady=10, sticky="nsew", ipadx=5, ipady=5)

            ttk.Label(file_frame, text="系统操作", font=("Arial", 12, "bold")).pack(pady=(0, 10))

            tk.Button(file_frame, text="退出系统", command=self.root.quit, **button_style).pack(fill=tk.X, pady=3)

        # 添加退出按钮框架（对管理员）
        if self.current_user['role'] == 'admin':
            exit_frame = ttk.Frame(modules_container, padding=10)
            exit_frame.grid(row=2, column=1, padx=10, pady=10, sticky="n")

            tk.Button(exit_frame, text="退出系统", command=self.root.quit,
                      width=16, height=2, font=("Arial", 10, "bold"),
                      bg="#e74c3c", fg="white",
                      activebackground="#c0392b", activeforeground="white").pack(pady=3)

        # 状态栏，使用灰色背景和细边框
        status_frame = ttk.Frame(self.root, relief=tk.GROOVE, borderwidth=1)
        status_frame.pack(side=tk.BOTTOM, fill=tk.X)

        self.status_bar = ttk.Label(status_frame, text="就绪", style="Status.TLabel", anchor=tk.W)
        self.status_bar.pack(side=tk.LEFT, fill=tk.X, padx=5, pady=2)

        # 添加当前日期时间到状态栏
        import datetime
        date_label = ttk.Label(status_frame,
                               text=f"日期: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}",
                               style="Status.TLabel")
        date_label.pack(side=tk.RIGHT, padx=10, pady=2)

        # 配置网格权重，使按钮区域能够自适应窗口大小
        for i in range(3):
            modules_container.columnconfigure(i, weight=1)
        for i in range(2):
            modules_container.rowconfigure(i, weight=1)

    # 添加调用AI函数的方法
    def call_ai_function(self):
        # 导入py文件中的m函数
        try:
            # 调用函数并获取结果
            result = ai4.start()
            # 可以在这里处理结果，例如显示在状态栏或弹窗中
            self.status_bar.config(text=f"AI功能已调用: {result}")
            print(f"AI返回结果: {result}")
        except ImportError:
            self.status_bar.config(text="错误: 无法导入ai.py模块")
            print("错误: 无法导入ai.py模块")
        except Exception as e:
            self.status_bar.config(text=f"AI调用错误: {str(e)}")
            print(f"AI调用错误: {str(e)}")

    def update_status(self, message):
        self.status_bar.config(text=message)
        self.root.update_idletasks()

    # 功能方法
    def add_room(self):
        # 创建添加房间的顶层窗口
        add_room_win = tk.Toplevel(self.root)
        add_room_win.title("添加房间")
        add_room_win.geometry("300x220")

        # 房间号标签与输入框
        ttk.Label(add_room_win, text="房间号:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        room_number_entry = ttk.Entry(add_room_win)
        room_number_entry.grid(row=0, column=1, padx=5, pady=5)

        # 房间类型标签与输入框
        ttk.Label(add_room_win, text="房间类型:").grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
        room_type_entry = ttk.Entry(add_room_win)
        room_type_entry.grid(row=1, column=1, padx=5, pady=5)

        # 价钱标签与输入框
        ttk.Label(add_room_win, text="价钱(元):").grid(row=2, column=0, padx=5, pady=5, sticky=tk.W)
        price_entry = ttk.Entry(add_room_win)
        price_entry.grid(row=2, column=1, padx=5, pady=5)

        # 清洁状态标签与输入框
        ttk.Label(add_room_win, text="清洁状态:").grid(row=3, column=0, padx=5, pady=5, sticky=tk.W)
        clean_status_entry = ttk.Entry(add_room_win)
        clean_status_entry.grid(row=3, column=1, padx=5, pady=5)

        def save_room():
            room_number = room_number_entry.get()
            room_type = room_type_entry.get()
            price = price_entry.get()
            clean_status = clean_status_entry.get()

            # 校验必填项
            if not (room_number and room_type and price and clean_status):
                messagebox.showerror("错误", "房间号、房间类型、价钱、清洁状态均为必填项")
                return

            # 校验房间号为整数
            if not room_number.isdigit():
                messagebox.showerror("错误", "房间号必须为整数")
                return

            # 校验价钱为数字
            try:
                float(price)
            except ValueError:
                messagebox.showerror("错误", "价钱必须为有效数字（如：300.0）")
                return

            try:
                conn = sqlite3.connect('hotel.db')
                cursor = conn.cursor()

                # 检查房间号是否已存在
                cursor.execute("SELECT * FROM rooms WHERE room_number = ?", (room_number,))
                if cursor.fetchone():
                    messagebox.showerror("错误", "该房间号已存在")
                    return

                # 插入房间数据，使用用户输入的清洁状态
                cursor.execute(
                    "INSERT INTO rooms (room_number, room_type, price, status, clean_status) "
                    "VALUES (?, ?, ?, '空闲', ?)",
                    (room_number, room_type, price, clean_status)
                )
                conn.commit()
                messagebox.showinfo("成功", "房间添加成功")
                add_room_win.destroy()
            except Exception as e:
                messagebox.showerror("错误", f"添加失败：{str(e)}")
            finally:
                if 'conn' in locals():
                    conn.close()

        ttk.Button(add_room_win, text="保存", command=save_room).grid(row=4, column=0, columnspan=2, pady=10)

    def modify_room(self):
        # 创建修改房间信息的顶层窗口
        modify_room_win = tk.Toplevel(self.root)
        modify_room_win.title("修改房间信息")
        modify_room_win.geometry("400x250")

        # 房间号标签与输入框（用于查询要修改的房间）
        ttk.Label(modify_room_win, text="房间号:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        room_number_entry = ttk.Entry(modify_room_win)
        room_number_entry.grid(row=0, column=1, padx=5, pady=5)

        def query_room():
            room_number = room_number_entry.get()
            if not room_number.isdigit():
                messagebox.showerror("错误", "请输入有效的房间号（整数）")
                return

            try:
                conn = sqlite3.connect('hotel.db')
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT room_type, price, status, clean_status FROM rooms WHERE room_number = ?",
                    (room_number,)
                )
                result = cursor.fetchone()

                if result:
                    # 填充现有数据到输入框
                    room_type_entry.delete(0, tk.END)
                    room_type_entry.insert(0, result[0])
                    price_entry.delete(0, tk.END)
                    price_entry.insert(0, result[1])
                    # 修复：添加清洁状态的填充
                    clean_status_entry.delete(0, tk.END)
                    clean_status_entry.insert(0, result[3])
                else:
                    messagebox.showerror("错误", "未找到该房间号对应的房间")
            finally:
                if 'conn' in locals():
                    conn.close()

        ttk.Button(modify_room_win, text="查询", command=query_room).grid(row=0, column=2, padx=5, pady=5)

        # 房间类型标签与输入框（可修改）
        ttk.Label(modify_room_win, text="房间类型:").grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
        room_type_entry = ttk.Entry(modify_room_win)
        room_type_entry.grid(row=1, column=1, padx=5, pady=5)

        # 价钱标签与输入框（可修改）
        ttk.Label(modify_room_win, text="价钱(元):").grid(row=2, column=0, padx=5, pady=5, sticky=tk.W)
        price_entry = ttk.Entry(modify_room_win)
        price_entry.grid(row=2, column=1, padx=5, pady=5)

        # 清洁状态标签与输入框（可修改）
        ttk.Label(modify_room_win, text="清洁状态:").grid(row=3, column=0, padx=5, pady=5, sticky=tk.W)
        clean_status_entry = ttk.Entry(modify_room_win)  # 修正变量名，避免与price_entry冲突
        clean_status_entry.grid(row=3, column=1, padx=5, pady=5)

        def save_modification():
            room_number = room_number_entry.get()
            if not room_number.isdigit():
                messagebox.showerror("错误", "请输入有效的房间号（整数）")
                return

            room_type = room_type_entry.get()
            price = price_entry.get()
            clean_status = clean_status_entry.get()  # 获取清洁状态

            # 校验所有必填项
            if not (room_type and price and clean_status):
                messagebox.showerror("错误", "房间类型、价钱和清洁状态均为必填项")
                return

            try:
                float(price)  # 校验价钱格式
            except ValueError:
                messagebox.showerror("错误", "价钱必须为有效数字（如：300.0）")
                return

            try:
                conn = sqlite3.connect('hotel.db')
                cursor = conn.cursor()
                # 更新房间信息，包括清洁状态
                cursor.execute(
                    "UPDATE rooms SET room_type = ?, price = ?, clean_status = ? WHERE room_number = ?",
                    (room_type, price, clean_status, room_number)
                )
                if cursor.rowcount == 0:
                    messagebox.showerror("错误", "未找到该房间号对应的房间，修改失败")
                else:
                    conn.commit()
                    messagebox.showinfo("成功", "房间信息修改成功")
                    modify_room_win.destroy()
            except Exception as e:
                messagebox.showerror("错误", f"修改失败：{str(e)}")
            finally:
                if 'conn' in locals():
                    conn.close()

        ttk.Button(modify_room_win, text="保存修改", command=save_modification).grid(row=4, column=0, columnspan=2,
                                                                                     pady=10)

    def view_all_rooms(self):
        # 创建查看房间列表的顶层窗口
        view_rooms_win = tk.Toplevel(self.root)
        view_rooms_win.title("房间列表")
        view_rooms_win.geometry("1000x600")

        # 创建树状视图展示房间数据
        tree = ttk.Treeview(view_rooms_win, columns=("房间号", "房间类型", "价钱", "状态", "清洁状态"),
                            show='headings', selectmode='browse')
        tree.heading("房间号", text="房间号")
        tree.heading("房间类型", text="房间类型")
        tree.heading("价钱", text="价钱(元)")
        tree.heading("状态", text="状态")
        tree.heading("清洁状态", text="清洁状态")
        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # 添加滚动条
        scrollbar = ttk.Scrollbar(view_rooms_win, orient='vertical', command=tree.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        tree.configure(yscrollcommand=scrollbar.set)

        try:
            conn = sqlite3.connect('hotel.db')
            cursor = conn.cursor()
            # 查询房间表的所有字段
            cursor.execute("SELECT room_number, room_type, price, status, clean_status FROM rooms")
            results = cursor.fetchall()
            for row in results:
                tree.insert('', tk.END, values=row)
        finally:
            if 'conn' in locals():
                conn.close()


    # 客户管理相关实现
    def add_customer(self):
        # 创建添加客户的顶层窗口
        add_customer_win = tk.Toplevel(self.root)
        add_customer_win.title("添加客户")
        add_customer_win.geometry("300x220")

        # 姓名标签与输入框
        ttk.Label(add_customer_win, text="姓名:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        name_entry = ttk.Entry(add_customer_win)
        name_entry.grid(row=0, column=1, padx=5, pady=5)

        # 联系方式标签与输入框
        ttk.Label(add_customer_win, text="联系方式:").grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
        contact_entry = ttk.Entry(add_customer_win)
        contact_entry.grid(row=1, column=1, padx=5, pady=5)

        # 身份证号标签与输入框
        ttk.Label(add_customer_win, text="身份证号:").grid(row=2, column=0, padx=5, pady=5, sticky=tk.W)
        id_card_entry = ttk.Entry(add_customer_win)
        id_card_entry.grid(row=2, column=1, padx=5, pady=5)

        def check_id(sid):
            import re
            pattern = r'^[1-9]\d{5}(18|19|([23]\d))\d{2}((0[1-9])|(10|11|12))(([0-2][1-9])|10|20|30|31)\d{3}[0-9Xx]$'
            if re.match(pattern, sid):
                return True
            else:
                return False

        def save_customer():
            name = name_entry.get()
            contact = contact_entry.get()
            id_card = id_card_entry.get()

            if not (name and contact and id_card):
                messagebox.showerror("错误", "姓名、联系方式、身份证号均为必填项")
                return

            if not check_id(id_card):
                messagebox.showwarning("警告", "请正确输入身份证号！")
                id_card_entry.delete(0, tk.END)
                return

            try:
                conn = sqlite3.connect('hotel.db')
                cursor = conn.cursor()
                cursor.execute("INSERT INTO customers (name, contact, id_card) VALUES (?, ?, ?)",
                               (name, contact, id_card))
                conn.commit()
                messagebox.showinfo("成功", "客户添加成功")
                add_customer_win.destroy()
            except sqlite3.IntegrityError:
                messagebox.showerror("错误", "该身份证号已存在")
            finally:
                conn.close()

        ttk.Button(add_customer_win, text="保存", command=save_customer).grid(row=3, column=0, columnspan=2, pady=10)

    def modify_customer(self):
        # 创建修改客户信息的顶层窗口
        modify_customer_win = tk.Toplevel(self.root)
        modify_customer_win.title("修改客户信息")
        modify_customer_win.geometry("400x250")

        # 客户ID标签与输入框，用于查询要修改的客户
        ttk.Label(modify_customer_win, text="客户ID:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        customer_id_entry = ttk.Entry(modify_customer_win)
        customer_id_entry.grid(row=0, column=1, padx=5, pady=5)

        def query_customer():
            customer_id = customer_id_entry.get()
            if not customer_id.isdigit():
                messagebox.showerror("错误", "请输入有效的客户ID")
                return
            try:
                conn = sqlite3.connect('hotel.db')
                cursor = conn.cursor()
                cursor.execute("SELECT name, contact, id_card FROM customers WHERE customer_id = ?",
                               (customer_id,))
                result = cursor.fetchone()
                if result:
                    name_entry.delete(0, tk.END)
                    name_entry.insert(0, result[0])
                    contact_entry.delete(0, tk.END)
                    contact_entry.insert(0, result[1])
                    id_card_entry.delete(0, tk.END)
                    id_card_entry.insert(0, result[2])
                else:
                    messagebox.showerror("错误", "未找到该客户ID对应的客户")
            finally:
                conn.close()

        ttk.Button(modify_customer_win, text="查询", command=query_customer).grid(row=0, column=2, padx=5, pady=5)

        # 姓名标签与输入框（查询后展示并可修改）
        ttk.Label(modify_customer_win, text="姓名:").grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
        name_entry = ttk.Entry(modify_customer_win)
        name_entry.grid(row=1, column=1, padx=5, pady=5)

        # 联系方式标签与输入框（查询后展示并可修改）
        ttk.Label(modify_customer_win, text="联系方式:").grid(row=2, column=0, padx=5, pady=5, sticky=tk.W)
        contact_entry = ttk.Entry(modify_customer_win)
        contact_entry.grid(row=2, column=1, padx=5, pady=5)

        # 身份证号标签与输入框（查询后展示并可修改）
        ttk.Label(modify_customer_win, text="身份证号:").grid(row=3, column=0, padx=5, pady=5, sticky=tk.W)
        id_card_entry = ttk.Entry(modify_customer_win)
        id_card_entry.grid(row=3, column=1, padx=5, pady=5)

        def save_modification():
            customer_id = customer_id_entry.get()
            if not customer_id.isdigit():
                messagebox.showerror("错误", "请输入有效的客户ID")
                return
            name = name_entry.get()
            contact = contact_entry.get()
            id_card = id_card_entry.get()
            if not (name and contact and id_card):
                messagebox.showerror("错误", "姓名、联系方式、身份证号均为必填项")
                return
            try:
                conn = sqlite3.connect('hotel.db')
                cursor = conn.cursor()
                cursor.execute("UPDATE customers SET name = ?, contact = ?, id_card = ? WHERE customer_id = ?",
                               (name, contact, id_card, customer_id))
                if cursor.rowcount == 0:
                    messagebox.showerror("错误", "未找到该客户ID对应的客户，修改失败")
                else:
                    conn.commit()
                    messagebox.showinfo("成功", "客户信息修改成功")
                    modify_customer_win.destroy()
            finally:
                conn.close()

        ttk.Button(modify_customer_win, text="保存修改", command=save_modification).grid(row=4, column=0, columnspan=2,
                                                                                         pady=10)

    def view_customers(self):
        # 创建查看客户列表的顶层窗口
        view_customers_win = tk.Toplevel(self.root)
        view_customers_win.title("客户列表")
        view_customers_win.geometry("1000x400")

        # 创建树状视图展示客户数据
        tree = ttk.Treeview(view_customers_win, columns=("客户ID", "姓名", "联系方式", "身份证号", "积分"),
                            show='headings', selectmode='browse')
        tree.heading("客户ID", text="客户ID")
        tree.heading("姓名", text="姓名")
        tree.heading("联系方式", text="联系方式")
        tree.heading("身份证号", text="身份证号")
        tree.heading("积分", text="积分")
        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # 添加滚动条
        scrollbar = ttk.Scrollbar(view_customers_win, orient='vertical', command=tree.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        tree.configure(yscrollcommand=scrollbar.set)

        try:
            conn = sqlite3.connect('hotel.db')
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM customers")
            results = cursor.fetchall()
            for row in results:
                tree.insert('', tk.END, values=row)
        finally:
            conn.close()

    def add_reservation(self):
        # 创建添加预订的顶层窗口
        add_reservation_win = tk.Toplevel(self.root)  # 这里假设类中有 self.root 表示主窗口，若不是这种结构，根据实际情况调整
        add_reservation_win.title("新增预订")
        add_reservation_win.geometry("400x350")

        # 客户ID标签与输入框
        ttk.Label(add_reservation_win, text="客户ID:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        customer_id_entry = ttk.Entry(add_reservation_win)
        customer_id_entry.grid(row=0, column=1, padx=5, pady=5)

        # 查询客户按钮
        def query_customer():
            customer_id = customer_id_entry.get()
            if not customer_id.isdigit():
                messagebox.showerror("错误", "请输入有效的客户ID")
                return
            try:
                conn = sqlite3.connect('hotel.db')
                cursor = conn.cursor()
                cursor.execute("SELECT name FROM customers WHERE customer_id = ?", (customer_id,))
                result = cursor.fetchone()
                if result:
                    customer_name_label.config(text=f"客户姓名: {result[0]}")
                else:
                    messagebox.showerror("错误", "未找到该客户ID对应的客户")
            finally:
                conn.close()

        ttk.Button(add_reservation_win, text="查询客户", command=query_customer).grid(row=0, column=2, padx=5, pady=5)
        customer_name_label = ttk.Label(add_reservation_win, text="客户姓名: ")
        customer_name_label.grid(row=1, column=0, columnspan=3, padx=5, pady=5, sticky=tk.W)

        # 房间号标签与输入框
        ttk.Label(add_reservation_win, text="房间号:").grid(row=2, column=0, padx=5, pady=5, sticky=tk.W)
        room_number_entry = ttk.Entry(add_reservation_win)
        room_number_entry.grid(row=2, column=1, padx=5, pady=5)

        # 查询房间按钮
        def query_room():
            room_number = room_number_entry.get()
            if not room_number.isdigit():
                messagebox.showerror("错误", "请输入有效的房间号")
                return
            try:
                conn = sqlite3.connect('hotel.db')
                cursor = conn.cursor()
                cursor.execute("SELECT room_type, price, status FROM rooms WHERE room_number = ?", (room_number,))
                result = cursor.fetchone()
                if result:
                    room_info_label.config(text=f"房间类型: {result[0]}, 价格: {result[1]}, 状态: {result[2]}")
                else:
                    messagebox.showerror("错误", "未找到该房间号对应的房间")
            finally:
                conn.close()

        ttk.Button(add_reservation_win, text="查询房间", command=query_room).grid(row=2, column=2, padx=5, pady=5)
        room_info_label = ttk.Label(add_reservation_win, text="房间信息: ")
        room_info_label.grid(row=3, column=0, columnspan=3, padx=5, pady=5, sticky=tk.W)

        # 入住日期
        ttk.Label(add_reservation_win, text="入住日期:").grid(row=4, column=0, padx=5, pady=5, sticky=tk.W)
        check_in_entry = ttk.Entry(add_reservation_win)
        check_in_entry.grid(row=4, column=1, padx=5, pady=5)
        check_in_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))

        # 退房日期
        ttk.Label(add_reservation_win, text="退房日期:").grid(row=5, column=0, padx=5, pady=5, sticky=tk.W)
        check_out_entry = ttk.Entry(add_reservation_win)
        check_out_entry.grid(row=5, column=1, padx=5, pady=5)
        check_out_entry.insert(0, (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d"))

        def save_reservation():
            customer_id = customer_id_entry.get()
            room_number = room_number_entry.get()
            check_in_date = check_in_entry.get()
            check_out_date = check_out_entry.get()

            if not (customer_id.isdigit() and room_number.isdigit()):
                messagebox.showerror("错误", "客户ID和房间号必须为数字")
                return

            # 验证日期格式
            try:
                datetime.strptime(check_in_date, "%Y-%m-%d")
                datetime.strptime(check_out_date, "%Y-%m-%d")
            except ValueError:
                messagebox.showerror("错误", "日期格式不正确，请使用YYYY-MM-DD格式")
                return

            # 验证退房日期晚于入住日期
            if check_out_date <= check_in_date:
                messagebox.showerror("错误", "退房日期必须晚于入住日期")
                return

            try:
                # 解析日期
                in_date = datetime.strptime(check_in_date, "%Y-%m-%d")
                out_date = datetime.strptime(check_out_date, "%Y-%m-%d")

                # 检查日期合理性
                if in_date >= out_date:
                    messagebox.showerror("错误", "退房日期必须晚于入住日期")
                    return

                conn = sqlite3.connect('hotel.db')
                cursor = conn.cursor()


                # 检查房间是否存在
                cursor.execute("SELECT room_number FROM rooms WHERE room_number = ?", (room_number,))
                if not cursor.fetchone():
                    messagebox.showerror("错误", "该房间不存在")
                    return

                # 检查房间状态

                # 检查房间是否存在，修改为查询实际存在的字段，这里用 room_number 示例
                cursor.execute("SELECT room_number FROM rooms WHERE room_number = ?", (room_number,))
                room = cursor.fetchone()
                if not room:
                    messagebox.showerror("错误", "该房间不存在")
                    conn.close()
                    return

                # 检查房间状态，假设数据库中“空闲”存的是中文“空闲”

                cursor.execute("SELECT status FROM rooms WHERE room_number = ?", (room_number,))
                room_status = cursor.fetchone()[0]
                if room_status != '空闲':
                    messagebox.showerror("错误", f"该房间当前状态为: {room_status}, 不可预订")
                    return

                # 检查日期冲突
                cursor.execute("""
                    SELECT COUNT(*) FROM reservations 
                    WHERE room_number = ? 
                    AND (
                        (check_in_date < ? AND check_out_date > ?) OR  -- 新预订开始日期在已有预订期间
                        (check_in_date < ? AND check_out_date > ?) OR  -- 新预订结束日期在已有预订期间
                        (check_in_date >= ? AND check_out_date <= ?)   -- 新预订完全包含在已有预订期间
                    )
                """, (room_number,
                      check_out_date, check_in_date,  # 第一个条件
                      check_out_date, check_in_date,  # 第二个条件
                      check_in_date, check_out_date))  # 第三个条件

                conflict_count = cursor.fetchone()[0]
                if conflict_count > 0:
                    messagebox.showerror("错误", "该房间在所选日期已被预订")
                    return
                    conn.close()
                    return

                # 生成入住到退房期间的所有日期
                date_range = [(in_date + timedelta(days=i)).strftime("%Y-%m-%d")
                              for i in range((out_date - in_date).days)]

                # 检查每一天是否已有预订
                for date in date_range:
                    cursor.execute("""
                        SELECT COUNT(*) FROM reservations 
                        WHERE room_number = ? 
                        AND status != 'cancelled'
                        AND (
                            (check_in_date <= ? AND check_out_date > ?)
                        )
                    """, (room_number, date, date))

                    conflict_count = cursor.fetchone()[0]
                    if conflict_count > 0:
                        messagebox.showerror("错误", f"该房间在 {date} 已有预订，无法重复预订")
                        conn.close()
                        return

                # 添加预订
                cursor.execute("""
                    INSERT INTO reservations (room_number, customer_id, check_in_date, check_out_date, status)
                    VALUES (?, ?, ?, ?, ?)
                """, (room_number, customer_id, check_in_date, check_out_date, "已预订"))

                # 更新房间状态
                # 更新房间状态为已预订（这里根据实际需求，比如改为 '已预订' 等，也得和表结构对应）
                cursor.execute("UPDATE rooms SET status = '已预订' WHERE room_number = ?", (room_number,))

                conn.commit()
                messagebox.showinfo("成功", "预订添加成功")
                add_reservation_win.destroy()
                conn.close()
            except ValueError as ve:
                messagebox.showerror("错误", f"日期格式错误: {str(ve)}")
                if 'conn' in locals():
                    conn.close()
            except Exception as e:
                messagebox.showerror("错误", f"添加预订失败: {str(e)}")
                if 'conn' in locals():
                    conn.close()

                    # 新增“保存”按钮，绑定 save_reservation 函数

        save_btn = ttk.Button(add_reservation_win, text="保存", command=save_reservation)
        save_btn.grid(row=6, column=0, columnspan=3, pady=10)

    def modify_reservation(self):
        # 创建修改预订的顶层窗口
        modify_reservation_win = tk.Toplevel(self.root)
        modify_reservation_win.title("修改预订")
        modify_reservation_win.geometry("400x400")

        # 预订ID标签与输入框
        ttk.Label(modify_reservation_win, text="预订ID:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        reservation_id_entry = ttk.Entry(modify_reservation_win)
        reservation_id_entry.grid(row=0, column=1, padx=5, pady=5)

        # 查询预订按钮
        def query_reservation():
            reservation_id = reservation_id_entry.get()
            if not reservation_id.isdigit():
                messagebox.showerror("错误", "请输入有效的预订ID")
                return
            try:
                conn = sqlite3.connect('hotel.db')
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT r.reservation_id, r.room_number, r.customer_id, c.name, 
                           r.check_in_date, r.check_out_date, r.status
                    FROM reservations r
                    JOIN customers c ON r.customer_id = c.customer_id
                    WHERE r.reservation_id = ?
                """, (reservation_id,))
                result = cursor.fetchone()
                if result:
                    # 显示预订信息
                    reservation_info_label.config(text=f"预订ID: {result[0]}, 房间号: {result[1]}, 客户: {result[3]}")

                    # 设置各个字段的值
                    room_number_entry.delete(0, tk.END)
                    room_number_entry.insert(0, str(result[1]))

                    customer_id_entry.delete(0, tk.END)
                    customer_id_entry.insert(0, str(result[2]))

                    check_in_entry.delete(0, tk.END)
                    check_in_entry.insert(0, result[4])

                    check_out_entry.delete(0, tk.END)
                    check_out_entry.insert(0, result[5])

                    status_var.set(result[6])
                else:
                    messagebox.showerror("错误", "未找到该预订ID对应的预订")
            finally:
                conn.close()

        ttk.Button(modify_reservation_win, text="查询预订", command=query_reservation).grid(row=0, column=2, padx=5,
                                                                                            pady=5)
        reservation_info_label = ttk.Label(modify_reservation_win, text="")
        reservation_info_label.grid(row=1, column=0, columnspan=3, padx=5, pady=5, sticky=tk.W)

        # 房间号
        ttk.Label(modify_reservation_win, text="房间号:").grid(row=2, column=0, padx=5, pady=5, sticky=tk.W)
        room_number_entry = ttk.Entry(modify_reservation_win)
        room_number_entry.grid(row=2, column=1, padx=5, pady=5)

        # 客户ID
        ttk.Label(modify_reservation_win, text="客户ID:").grid(row=3, column=0, padx=5, pady=5, sticky=tk.W)
        customer_id_entry = ttk.Entry(modify_reservation_win)
        customer_id_entry.grid(row=3, column=1, padx=5, pady=5)

        # 入住日期
        ttk.Label(modify_reservation_win, text="入住日期:").grid(row=4, column=0, padx=5, pady=5, sticky=tk.W)
        check_in_entry = ttk.Entry(modify_reservation_win)
        check_in_entry.grid(row=4, column=1, padx=5, pady=5)

        # 退房日期
        ttk.Label(modify_reservation_win, text="退房日期:").grid(row=5, column=0, padx=5, pady=5, sticky=tk.W)
        check_out_entry = ttk.Entry(modify_reservation_win)
        check_out_entry.grid(row=5, column=1, padx=5, pady=5)

        # 状态
        ttk.Label(modify_reservation_win, text="状态:").grid(row=6, column=0, padx=5, pady=5, sticky=tk.W)
        status_var = tk.StringVar(value="reserved")
        ttk.Combobox(modify_reservation_win, textvariable=status_var,
                     values=["reserved", "checked_in", "canceled", "completed"]).grid(row=6, column=1, padx=5, pady=5)

        def save_modification():
            reservation_id = reservation_id_entry.get()
            room_number = room_number_entry.get()
            customer_id = customer_id_entry.get()
            check_in_date = check_in_entry.get()
            check_out_date = check_out_entry.get()
            status = status_var.get()

            if not (reservation_id.isdigit() and room_number.isdigit() and customer_id.isdigit()):
                messagebox.showerror("错误", "ID和房间号必须为数字")
                return
            if not (check_in_date and check_out_date):
                messagebox.showerror("错误", "日期不能为空")
                return

            try:
                conn = sqlite3.connect('hotel.db')
                cursor = conn.cursor()

                # 获取原始房间号
                cursor.execute("SELECT room_number FROM reservations WHERE reservation_id = ?", (reservation_id,))
                original_room = cursor.fetchone()
                if not original_room:
                    messagebox.showerror("错误", "未找到该预订")
                    return

                original_room_number = original_room[0]

                # 如果房间号改变了，需要更新房间状态
                if original_room_number != int(room_number):
                    # 恢复原房间状态
                    cursor.execute("UPDATE rooms SET status = 'available' WHERE room_number = ?",
                                   (original_room_number,))

                    # 检查新房间是否可用
                    cursor.execute("SELECT status FROM rooms WHERE room_number = ?", (room_number,))
                    new_room_status = cursor.fetchone()
                    if not new_room_status or new_room_status[0] != "available":
                        messagebox.showerror("错误", "新房间不可用")
                        conn.rollback()
                        return

                    # 更新新房间状态
                    cursor.execute("UPDATE rooms SET status = 'reserved' WHERE room_number = ?", (room_number,))

                # 更新预订信息
                cursor.execute("""
                    UPDATE reservations 
                    SET room_number = ?, customer_id = ?, check_in_date = ?, check_out_date = ?, status = ?
                    WHERE reservation_id = ?
                """, (room_number, customer_id, check_in_date, check_out_date, status, reservation_id))

                conn.commit()
                messagebox.showinfo("成功", "预订修改成功")
                modify_reservation_win.destroy()
            except Exception as e:
                messagebox.showerror("错误", f"修改预订失败: {str(e)}")
            finally:
                conn.close()

        ttk.Button(modify_reservation_win, text="保存修改", command=save_modification).grid(row=7, column=0,
                                                                                            columnspan=3, pady=10)

    def cancel_reservation(self):
        # 创建取消预订的对话框
        reservation_id = simpledialog.askinteger("取消预订", "请输入要取消的预订ID:")
        if not reservation_id:
            return

        try:
            conn = sqlite3.connect('hotel.db')
            cursor = conn.cursor()

            # 获取预订信息
            cursor.execute("SELECT room_number FROM reservations WHERE reservation_id = ? AND status = 'reserved'",
                           (reservation_id,))
            result = cursor.fetchone()
            if not result:
                messagebox.showerror("错误", "未找到可取消的预订（可能已入住或已完成）")
                return

            room_number = result[0]

            # 更新预订状态
            cursor.execute("UPDATE reservations SET status = 'canceled' WHERE reservation_id = ?", (reservation_id,))

            # 更新房间状态
            cursor.execute("UPDATE rooms SET status = 'available' WHERE room_number = ?", (room_number,))

            conn.commit()
            messagebox.showinfo("成功", "预订已取消")
        except Exception as e:
            messagebox.showerror("错误", f"取消预订失败: {str(e)}")
        finally:
            conn.close()

    def view_reservations(self):
        # 创建查看预订列表的顶层窗口
        view_reservations_win = tk.Toplevel(self.root)
        view_reservations_win.title("预订列表")
        view_reservations_win.geometry("1100x500")

        # 创建树状视图展示预订数据
        tree = ttk.Treeview(view_reservations_win,
                            columns=("预订ID", "房间号", "客户ID", "客户姓名", "入住日期", "退房日期", "状态"),
                            show='headings', selectmode='browse')

        # 设置列标题
        tree.heading("预订ID", text="预订ID")
        tree.heading("房间号", text="房间号")
        tree.heading("客户ID", text="客户ID")
        tree.heading("客户姓名", text="客户姓名")
        tree.heading("入住日期", text="入住日期")
        tree.heading("退房日期", text="退房日期")
        tree.heading("状态", text="状态")

        # 设置列宽
        tree.column("预订ID", width=80)
        tree.column("房间号", width=80)
        tree.column("客户ID", width=80)
        tree.column("客户姓名", width=120)
        tree.column("入住日期", width=120)
        tree.column("退房日期", width=120)
        tree.column("状态", width=100)

        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # 添加滚动条
        scrollbar = ttk.Scrollbar(view_reservations_win, orient='vertical', command=tree.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        tree.configure(yscrollcommand=scrollbar.set)

        # 添加筛选选项
        filter_frame = ttk.Frame(view_reservations_win)
        filter_frame.pack(fill=tk.X, padx=5, pady=5)

        ttk.Label(filter_frame, text="状态筛选:").pack(side=tk.LEFT, padx=5)
        status_var = tk.StringVar(value="all")
        status_combo = ttk.Combobox(filter_frame, textvariable=status_var,
                                    values=["all", "reserved", "checked_in", "canceled", "completed"])
        status_combo.pack(side=tk.LEFT, padx=5)

        def load_reservations():
            status = status_var.get()
            try:
                conn = sqlite3.connect('hotel.db')
                cursor = conn.cursor()

                # 清空现有数据
                for item in tree.get_children():
                    tree.delete(item)

                # 构建查询
                query = """
                    SELECT r.reservation_id, r.room_number, r.customer_id, c.name, 
                           r.check_in_date, r.check_out_date, r.status
                    FROM reservations r
                    JOIN customers c ON r.customer_id = c.customer_id
                """
                params = []

                if status != "all":
                    query += " WHERE r.status = ?"
                    params.append(status)

                query += " ORDER BY r.check_in_date"

                cursor.execute(query, params)
                results = cursor.fetchall()

                for row in results:
                    tree.insert('', tk.END, values=row)
            finally:
                conn.close()

        ttk.Button(filter_frame, text="筛选", command=load_reservations).pack(side=tk.LEFT, padx=5)

        # 初始加载数据
        load_reservations()

    def check_in(self):
        """办理入住 - 需预订房间号和客户ID匹配"""
        win = tk.Toplevel(self.root)
        win.title("办理入住")
        win.geometry("350x200")

        # 房间号输入
        ttk.Label(win, text="房间号:").grid(row=0, column=0, padx=5, pady=5)
        room_entry = ttk.Entry(win)
        room_entry.grid(row=0, column=1, padx=5, pady=5)
        room_entry.focus()

        # 客户ID输入
        ttk.Label(win, text="客户ID:").grid(row=1, column=0, padx=5, pady=5)
        customer_entry = ttk.Entry(win)
        customer_entry.grid(row=1, column=1, padx=5, pady=5)

        def validate_booking():
            """验证预订信息是否匹配"""
            room = room_entry.get()
            customer = customer_entry.get()

            if not (room and customer):
                messagebox.showerror("错误", "房间号和客户ID不能为空")
                return False

            try:
                conn = sqlite3.connect('hotel.db')
                cursor = conn.cursor()

                # 检查是否存在匹配的预订（房间号、客户ID、状态为"已预订"）
                cursor.execute("""
                    SELECT r.reservation_id, c.name
                    FROM reservations r
                    JOIN customers c ON r.customer_id = c.customer_id
                    WHERE r.room_number = ? AND r.customer_id = ? AND r.status = '已预订'
                """, (room, customer))

                reservation = cursor.fetchone()
                if not reservation:
                    messagebox.showerror("错误", "未找到匹配的预订记录\n请确认房间号和客户ID是否正确")
                    return False

                reservation_id, customer_name = reservation
                messagebox.showinfo("验证成功", f"已找到匹配预订\n预订ID: {reservation_id}\n客户: {customer_name}")
                return True

            except Exception as e:
                messagebox.showerror("错误", f"验证预订失败: {str(e)}")
                return False
            finally:
                conn.close()

        def confirm_check_in():
            """确认入住，仅当预订验证通过时执行"""
            if not validate_booking():
                return

            room = room_entry.get()
            customer = customer_entry.get()

            try:
                conn = sqlite3.connect('hotel.db')
                cursor = conn.cursor()

                # 检查房间状态是否为"已预订"
                cursor.execute("SELECT status FROM rooms WHERE room_number=?", (room,))
                room_status = cursor.fetchone()
                if not room_status or room_status[0] != "已预订":
                    messagebox.showerror("错误", f"房间{room}状态异常，无法办理入住")
                    return

                # 更新房间状态为"已入住"
                cursor.execute("UPDATE rooms SET status='已入住' WHERE room_number=?", (room,))

                # 更新预订状态为"已入住"
                cursor.execute("UPDATE reservations SET status='已入住' WHERE room_number=? AND customer_id=?",
                               (room, customer))

                conn.commit()
                messagebox.showinfo("成功", f"房间{room}入住成功\n客户ID: {customer}")
                win.destroy()

            except Exception as e:
                messagebox.showerror("错误", f"入住失败：{str(e)}")
            finally:
                conn.close()

        # 按钮区域
        ttk.Button(win, text="验证预订", command=validate_booking).grid(row=2, column=0, padx=5, pady=10)
        ttk.Button(win, text="确认入住", command=confirm_check_in).grid(row=2, column=1, padx=5, pady=10)

    def check_out(self):
        """简化版办理退房"""
        win = tk.Toplevel(self.root)
        win.title("办理退房")

        # 房间选择
        ttk.Label(win, text="房间号:").grid(row=0, column=0)
        room_entry = ttk.Entry(win)
        room_entry.grid(row=0, column=1)

        def confirm():
            room = room_entry.get()

            if not room:
                messagebox.showerror("错误", "请填写房间号")
                return

            try:
                conn = sqlite3.connect('hotel.db')
                cursor = conn.cursor()

                # 获取房间价格
                cursor.execute("SELECT price FROM rooms WHERE room_number=?", (room,))
                price = cursor.fetchone()[0]

                # 更新房间状态
                cursor.execute("""
                    UPDATE rooms 
                    SET status='空闲', clean_status='未清洁' 
                    WHERE room_number=?
                """, (room,))

                # 记录交易（简化：按1天计算）
                cursor.execute("""
                    INSERT INTO transactions (amount, transaction_date, description)
                    VALUES (?, datetime('now'), '房费')
                """, (price,))

                conn.commit()
                messagebox.showinfo("成功", f"房间 {room} 退房成功\n应收: {price}元")
                win.destroy()
            except Exception as e:
                messagebox.showerror("错误", f"退房失败: {str(e)}")
            finally:
                conn.close()

        ttk.Button(win, text="确认退房", command=confirm).grid(row=1, columnspan=2)

    def view_finance(self):
        """显示财务统计信息"""
        finance_window = tk.Toplevel(self.root)
        finance_window.title("财务统计")
        finance_window.geometry("800x600")
        finance_window.transient(self.root)

        # 创建主框架
        main_frame = ttk.Frame(finance_window, padding="20 20 20 20")
        main_frame.pack(fill=tk.BOTH, expand=True)

        ttk.Label(main_frame, text="财务收入统计", font=("Arial", 16, "bold")).pack(pady=10)

        # 创建统计数据框架
        stats_frame = ttk.LabelFrame(main_frame, text="收入概览", padding="10 10 10 10")
        stats_frame.pack(fill=tk.X, pady=10)

        # 获取统计数据
        try:
            cursor = self.conn.cursor()

            # 总收入
            cursor.execute("SELECT SUM(amount) FROM transactions")
            total_income = cursor.fetchone()[0] or 0

            # 今日收入
            cursor.execute("SELECT SUM(amount) FROM transactions WHERE date(transaction_date) = date('now')")
            today_income = cursor.fetchone()[0] or 0

            # 本月收入
            cursor.execute(
                "SELECT SUM(amount) FROM transactions WHERE strftime('%Y-%m', transaction_date) = strftime('%Y-%m', 'now')")
            month_income = cursor.fetchone()[0] or 0

            # 订单数量
            cursor.execute("SELECT COUNT(DISTINCT reservation_id) FROM transactions")
            order_count = cursor.fetchone()[0] or 0

            # 平均每订单收入
            avg_income_per_order = total_income / order_count if order_count > 0 else 0

        except sqlite3.Error as e:
            messagebox.showerror("数据库错误", f"获取财务数据失败: {str(e)}", parent=finance_window)
            return

        # 显示统计数据
        stats_grid = ttk.Frame(stats_frame)
        stats_grid.pack(fill=tk.X, padx=20, pady=10)

        # 第一行
        ttk.Label(stats_grid, text="总收入:", font=("Arial", 12)).grid(row=0, column=0, sticky=tk.W, padx=10, pady=5)
        ttk.Label(stats_grid, text=f"¥ {total_income:.2f}", font=("Arial", 12, "bold")).grid(row=0, column=1,
                                                                                             sticky=tk.W, padx=10,
                                                                                             pady=5)

        ttk.Label(stats_grid, text="今日收入:", font=("Arial", 12)).grid(row=0, column=2, sticky=tk.W, padx=10, pady=5)
        ttk.Label(stats_grid, text=f"¥ {today_income:.2f}", font=("Arial", 12, "bold")).grid(row=0, column=3,
                                                                                             sticky=tk.W, padx=10,
                                                                                             pady=5)

        # 第二行
        ttk.Label(stats_grid, text="本月收入:", font=("Arial", 12)).grid(row=1, column=0, sticky=tk.W, padx=10, pady=5)
        ttk.Label(stats_grid, text=f"¥ {month_income:.2f}", font=("Arial", 12, "bold")).grid(row=1, column=1,
                                                                                             sticky=tk.W, padx=10,
                                                                                             pady=5)

        ttk.Label(stats_grid, text="订单数量:", font=("Arial", 12)).grid(row=1, column=2, sticky=tk.W, padx=10, pady=5)
        ttk.Label(stats_grid, text=f"{order_count}", font=("Arial", 12, "bold")).grid(row=1, column=3, sticky=tk.W,
                                                                                      padx=10, pady=5)

        # 第三行
        ttk.Label(stats_grid, text="平均每订单收入:", font=("Arial", 12)).grid(row=2, column=0, sticky=tk.W, padx=10,
                                                                               pady=5)
        ttk.Label(stats_grid, text=f"¥ {avg_income_per_order:.2f}", font=("Arial", 12, "bold")).grid(row=2, column=1,
                                                                                                     sticky=tk.W,
                                                                                                     padx=10, pady=5)

        # 创建图表框架
        charts_frame = ttk.LabelFrame(main_frame, text="收入趋势", padding="10 10 10 10")
        charts_frame.pack(fill=tk.BOTH, expand=True, pady=10)

        # 使用matplotlib创建简单图表
        try:
            # 过去7天的收入
            cursor.execute("""
                SELECT date(transaction_date) as date, SUM(amount) as daily_income
                FROM transactions
                WHERE date(transaction_date) >= date('now', '-6 days')
                GROUP BY date(transaction_date)
                ORDER BY date(transaction_date)
            """)

            daily_data = cursor.fetchall()
            dates = []
            incomes = []

            # 确保有7天的数据（即使某天没有收入）
            date_income_dict = {row[0]: row[1] for row in daily_data}

            for i in range(6, -1, -1):
                date_str = self.get_date_str(i)
                dates.append(date_str.split('-')[2])  # 只显示日期部分
                incomes.append(date_income_dict.get(date_str, 0))

            # 创建绘图控件
            from matplotlib.figure import Figure
            from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

            fig = Figure(figsize=(8, 4), dpi=100)
            ax = fig.add_subplot(111)

            # 绘制柱状图
            bars = ax.bar(dates, incomes, color='skyblue')
            ax.set_xlabel('日期')
            ax.set_ylabel('收入 (¥)')
            ax.set_title('过去7天收入统计')

            # 添加数据标签
            for bar, income in zip(bars, incomes):
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width() / 2., height + 5,
                        f'¥{income:.0f}', ha='center', va='bottom')

            # 将图表添加到界面
            canvas = FigureCanvasTkAgg(fig, master=charts_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        except Exception as e:
            error_label = ttk.Label(charts_frame, text=f"无法加载图表: {str(e)}", foreground="red")
            error_label.pack(padx=20, pady=20)
            import traceback
            traceback.print_exc()  # 在控制台打印详细错误信息

        # 底部按钮
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(pady=10)

        ttk.Button(button_frame, text="导出报表", command=lambda: self.export_finance_report(
            total_income, today_income, month_income, order_count, avg_income_per_order
        ), width=15).pack(side=tk.LEFT, padx=5)

        ttk.Button(button_frame, text="查看详细交易", command=self.view_transactions, width=15).pack(side=tk.LEFT,
                                                                                                     padx=5)
        ttk.Button(button_frame, text="关闭", command=finance_window.destroy, width=15).pack(side=tk.LEFT, padx=5)

    def get_date_str(self, days_ago):
        """获取指定天数前的日期字符串，格式为YYYY-MM-DD"""
        import datetime
        today = datetime.date.today()
        target_date = today - datetime.timedelta(days=days_ago)
        return target_date.strftime("%Y-%m-%d")

    def export_finance_report(self, total_income, today_income, month_income, order_count, avg_income_per_order):
        """导出财务报表到CSV文件"""
        import csv
        import datetime
        from tkinter import filedialog

        # 让用户选择保存位置
        filename = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV文件", "*.csv"), ("所有文件", "*.*")],
            title="保存财务报表"
        )

        if not filename:
            return  # 用户取消了保存

        try:
            with open(filename, 'w', newline='', encoding='utf-8-sig') as csvfile:
                writer = csv.writer(csvfile)

                # 写入报表头
                writer.writerow(['酒店住房管理系统财务报表'])
                writer.writerow(['生成时间', datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")])
                writer.writerow([])  # 空行

                # 写入摘要数据
                writer.writerow(['财务摘要'])
                writer.writerow(['总收入', f'¥ {total_income:.2f}'])
                writer.writerow(['今日收入', f'¥ {today_income:.2f}'])
                writer.writerow(['本月收入', f'¥ {month_income:.2f}'])
                writer.writerow(['订单数量', order_count])
                writer.writerow(['平均每订单收入', f'¥ {avg_income_per_order:.2f}'])
                writer.writerow([])  # 空行

                # 写入详细交易记录
                writer.writerow(['详细交易记录'])
                writer.writerow(['交易ID', '订单ID', '房间号', '客户姓名', '金额', '交易日期', '描述'])

                cursor = self.conn.cursor()
                cursor.execute("""
                    SELECT t.transaction_id, t.reservation_id, r.room_number, c.name, t.amount, 
                           t.transaction_date, t.description
                    FROM transactions t
                    LEFT JOIN reservations r ON t.reservation_id = r.reservation_id
                    LEFT JOIN customers c ON r.customer_id = c.customer_id
                    ORDER BY t.transaction_date DESC
                """)

                transactions = cursor.fetchall()
                for transaction in transactions:
                    writer.writerow(transaction)

            messagebox.showinfo("成功", f"财务报表已成功导出到: {filename}")
        except Exception as e:
            messagebox.showerror("错误", f"导出报表失败: {str(e)}")

    def add_transaction(self):
        """添加新的交易记录"""
        transaction_window = tk.Toplevel(self.root)
        transaction_window.title("添加收费项目")
        transaction_window.geometry("500x400")
        transaction_window.transient(self.root)
        transaction_window.grab_set()  # 模态窗口

        # 创建表单框架
        frame = ttk.Frame(transaction_window, padding="20 20 20 20")
        frame.pack(fill=tk.BOTH, expand=True)

        ttk.Label(frame, text="添加新收费项目", font=("Arial", 14, "bold")).grid(column=0, row=0, columnspan=2, pady=10)

        # 订单选择
        ttk.Label(frame, text="关联订单:").grid(column=0, row=1, sticky=tk.W, pady=5)
        reservation_var = tk.StringVar()
        reservation_combo = ttk.Combobox(frame, textvariable=reservation_var, width=30)
        reservation_combo.grid(column=1, row=1, pady=5, sticky=tk.W)

        # 加载活跃订单
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT r.reservation_id, r.room_number, c.name, r.check_in_date, r.check_out_date
            FROM reservations r
            JOIN customers c ON r.customer_id = c.customer_id
            WHERE r.status IN ('confirmed', 'checked_in')
            ORDER BY r.check_in_date DESC
        """)
        reservations = cursor.fetchall()

        reservation_combo['values'] = [f"{r[0]} - 房间{r[1]} - {r[2]}" for r in reservations]
        if reservations:
            reservation_combo.current(0)

        # 金额
        ttk.Label(frame, text="金额 (¥):").grid(column=0, row=2, sticky=tk.W, pady=5)
        amount_var = tk.StringVar()
        amount_entry = ttk.Entry(frame, textvariable=amount_var, width=15)
        amount_entry.grid(column=1, row=2, pady=5, sticky=tk.W)

        # 描述
        ttk.Label(frame, text="描述:").grid(column=0, row=3, sticky=tk.W, pady=5)
        description_var = tk.StringVar()
        description_entry = ttk.Entry(frame, textvariable=description_var, width=30)
        description_entry.grid(column=1, row=3, pady=5, sticky=tk.W)

        # 交易日期（默认当前日期）
        import datetime
        ttk.Label(frame, text="交易日期:").grid(column=0, row=4, sticky=tk.W, pady=5)
        date_var = tk.StringVar(value=datetime.date.today().strftime("%Y-%m-%d"))
        date_entry = ttk.Entry(frame, textvariable=date_var, width=15)
        date_entry.grid(column=1, row=4, pady=5, sticky=tk.W)

        # 交易类型
        ttk.Label(frame, text="交易类型:").grid(column=0, row=5, sticky=tk.W, pady=5)
        type_var = tk.StringVar(value="房费")
        type_combo = ttk.Combobox(frame, textvariable=type_var, width=15)
        type_combo['values'] = ("房费", "餐饮", "会议室", "SPA", "迷你吧", "洗衣", "其他")
        type_combo.grid(column=1, row=5, pady=5, sticky=tk.W)

        # 创建提交函数
        def save_transaction():
            # 验证输入
            if not reservation_var.get():
                messagebox.showerror("错误", "请选择关联订单", parent=transaction_window)
                return

            try:
                amount = float(amount_var.get())
                if amount <= 0:
                    messagebox.showerror("错误", "金额必须大于零", parent=transaction_window)
                    return
            except ValueError:
                messagebox.showerror("错误", "请输入有效的金额", parent=transaction_window)
                return

            if not description_var.get():
                # 如果没有填写描述，则使用交易类型作为描述
                description_var.set(f"{type_var.get()} 费用")

            try:
                # 从选择的订单中提取订单ID
                reservation_id = reservation_var.get().split(" - ")[0]

                # 保存交易记录
                cursor = self.conn.cursor()
                cursor.execute("""
                    INSERT INTO transactions (reservation_id, amount, transaction_date, description)
                    VALUES (?, ?, ?, ?)
                """, (
                    reservation_id,
                    amount,
                    date_var.get(),
                    description_var.get()
                ))

                self.conn.commit()
                messagebox.showinfo("成功", "交易记录已成功添加", parent=transaction_window)

                # 清空表单
                amount_var.set("")
                description_var.set("")
                type_var.set("房费")

                self.update_status(f"已添加金额为 ¥{amount:.2f} 的新交易记录")
            except sqlite3.Error as e:
                self.conn.rollback()
                messagebox.showerror("数据库错误", f"添加交易记录失败: {str(e)}", parent=transaction_window)

        # 添加按钮
        button_frame = ttk.Frame(frame)
        button_frame.grid(column=0, row=6, columnspan=2, pady=20)

        ttk.Button(button_frame, text="保存", command=save_transaction, width=10).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="取消", command=transaction_window.destroy, width=10).pack(side=tk.LEFT, padx=5)

    def view_transactions(self):
        """查看所有交易记录"""
        transactions_window = tk.Toplevel(self.root)
        transactions_window.title("交易记录")
        transactions_window.geometry("1000x600")
        transactions_window.transient(self.root)

        # 创建主框架
        main_frame = ttk.Frame(transactions_window, padding="20 20 20 20")
        main_frame.pack(fill=tk.BOTH, expand=True)

        ttk.Label(main_frame, text="交易记录列表", font=("Arial", 14, "bold")).pack(pady=10)

        # 创建搜索框架
        search_frame = ttk.Frame(main_frame)
        search_frame.pack(fill=tk.X, pady=10)

        ttk.Label(search_frame, text="开始日期:").pack(side=tk.LEFT, padx=(0, 5))
        import datetime
        start_date_var = tk.StringVar(value=(datetime.date.today() - datetime.timedelta(days=30)).strftime("%Y-%m-%d"))
        start_date_entry = ttk.Entry(search_frame, textvariable=start_date_var, width=12)
        start_date_entry.pack(side=tk.LEFT, padx=(0, 10))

        ttk.Label(search_frame, text="结束日期:").pack(side=tk.LEFT, padx=(0, 5))
        end_date_var = tk.StringVar(value=datetime.date.today().strftime("%Y-%m-%d"))
        end_date_entry = ttk.Entry(search_frame, textvariable=end_date_var, width=12)
        end_date_entry.pack(side=tk.LEFT, padx=(0, 10))

        ttk.Label(search_frame, text="关键词:").pack(side=tk.LEFT, padx=(10, 5))
        keyword_var = tk.StringVar()
        keyword_entry = ttk.Entry(search_frame, textvariable=keyword_var, width=15)
        keyword_entry.pack(side=tk.LEFT, padx=(0, 10))

        # 创建表格框架
        table_frame = ttk.Frame(main_frame)
        table_frame.pack(fill=tk.BOTH, expand=True, pady=10)

        # 创建交易记录表格
        columns = ("交易ID", "订单ID", "房间号", "客户姓名", "金额", "交易日期", "描述")
        transactions_tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=20)

        # 添加滚动条
        scrollbar_y = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=transactions_tree.yview)
        scrollbar_y.pack(side=tk.RIGHT, fill=tk.Y)
        scrollbar_x = ttk.Scrollbar(table_frame, orient=tk.HORIZONTAL, command=transactions_tree.xview)
        scrollbar_x.pack(side=tk.BOTTOM, fill=tk.X)

        transactions_tree.configure(yscrollcommand=scrollbar_y.set, xscrollcommand=scrollbar_x.set)
        transactions_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # 设置列标题和宽度
        transactions_tree.heading("交易ID", text="交易ID")
        transactions_tree.column("交易ID", width=60, anchor=tk.CENTER)

        transactions_tree.heading("订单ID", text="订单ID")
        transactions_tree.column("订单ID", width=60, anchor=tk.CENTER)

        transactions_tree.heading("房间号", text="房间号")
        transactions_tree.column("房间号", width=70, anchor=tk.CENTER)

        transactions_tree.heading("客户姓名", text="客户姓名")
        transactions_tree.column("客户姓名", width=100)

        transactions_tree.heading("金额", text="金额")
        transactions_tree.column("金额", width=80, anchor=tk.E)

        transactions_tree.heading("交易日期", text="交易日期")
        transactions_tree.column("交易日期", width=100, anchor=tk.CENTER)

        transactions_tree.heading("描述", text="描述")
        transactions_tree.column("描述", width=200)

        # 定义加载数据函数
        def load_transactions():
            # 清空现有数据
            for item in transactions_tree.get_children():
                transactions_tree.delete(item)

            # 构建查询条件
            conditions = []
            params = []

            # 日期条件
            if start_date_var.get():
                conditions.append("t.transaction_date >= ?")
                params.append(start_date_var.get())

            if end_date_var.get():
                conditions.append("t.transaction_date <= ?")
                params.append(end_date_var.get())

            # 关键词条件
            if keyword_var.get():
                keyword = f"%{keyword_var.get()}%"
                conditions.append("(t.description LIKE ? OR c.name LIKE ?)")
                params.extend([keyword, keyword])

            # 构建完整查询
            query = """
                SELECT t.transaction_id, t.reservation_id, r.room_number, c.name, t.amount, 
                       t.transaction_date, t.description
                FROM transactions t
                LEFT JOIN reservations r ON t.reservation_id = r.reservation_id
                LEFT JOIN customers c ON r.customer_id = c.customer_id
            """

            if conditions:
                query += " WHERE " + " AND ".join(conditions)

            query += " ORDER BY t.transaction_date DESC"

            try:
                cursor = self.conn.cursor()
                cursor.execute(query, params)

                transactions = cursor.fetchall()

                # 填充表格
                for transaction in transactions:
                    # 格式化金额显示
                    formatted_amount = f"¥ {transaction[4]:.2f}"
                    # 使用修改后的金额替换原始金额
                    row_data = list(transaction)
                    row_data[4] = formatted_amount

                    transactions_tree.insert("", tk.END, values=row_data)

                self.update_status(f"已加载 {len(transactions)} 条交易记录")
            except sqlite3.Error as e:
                messagebox.showerror("数据库错误", f"加载交易数据失败: {str(e)}", parent=transactions_window)

        # 添加搜索按钮
        ttk.Button(search_frame, text="搜索", command=load_transactions, width=10).pack(side=tk.LEFT, padx=10)
        ttk.Button(search_frame, text="重置", command=lambda: [
            start_date_var.set((datetime.date.today() - datetime.timedelta(days=30)).strftime("%Y-%m-%d")),
            end_date_var.set(datetime.date.today().strftime("%Y-%m-%d")),
            keyword_var.set(""),
            load_transactions()], width=10).pack(side=tk.LEFT)

        # 底部按钮框架
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(pady=10)

        ttk.Button(button_frame, text="添加交易", command=self.add_transaction, width=15).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="导出数据", command=lambda: self.export_transaction_data(transactions_tree),
                   width=15).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="删除交易", command=lambda: self.delete_transaction(transactions_tree),
                   width=15).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="关闭", command=transactions_window.destroy, width=15).pack(side=tk.LEFT, padx=5)

        # 加载初始数据
        load_transactions()

        # 添加右键菜单
        context_menu = tk.Menu(transactions_tree, tearoff=0)
        context_menu.add_command(label="查看详情", command=lambda: self.view_transaction_details(transactions_tree))
        context_menu.add_command(label="删除交易", command=lambda: self.delete_transaction(transactions_tree))

        def show_context_menu(event):
            if transactions_tree.selection():
                context_menu.post(event.x_root, event.y_root)

        transactions_tree.bind("<Button-3>", show_context_menu)  # 右键点击事件

    def view_transaction_details(self, tree_view):
        """查看交易详情"""
        selected_items = tree_view.selection()
        if not selected_items:
            messagebox.showinfo("提示", "请先选择一条交易记录")
            return

        # 获取选中的交易记录ID
        item = selected_items[0]
        transaction_id = tree_view.item(item, "values")[0]

        try:
            cursor = self.conn.cursor()
            cursor.execute("""
                SELECT t.transaction_id, t.reservation_id, r.room_number, c.name, c.contact, c.id_card,
                       t.amount, t.transaction_date, t.description, r.check_in_date, r.check_out_date
                FROM transactions t
                LEFT JOIN reservations r ON t.reservation_id = r.reservation_id
                LEFT JOIN customers c ON r.customer_id = c.customer_id
                WHERE t.transaction_id = ?
            """, (transaction_id,))

            transaction = cursor.fetchone()

            if not transaction:
                messagebox.showerror("错误", "找不到交易记录")
                return

            # 创建详情窗口
            details_window = tk.Toplevel(self.root)
            details_window.title(f"交易详情 - ID: {transaction_id}")
            details_window.geometry("500x400")
            details_window.transient(self.root)
            details_window.grab_set()  # 模态窗口

            # 创建详情框架
            frame = ttk.Frame(details_window, padding="20 20 20 20")
            frame.pack(fill=tk.BOTH, expand=True)

            ttk.Label(frame, text="交易详细信息", font=("Arial", 14, "bold")).grid(column=0, row=0, columnspan=2,
                                                                                   pady=10)

            # 交易信息
            info_frame = ttk.LabelFrame(frame, text="基本信息", padding="10 10 10 10")
            info_frame.grid(column=0, row=1, columnspan=2, sticky=tk.EW, pady=10)

            # 第一列
            ttk.Label(info_frame, text="交易ID:").grid(column=0, row=0, sticky=tk.W, pady=5)
            ttk.Label(info_frame, text=transaction[0]).grid(column=1, row=0, sticky=tk.W, pady=5)

            ttk.Label(info_frame, text="订单ID:").grid(column=0, row=1, sticky=tk.W, pady=5)
            ttk.Label(info_frame, text=transaction[1]).grid(column=1, row=1, sticky=tk.W, pady=5)

            ttk.Label(info_frame, text="房间号:").grid(column=0, row=2, sticky=tk.W, pady=5)
            ttk.Label(info_frame, text=transaction[2] or "未指定").grid(column=1, row=2, sticky=tk.W, pady=5)

            ttk.Label(info_frame, text="交易金额:").grid(column=0, row=3, sticky=tk.W, pady=5)
            ttk.Label(info_frame, text=f"¥ {transaction[6]:.2f}", font=("Arial", "10", "bold")).grid(column=1, row=3,
                                                                                                     sticky=tk.W,
                                                                                                     pady=5)

            # 第二列
            ttk.Label(info_frame, text="交易日期:").grid(column=2, row=0, sticky=tk.W, pady=5, padx=(20, 0))
            ttk.Label(info_frame, text=transaction[7]).grid(column=3, row=0, sticky=tk.W, pady=5)

            ttk.Label(info_frame, text="入住日期:").grid(column=2, row=1, sticky=tk.W, pady=5, padx=(20, 0))
            ttk.Label(info_frame, text=transaction[9] or "未指定").grid(column=3, row=1, sticky=tk.W, pady=5)

            ttk.Label(info_frame, text="退房日期:").grid(column=2, row=2, sticky=tk.W, pady=5, padx=(20, 0))
            ttk.Label(info_frame, text=transaction[10] or "未指定").grid(column=3, row=2, sticky=tk.W, pady=5)

            ttk.Label(info_frame, text="描述:").grid(column=2, row=3, sticky=tk.W, pady=5, padx=(20, 0))
            ttk.Label(info_frame, text=transaction[8]).grid(column=3, row=3, sticky=tk.W, pady=5)

            # 客户信息
            customer_frame = ttk.LabelFrame(frame, text="客户信息", padding="10 10 10 10")
            customer_frame.grid(column=0, row=2, columnspan=2, sticky=tk.EW, pady=10)

            ttk.Label(customer_frame, text="客户姓名:").grid(column=0, row=0, sticky=tk.W, pady=5)
            ttk.Label(customer_frame, text=transaction[3] or "未知").grid(column=1, row=0, sticky=tk.W, pady=5)

            ttk.Label(customer_frame, text="联系方式:").grid(column=0, row=1, sticky=tk.W, pady=5)
            ttk.Label(customer_frame, text=transaction[4] or "未知").grid(column=1, row=1, sticky=tk.W, pady=5)

            ttk.Label(customer_frame, text="身份证号:").grid(column=0, row=2, sticky=tk.W, pady=5)
            id_card = transaction[5] or "未知"
            # 如果有身份证号，只显示前4位和后4位，中间用*替代
            if len(id_card) >= 8 and id_card != "未知":
                masked_id = id_card[:4] + '*' * (len(id_card) - 8) + id_card[-4:]
                ttk.Label(customer_frame, text=masked_id).grid(column=1, row=2, sticky=tk.W, pady=5)
            else:
                ttk.Label(customer_frame, text=id_card).grid(column=1, row=2, sticky=tk.W, pady=5)

            # 底部按钮
            button_frame = ttk.Frame(frame)
            button_frame.grid(column=0, row=3, columnspan=2, pady=15)

            ttk.Button(button_frame, text="打印收据", command=lambda: self.print_receipt(transaction), width=15).pack(
                side=tk.LEFT, padx=5)
            ttk.Button(button_frame, text="关闭", command=details_window.destroy, width=15).pack(side=tk.LEFT, padx=5)

        except sqlite3.Error as e:
            messagebox.showerror("数据库错误", f"获取交易详情失败: {str(e)}")

    def print_receipt(self, transaction):
        """打印交易收据（模拟）"""
        import datetime

        receipt_window = tk.Toplevel(self.root)
        receipt_window.title("收据预览")
        receipt_window.geometry("400x500")
        receipt_window.transient(self.root)

        # 创建收据框架
        frame = ttk.Frame(receipt_window, padding="20 20 20 20")
        frame.pack(fill=tk.BOTH, expand=True)

        # 创建可滚动的文本区域
        from tkinter import scrolledtext
        receipt_text = scrolledtext.ScrolledText(frame, wrap=tk.WORD, width=50, height=25)
        receipt_text.pack(fill=tk.BOTH, expand=True)

        # 生成收据内容
        receipt_content = f"""
    {'=' * 50}
                    酒店住房管理系统
                        收  据
    {'=' * 50}

    收据号: {transaction[0]:08d}
    日期时间: {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

    客户信息:
      姓名: {transaction[3] or "未知"}
      联系电话: {transaction[4] or "未知"}

    订单信息:
      订单ID: {transaction[1]}
      房间号: {transaction[2] or "未指定"}
      入住日期: {transaction[9] or "未指定"}
      退房日期: {transaction[10] or "未指定"}

    交易信息:
      交易日期: {transaction[7]}
      交易描述: {transaction[8]}

    金额明细:
      {transaction[8]}: ¥ {transaction[6]:.2f}
    {'- ' * 25}
      总计: ¥ {transaction[6]:.2f}

    {'=' * 50}
            感谢您选择我们的酒店
            欢迎再次光临!
    {'=' * 50}
    """
        # 设置收据文本
        receipt_text.insert(tk.END, receipt_content)
        receipt_text.configure(state='disabled')  # 使文本不可编辑

        # 底部按钮
        button_frame = ttk.Frame(receipt_window)
        button_frame.pack(pady=10)

        ttk.Button(button_frame, text="打印", command=lambda: self.simulate_printing(receipt_content), width=10).pack(
            side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="保存", command=lambda: self.save_receipt(receipt_content), width=10).pack(
            side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="关闭", command=receipt_window.destroy, width=10).pack(side=tk.LEFT, padx=5)

    def simulate_printing(self, content):
        """模拟打印功能"""
        messagebox.showinfo("打印", "收据已发送到打印机（模拟）")

    def save_receipt(self, content):
        """保存收据到文件"""
        from tkinter import filedialog
        import datetime

        filename = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("文本文件", "*.txt"), ("所有文件", "*.*")],
            initialfile=f"收据_{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}.txt",
            title="保存收据"
        )

        if not filename:
            return  # 用户取消了保存

        try:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(content)
            messagebox.showinfo("成功", f"收据已保存到: {filename}")
        except Exception as e:
            messagebox.showerror("错误", f"保存收据失败: {str(e)}")

    def delete_transaction(self, tree_view):
        """删除交易记录"""
        selected_items = tree_view.selection()
        if not selected_items:
            messagebox.showinfo("提示", "请先选择一条交易记录")
            return

        # 获取选中的交易记录ID
        item = selected_items[0]
        transaction_id = tree_view.item(item, "values")[0]

        # 确认删除
        if not messagebox.askyesno("确认删除", "确定要删除所选交易记录吗？\n此操作不可恢复。"):
            return

        try:
            cursor = self.conn.cursor()
            cursor.execute("DELETE FROM transactions WHERE transaction_id = ?", (transaction_id,))
            self.conn.commit()

            # 从树形视图中移除
            tree_view.delete(item)

            messagebox.showinfo("成功", "交易记录已成功删除")
            self.update_status(f"交易记录 #{transaction_id} 已删除")
        except sqlite3.Error as e:
            self.conn.rollback()
            messagebox.showerror("数据库错误", f"删除交易记录失败: {str(e)}")

    def export_transaction_data(self, tree_view):
        """导出交易数据到CSV文件"""
        import csv
        from tkinter import filedialog

        # 让用户选择保存位置
        filename = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV文件", "*.csv"), ("所有文件", "*.*")],
            title="导出交易数据"
        )

        if not filename:
            return  # 用户取消了保存

        try:
            with open(filename, 'w', newline='', encoding='utf-8-sig') as csvfile:
                writer = csv.writer(csvfile)

                # 写入表头
                writer.writerow(["交易ID", "订单ID", "房间号", "客户姓名", "金额", "交易日期", "描述"])

                # 写入所有数据
                for item in tree_view.get_children():
                    values = tree_view.item(item, "values")
                    writer.writerow(values)

            messagebox.showinfo("成功", f"交易数据已成功导出到: {filename}")
        except Exception as e:
            messagebox.showerror("错误", f"导出数据失败: {str(e)}")

    def add_user(self):
        # 创建添加用户的对话框
        add_user_window = tk.Toplevel(self.root)
        add_user_window.title("添加用户")
        add_user_window.geometry("400x300")
        add_user_window.resizable(False, False)
        add_user_window.transient(self.root)  # 设置为主窗口的子窗口
        add_user_window.grab_set()  # 模态窗口

        # 创建表单
        frame = ttk.Frame(add_user_window, padding="20 20 20 20")
        frame.pack(fill=tk.BOTH, expand=True)

        ttk.Label(frame, text="添加新用户", font=("Arial", 14, "bold")).grid(column=0, row=0, columnspan=2, pady=10)

        # 用户名输入
        ttk.Label(frame, text="用户名:").grid(column=0, row=1, sticky=tk.W, pady=5)
        username_entry = ttk.Entry(frame, width=25)
        username_entry.grid(column=1, row=1, pady=5)
        # 设置初始焦点
        username_entry.focus_set()

        # 密码输入
        ttk.Label(frame, text="密码:").grid(column=0, row=2, sticky=tk.W, pady=5)
        password_entry = ttk.Entry(frame, show="*", width=25)
        password_entry.grid(column=1, row=2, pady=5)

        # 确认密码
        ttk.Label(frame, text="确认密码:").grid(column=0, row=3, sticky=tk.W, pady=5)
        confirm_password_entry = ttk.Entry(frame, show="*", width=25)
        confirm_password_entry.grid(column=1, row=3, pady=5)

        # 用户角色
        ttk.Label(frame, text="用户角色:").grid(column=0, row=4, sticky=tk.W, pady=5)
        role_var = tk.StringVar(value="frontdesk")
        ttk.Radiobutton(frame, text="前台", variable=role_var, value="frontdesk").grid(column=1, row=4, sticky=tk.W)
        ttk.Radiobutton(frame, text="管理员", variable=role_var, value="admin").grid(column=1, row=4, sticky=tk.E)

        # 按钮框架
        button_frame = ttk.Frame(frame)
        button_frame.grid(column=0, row=5, columnspan=2, pady=15)

        # 用于调试的函数
        def print_values():
            print(f"用户名: '{username_entry.get()}'")
            print(f"密码: '{password_entry.get()}'")

        def save_user():
            # 直接从Entry控件获取值
            username = username_entry.get().strip()
            password = password_entry.get()
            confirm_password = confirm_password_entry.get()
            role = role_var.get()

            # 打印调试信息到控制台
            print(f"尝试添加用户: '{username}', 角色: {role}")

            # 验证输入
            if not username:
                messagebox.showerror("错误", "用户名不能为空", parent=add_user_window)
                username_entry.focus_set()
                return

            if not password:
                messagebox.showerror("错误", "密码不能为空", parent=add_user_window)
                password_entry.focus_set()
                return

            if password != confirm_password:
                messagebox.showerror("错误", "两次输入的密码不一致", parent=add_user_window)
                confirm_password_entry.focus_set()
                return

            # 打开新的数据库连接
            conn = sqlite3.connect('hotel.db')
            cursor = conn.cursor()

            try:
                # 检查用户名是否已存在
                cursor.execute("SELECT COUNT(*) FROM users WHERE username = ?", (username,))
                if cursor.fetchone()[0] > 0:
                    messagebox.showerror("错误", f"用户名 '{username}' 已存在", parent=add_user_window)
                    username_entry.focus_set()
                    return

                # 添加新用户
                password_hash = hashlib.sha256(password.encode()).hexdigest()
                cursor.execute("INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)",
                               (username, password_hash, role))
                conn.commit()
                messagebox.showinfo("成功", f"用户 '{username}' 添加成功", parent=add_user_window)
                add_user_window.destroy()
                self.update_status(f"用户 '{username}' 已添加")
            except sqlite3.Error as e:
                conn.rollback()
                messagebox.showerror("数据库错误", f"添加用户失败: {str(e)}", parent=add_user_window)
            finally:
                conn.close()

        # 为按钮添加调试功能
        ttk.Button(button_frame, text="打印值", command=print_values).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="保存", command=save_user, width=10).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="取消", command=add_user_window.destroy, width=10).pack(side=tk.LEFT, padx=5)

    def modify_user(self):
        # 创建修改用户对话框
        modify_user_window = tk.Toplevel(self.root)
        modify_user_window.title("修改用户权限")
        modify_user_window.geometry("500x400")
        modify_user_window.transient(self.root)
        modify_user_window.grab_set()

        # 创建用户选择和修改框架
        frame = ttk.Frame(modify_user_window, padding="20 20 20 20")
        frame.pack(fill=tk.BOTH, expand=True)

        ttk.Label(frame, text="修改用户权限", font=("Arial", 14, "bold")).grid(column=0, row=0, columnspan=2, pady=10)

        # 创建用户列表框架
        list_frame = ttk.Frame(frame)
        list_frame.grid(column=0, row=1, columnspan=2, pady=10, sticky=tk.NSEW)
        frame.grid_rowconfigure(1, weight=1)
        frame.grid_columnconfigure(0, weight=1)

        # 创建用户列表
        columns = ("用户名", "角色")
        user_tree = ttk.Treeview(list_frame, columns=columns, show="headings", height=8)
        user_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # 添加滚动条
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=user_tree.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        user_tree.configure(yscrollcommand=scrollbar.set)

        # 设置列标题
        for col in columns:
            user_tree.heading(col, text=col)
            user_tree.column(col, width=100)

        # 加载用户数据
        cursor = self.conn.cursor()
        cursor.execute("SELECT user_id, username, role FROM users ORDER BY username")
        users = cursor.fetchall()

        for user in users:
            user_tree.insert("", tk.END, values=(user[1], user[2]), tags=(str(user[0]),))

        # 用户详情框架
        details_frame = ttk.LabelFrame(frame, text="用户详情", padding="10 10 10 10")
        details_frame.grid(column=0, row=2, columnspan=2, pady=10, sticky=tk.EW)

        ttk.Label(details_frame, text="用户名:").grid(column=0, row=0, sticky=tk.W, pady=5, padx=5)
        username_var = tk.StringVar()
        username_entry = ttk.Entry(details_frame, textvariable=username_var, width=25, state="readonly")
        username_entry.grid(column=1, row=0, pady=5, padx=5, sticky=tk.W)

        ttk.Label(details_frame, text="新角色:").grid(column=0, row=1, sticky=tk.W, pady=5, padx=5)
        role_var = tk.StringVar()
        role_combo = ttk.Combobox(details_frame, textvariable=role_var, width=23, state="readonly")
        role_combo['values'] = ('frontdesk', 'admin')
        role_combo.grid(column=1, row=1, pady=5, padx=5, sticky=tk.W)

        ttk.Label(details_frame, text="重置密码:").grid(column=0, row=2, sticky=tk.W, pady=5, padx=5)
        password_var = tk.StringVar()
        password_entry = ttk.Entry(details_frame, textvariable=password_var, show="*", width=25)
        password_entry.grid(column=1, row=2, pady=5, padx=5, sticky=tk.W)

        # 重置密码说明
        ttk.Label(details_frame, text="(留空表示不修改密码)").grid(column=2, row=2, sticky=tk.W, pady=5)

        # 存储当前选中的用户ID
        selected_user_id = tk.StringVar()

        # 用户选择事件
        def on_user_select(event):
            selected_items = user_tree.selection()
            if not selected_items:
                return

            item = selected_items[0]
            user_id = user_tree.item(item, "tags")[0]
            selected_user_id.set(user_id)

            # 获取用户详情
            cursor = self.conn.cursor()
            cursor.execute("SELECT username, role FROM users WHERE user_id = ?", (user_id,))
            user = cursor.fetchone()

            if user:
                username_var.set(user[0])
                role_var.set(user[1])
                password_var.set("")  # 清空密码字段

        user_tree.bind("<<TreeviewSelect>>", on_user_select)

        # 保存修改
        def save_changes():
            user_id = selected_user_id.get()
            if not user_id:
                messagebox.showerror("错误", "请先选择一个用户", parent=modify_user_window)
                return

            new_role = role_var.get()
            new_password = password_var.get()

            try:
                cursor = self.conn.cursor()

                # 更新角色
                cursor.execute("UPDATE users SET role = ? WHERE user_id = ?", (new_role, user_id))

                # 如果提供了新密码，则更新密码
                if new_password:
                    password_hash = self.hash_password(new_password)
                    cursor.execute("UPDATE users SET password_hash = ? WHERE user_id = ?", (password_hash, user_id))

                self.conn.commit()
                messagebox.showinfo("成功", f"用户 '{username_var.get()}' 的信息已更新", parent=modify_user_window)

                # 更新用户列表
                for item in user_tree.get_children():
                    if user_tree.item(item, "tags")[0] == user_id:
                        user_tree.item(item, values=(username_var.get(), new_role))
                        break

                self.update_status(f"用户 '{username_var.get()}' 的信息已更新")
            except sqlite3.Error as e:
                self.conn.rollback()
                messagebox.showerror("数据库错误", f"更新用户失败: {str(e)}", parent=modify_user_window)

        # 删除用户
        def delete_user():
            user_id = selected_user_id.get()
            if not user_id:
                messagebox.showerror("错误", "请先选择一个用户", parent=modify_user_window)
                return

            username = username_var.get()

            # 确认删除
            if not messagebox.askyesno("确认删除", f"确定要删除用户 '{username}' 吗？", parent=modify_user_window):
                return

            # 检查是否为当前登录用户
            if int(user_id) == self.current_user['user_id']:
                messagebox.showerror("错误", "不能删除当前登录的用户", parent=modify_user_window)
                return

            try:
                cursor = self.conn.cursor()
                cursor.execute("DELETE FROM users WHERE user_id = ?", (user_id,))
                self.conn.commit()

                # 从列表中移除
                selected_items = user_tree.selection()
                if selected_items:
                    user_tree.delete(selected_items[0])

                # 清空详情
                username_var.set("")
                role_var.set("")
                password_var.set("")
                selected_user_id.set("")

                messagebox.showinfo("成功", f"用户 '{username}' 已删除", parent=modify_user_window)
                self.update_status(f"用户 '{username}' 已删除")
            except sqlite3.Error as e:
                self.conn.rollback()
                messagebox.showerror("数据库错误", f"删除用户失败: {str(e)}", parent=modify_user_window)

        # 按钮框架
        button_frame = ttk.Frame(frame)
        button_frame.grid(column=0, row=3, columnspan=2, pady=15)

        ttk.Button(button_frame, text="保存修改", command=save_changes, width=12).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="删除用户", command=delete_user, width=12).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="关闭", command=modify_user_window.destroy, width=12).pack(side=tk.LEFT, padx=5)

    def view_users(self):
        # 创建查看用户列表的窗口
        view_users_window = tk.Toplevel(self.root)
        view_users_window.title("用户列表")
        view_users_window.geometry("600x400")
        view_users_window.transient(self.root)

        # 创建主框架
        frame = ttk.Frame(view_users_window, padding="20 20 20 20")
        frame.pack(fill=tk.BOTH, expand=True)

        ttk.Label(frame, text="系统用户列表", font=("Arial", 14, "bold")).pack(pady=10)

        # 创建用户表格
        columns = ("ID", "用户名", "角色", "创建时间")
        user_tree = ttk.Treeview(frame, columns=columns, show="headings", height=15)
        user_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # 添加滚动条
        scrollbar = ttk.Scrollbar(frame, orient=tk.VERTICAL, command=user_tree.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        user_tree.configure(yscrollcommand=scrollbar.set)

        # 设置列标题和宽度
        user_tree.heading("ID", text="ID")
        user_tree.column("ID", width=50, anchor=tk.CENTER)

        user_tree.heading("用户名", text="用户名")
        user_tree.column("用户名", width=150)

        user_tree.heading("角色", text="角色")
        user_tree.column("角色", width=100, anchor=tk.CENTER)

        user_tree.heading("创建时间", text="创建时间")
        user_tree.column("创建时间", width=150, anchor=tk.CENTER)

        # 加载用户数据
        # 注：SQLite默认不存储用户创建时间，这里我们假设有一个创建时间字段
        # 如果没有，我们可以在下面的查询中修改或省略该字段
        try:
            cursor = self.conn.cursor()
            # 尝试查询包含创建时间的表结构
            cursor.execute("PRAGMA table_info(users)")
            columns_info = cursor.fetchall()
            has_create_time = any(col[1] == 'create_time' for col in columns_info)

            if has_create_time:
                cursor.execute("SELECT user_id, username, role, create_time FROM users ORDER BY user_id")
            else:
                # 如果没有创建时间字段，我们使用"--"代替
                cursor.execute("SELECT user_id, username, role FROM users ORDER BY user_id")

            users = cursor.fetchall()

            for user in users:
                if has_create_time:
                    user_tree.insert("", tk.END, values=user)
                else:
                    # 添加"--"作为创建时间占位符
                    user_tree.insert("", tk.END, values=(user[0], user[1], user[2], "--"))

            self.update_status(f"已加载 {len(users)} 个用户记录")
        except sqlite3.Error as e:
            messagebox.showerror("数据库错误", f"加载用户数据失败: {str(e)}", parent=view_users_window)

        # 底部按钮
        button_frame = ttk.Frame(view_users_window)
        button_frame.pack(pady=15)

        ttk.Button(button_frame, text="刷新", command=lambda: self.refresh_user_list(user_tree, has_create_time),
                   width=10).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="关闭", command=view_users_window.destroy, width=10).pack(side=tk.LEFT, padx=5)

    def refresh_user_list(self, tree_view, has_create_time=False):
        # 清空现有数据
        for item in tree_view.get_children():
            tree_view.delete(item)

        # 重新加载数据
        try:
            cursor = self.conn.cursor()

            if has_create_time:
                cursor.execute("SELECT user_id, username, role, create_time FROM users ORDER BY user_id")
            else:
                cursor.execute("SELECT user_id, username, role FROM users ORDER BY user_id")

            users = cursor.fetchall()

            for user in users:
                if has_create_time:
                    tree_view.insert("", tk.END, values=user)
                else:
                    tree_view.insert("", tk.END, values=(user[0], user[1], user[2], "--"))

            self.update_status(f"用户列表已刷新，共 {len(users)} 条记录")
        except sqlite3.Error as e:
            messagebox.showerror("数据库错误", f"刷新用户数据失败: {str(e)}")

# ==== 主程序 ====
if __name__ == "__main__":
    def start_application(user):
        root = tk.Tk()
        app = HotelManagementSystem(root, user)
        root.mainloop()

    # 初始化数据库
    init_db()

    # 启动登录窗口
    login_window = lo.LoginWindow(start_application)
    login_window.mainloop()