import re
import tkinter as tk
from tkinter import ttk, messagebox
from database import Database

class PhoneBookApp:
    def __init__(self, root):
        self.root = root
        self.root.title("PHONE BOOK MANAGEMENT SYSTEM - UTH")
        self.root.geometry("850x550")
        self.db = Database()
        self.current_user = None
        self.selected_contact_id = None
        
        # Mở màn hình Đăng nhập đầu tiên (Mục 7.1)
        self.show_login_screen()

    # ================= MÀN HÌNH ĐĂNG NHẬP (MỤC 7.1) =================
    def show_login_screen(self):
        for widget in self.root.winfo_children():
            widget.destroy()

        frame = tk.Frame(self.root, bg="#f0f0f0", padx=30, pady=30)
        frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

        tk.Label(frame, text="PHONE BOOK MANAGEMENT SYSTEM", font=("Arial", 14, "bold"), fg="#003366").pack(pady=5)
        tk.Label(frame, text="UTH - Phone Book", font=("Arial", 10, "italic")).pack(pady=5)
        
        tk.Label(frame, text="ĐĂNG NHẬP", font=("Arial", 12, "bold")).pack(pady=10)

        tk.Label(frame, text="Tên đăng nhập:").pack(anchor=tk.W, pady=2)
        self.username_entry = tk.Entry(frame, width=30)
        self.username_entry.insert(0, "admin")  # Tài khoản mẫu
        self.username_entry.pack(pady=2)

        tk.Label(frame, text="Mật khẩu:").pack(anchor=tk.W, pady=2)
        self.password_entry = tk.Entry(frame, width=30, show="*")
        self.password_entry.insert(0, "123456")  # Mật khẩu mẫu
        self.password_entry.pack(pady=2)

        tk.Button(frame, text="[ Đăng nhập ]", bg="#0056b3", fg="white", width=15, command=self.handle_login).pack(pady=15)
        tk.Label(frame, text="Quên mật khẩu?", fg="gray", cursor="hand2").pack()

    def handle_login(self):
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()

        user = self.db.authenticate(username, password)
        if user:
            self.current_user = {"id": user[0], "name": user[1]}
            messagebox.showinfo("Thành công", f"Chào mừng {user[1]} quay trở lại!")
            self.show_main_screen()
        else:
            messagebox.showerror("Lỗi", "Tên đăng nhập hoặc mật khẩu không chính xác!")

    # ================= MÀN HÌNH CHÍNH QUẢN LÝ DANH BẠ (MỤC 7.2) =================
    def show_main_screen(self):
        for widget in self.root.winfo_children():
            widget.destroy()

        # 1. Thanh Tiêu đề & Thông tin User
        top_bar = tk.Frame(self.root, bg="#003366", height=40, padx=10, pady=5)
        top_bar.pack(fill=tk.X)
        tk.Label(top_bar, text="PHONE BOOK MANAGEMENT SYSTEM (UTH)", font=("Arial", 11, "bold"), fg="white", bg="#003366").pack(side=tk.LEFT)
        tk.Button(top_bar, text="Đăng xuất", command=self.show_login_screen, bg="#d9534f", fg="white", bd=0).pack(side=tk.RIGHT)
        tk.Label(top_bar, text=f"Xin chào: {self.current_user['name']} | ", fg="white", bg="#003366").pack(side=tk.RIGHT)

        # 2. Thanh Tìm kiếm và Thêm liên hệ (Theo bản vẽ Mục 7.2)
        search_bar = tk.Frame(self.root, padx=10, pady=10)
        search_bar.pack(fill=tk.X)
        
        tk.Label(search_bar, text="Tìm kiếm:").pack(side=tk.LEFT, padx=5)
        self.search_entry = tk.Entry(search_bar, width=35)
        self.search_entry.pack(side=tk.LEFT, padx=5)
        self.search_entry.bind("<KeyRelease>", lambda e: self.load_contacts())

        tk.Button(search_bar, text="[+ Thêm liên hệ]", bg="#5cb85c", fg="white", font=("Arial", 9, "bold"), command=self.open_contact_dialog).pack(side=tk.RIGHT, padx=5)

        # 3. Thân ứng dụng: Menu Nhóm (bên trái) + Bảng danh sách (bên phải)
        main_body = tk.Frame(self.root, padx=10, pady=5)
        main_body.pack(fill=tk.BOTH, expand=True)

        # Cột Menu Nhóm (Left Panel - Mục 7.2)
        left_panel = tk.LabelFrame(main_body, text=" Menu Nhóm ", width=150, padx=5, pady=5)
        left_panel.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))

        self.selected_group = tk.StringVar(value="Tất cả")
        groups = ["Tất cả"] + self.db.get_user_groups(self.current_user['id'])
        for g in groups:
            rb = tk.Radiobutton(left_panel, text=g, variable=self.selected_group, value=g, command=self.load_contacts, anchor=tk.W)
            rb.pack(fill=tk.X, pady=3)

        # Bảng Danh sách Liên hệ (Right Panel - Treeview)
        right_panel = tk.Frame(main_body)
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        columns = ("id", "name", "phone", "email", "group")
        self.tree = ttk.Treeview(right_panel, columns=columns, show="headings")

        self.tree.heading("id", text="ID")
        self.tree.heading("name", text="Họ và Tên")
        self.tree.heading("phone", text="Số điện thoại")
        self.tree.heading("email", text="Email")
        self.tree.heading("group", text="Nhóm")

        self.tree.column("id", width=40, anchor=tk.CENTER)
        self.tree.column("name", width=180)
        self.tree.column("phone", width=130)
        self.tree.column("email", width=180)
        self.tree.column("group", width=100)

        self.tree.pack(fill=tk.BOTH, expand=True)

        # Khung nút thao tác Sửa / Xóa (Mục 7.2)
        action_bar = tk.Frame(right_panel, pady=10)
        action_bar.pack(fill=tk.X)

        tk.Button(action_bar, text="[Sửa]", bg="#f0ad4e", fg="white", width=10, command=self.edit_selected_contact).pack(side=tk.LEFT, padx=5)
        tk.Button(action_bar, text="[Xóa]", bg="#d9534f", fg="white", width=10, command=self.delete_selected_contact).pack(side=tk.LEFT, padx=5)

        self.load_contacts()

    # Tải danh sách liên hệ lên giao diện (Xử lý theo Mục 3.0 DFD)
    def load_contacts(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

        kw = self.search_entry.get().strip()
        grp = self.selected_group.get()
        contacts = self.db.get_contacts(self.current_user['id'], search_keyword=kw, group_filter=grp)

        for c in contacts:
            full_name = f"{c[1]} {c[2] if c[2] else ''}".strip()
            phone = c[3] if c[3] else "N/A"
            email = c[4] if c[4] else "N/A"
            group = c[5] if c[5] else "Chưa phân nhóm"
            self.tree.insert("", tk.END, values=(c[0], full_name, phone, email, group))

    # ================= CỬA SỔ POPUP: THÊM / SỬA LIÊN HỆ =================
    def open_contact_dialog(self, edit_data=None):
        dialog = tk.Toplevel(self.root)
        dialog.title("Chỉnh sửa liên hệ" if edit_data else "Thêm liên hệ mới")
        dialog.geometry("380x350")
        dialog.grab_set()

        tk.Label(dialog, text="Họ / Tên đệm (*):").pack(anchor=tk.W, padx=20, pady=2)
        fn_entry = tk.Entry(dialog, width=35)
        fn_entry.pack(padx=20, pady=2)

        tk.Label(dialog, text="Tên (*):").pack(anchor=tk.W, padx=20, pady=2)
        ln_entry = tk.Entry(dialog, width=35)
        ln_entry.pack(padx=20, pady=2)

        tk.Label(dialog, text="Số điện thoại (*):").pack(anchor=tk.W, padx=20, pady=2)
        phone_entry = tk.Entry(dialog, width=35)
        phone_entry.pack(padx=20, pady=2)

        tk.Label(dialog, text="Email:").pack(anchor=tk.W, padx=20, pady=2)
        email_entry = tk.Entry(dialog, width=35)
        email_entry.pack(padx=20, pady=2)

        tk.Label(dialog, text="Phân nhóm:").pack(anchor=tk.W, padx=20, pady=2)
        group_cb = ttk.Combobox(dialog, values=self.db.get_user_groups(self.current_user['id']), width=32)
        group_cb.current(0)
        group_cb.pack(padx=20, pady=2)

        # Nếu là Sửa -> Điền dữ liệu cũ vào các ô
        if edit_data:
            name_parts = edit_data[1].split(" ")
            fn_entry.insert(0, name_parts[0])
            ln_entry.insert(0, " ".join(name_parts[1:]) if len(name_parts) > 1 else "")
            phone_entry.insert(0, edit_data[2])
            email_entry.insert(0, edit_data[3] if edit_data[3] != "N/A" else "")
            group_cb.set(edit_data[4] if edit_data[4] != "Chưa phân nhóm" else "Gia đình")

        # Ràng buộc Dữ liệu - Data Validation (Mục 2 NFR)
        def save():
            fn = fn_entry.get().strip()
            ln = ln_entry.get().strip()
            ph = phone_entry.get().strip()
            em = email_entry.get().strip()
            grp = group_cb.get()

            if not fn or not ph:
                messagebox.showwarning("Cảnh báo", "Vui lòng nhập đầy đủ Tên và Số điện thoại!")
                return
            if not ph.isdigit() or not (10 <= len(ph) <= 11):
                messagebox.showerror("Lỗi định dạng", "Số điện thoại phải chứa 10-11 chữ số!")
                return
            if em and not re.match(r"[^@]+@[^@]+\.[^@]+", em):
                messagebox.showerror("Lỗi định dạng", "Email không đúng định dạng mẫu!")
                return

            if edit_data:
                success, msg = self.db.update_contact(edit_data[0], self.current_user['id'], fn, ln, ph, em, grp)
            else:
                success, msg = self.db.add_contact(self.current_user['id'], fn, ln, ph, em, grp)

            if success:
                messagebox.showinfo("Thành công", msg)
                dialog.destroy()
                self.load_contacts()
            else:
                messagebox.showerror("Lỗi", msg)

        tk.Button(dialog, text="Lưu liên hệ", bg="#0275d8", fg="white", command=save, width=15).pack(pady=15)

    def edit_selected_contact(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Thông báo", "Vui lòng chọn 1 dòng liên hệ trong bảng để sửa!")
            return
        item_values = self.tree.item(selected[0])['values']
        self.open_contact_dialog(edit_data=item_values)

    def delete_selected_contact(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Thông báo", "Vui lòng chọn 1 dòng liên hệ trong bảng để xóa!")
            return
        item_values = self.tree.item(selected[0])['values']
        
        confirm = messagebox.askyesno("Xác nhận xóa", f"Bạn có chắc muốn xóa liên hệ '{item_values[1]}'?")
        if confirm:
            self.db.delete_contact(item_values[0])
            messagebox.showinfo("Thành công", "Đã xóa liên hệ!")
            self.load_contacts()

if __name__ == "__main__":
    root = tk.Tk()
    app = PhoneBookApp(root)
    root.mainloop()