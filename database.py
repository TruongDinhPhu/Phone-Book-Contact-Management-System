import sqlite3

class Database:
    def __init__(self, db_name="phonebook_full.db"):
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()
        self.create_tables()
        self.seed_default_data()

    def create_tables(self):
        # 1. Bảng Users (Mục 6 - Data Model)
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS Users (
            user_id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            full_name TEXT NOT NULL,
            password_hash TEXT NOT NULL,
            email TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
        """)

        # 2. Bảng Contacts (Mục 6 - Data Model)
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS Contacts (
            contact_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            first_name TEXT NOT NULL,
            last_name TEXT,
            company TEXT,
            position TEXT,
            note TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES Users(user_id)
        )
        """)

        # 3. Bảng Groups (Mục 6 - Data Model)
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS Groups (
            group_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            group_name TEXT NOT NULL,
            description TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES Users(user_id)
        )
        """)

        # 4. Bảng Phones / Vertical Container (Mục 6)
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS Phones (
            phone_id INTEGER PRIMARY KEY AUTOINCREMENT,
            contact_id INTEGER NOT NULL,
            phone_number TEXT NOT NULL,
            phone_type TEXT DEFAULT 'Mobile',
            is_primary INTEGER DEFAULT 1,
            FOREIGN KEY (contact_id) REFERENCES Contacts(contact_id) ON DELETE CASCADE
        )
        """)

        # 5. Bảng Contact_Emails (Mục 6)
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS Contact_Emails (
            email_id INTEGER PRIMARY KEY AUTOINCREMENT,
            contact_id INTEGER NOT NULL,
            email_address TEXT,
            email_type TEXT DEFAULT 'Personal',
            is_primary INTEGER DEFAULT 1,
            FOREIGN KEY (contact_id) REFERENCES Contacts(contact_id) ON DELETE CASCADE
        )
        """)

        # 6. Bảng Contact_Group_Mapping (Mục 6)
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS Contact_Group_Mapping (
            mapping_id INTEGER PRIMARY KEY AUTOINCREMENT,
            contact_id INTEGER NOT NULL,
            group_id INTEGER NOT NULL,
            FOREIGN KEY (contact_id) REFERENCES Contacts(contact_id) ON DELETE CASCADE,
            FOREIGN KEY (group_id) REFERENCES Groups(group_id) ON DELETE CASCADE
        )
        """)
        self.conn.commit()

    def seed_default_data(self):
        # Thêm tài khoản test mặc định (Mục 7.1)
        self.cursor.execute("SELECT * FROM Users WHERE username = 'admin'")
        if not self.cursor.fetchone():
            self.cursor.execute("INSERT INTO Users (username, full_name, password_hash, email) VALUES ('admin', 'System Admin', '123456', 'admin@uth.edu.vn')")
            self.cursor.execute("INSERT INTO Users (username, full_name, password_hash, email) VALUES ('user1', 'Nguyễn Văn A', '123456', 'vana@gmail.com')")
            user_id = 1
            # Thêm nhóm mặc định (Mục 7.2)
            for g in ['Gia đình', 'Bạn bè', 'Đồng nghiệp', 'Nhóm khác']:
                self.cursor.execute("INSERT INTO Groups (user_id, group_name) VALUES (?, ?)", (user_id, g))
            self.conn.commit()

    # --- ĐĂNG NHẬP (Mục 1.0 DFD & 7.1) ---
    def authenticate(self, username, password):
        self.cursor.execute("SELECT user_id, full_name FROM Users WHERE username = ? AND password_hash = ?", (username, password))
        return self.cursor.fetchone()

    # --- KIỂM TRA TRÙNG SỐ ĐIỆN THOẠI (Mục 2.2 DFD & Mục 2 NFR) ---
    def check_duplicate_phone(self, phone_number, current_contact_id=None):
        if current_contact_id:
            self.cursor.execute("SELECT * FROM Phones WHERE phone_number = ? AND contact_id != ?", (phone_number, current_contact_id))
        else:
            self.cursor.execute("SELECT * FROM Phones WHERE phone_number = ?", (phone_number,))
        return self.cursor.fetchone() is not None

    # --- LẤY DANH SÁCH LIÊN HỆ THEO USER & KHU VỰC LỌC/TÌM KIẾM (Mục 3.0 DFD) ---
    def get_contacts(self, user_id, search_keyword="", group_filter="Tất cả"):
        query = """
        SELECT c.contact_id, c.first_name, c.last_name, p.phone_number, e.email_address, g.group_name
        FROM Contacts c
        LEFT JOIN Phones p ON c.contact_id = p.contact_id AND p.is_primary = 1
        LEFT JOIN Contact_Emails e ON c.contact_id = e.contact_id AND e.is_primary = 1
        LEFT JOIN Contact_Group_Mapping cgm ON c.contact_id = cgm.contact_id
        LEFT JOIN Groups g ON cgm.group_id = g.group_id
        WHERE c.user_id = ?
        """
        params = [user_id]

        if search_keyword:
            query += " AND (c.first_name LIKE ? OR c.last_name LIKE ? OR p.phone_number LIKE ?)"
            kw = f"%{search_keyword}%"
            params.extend([kw, kw, kw])

        if group_filter and group_filter != "Tất cả":
            query += " AND g.group_name = ?"
            params.append(group_filter)

        query += " GROUP BY c.contact_id ORDER BY c.first_name ASC"
        self.cursor.execute(query, params)
        return self.cursor.fetchall()

    # --- THÊM LIÊN HỆ (Mục 2.3 DFD) ---
    def add_contact(self, user_id, first_name, last_name, phone, email, group_name):
        if self.check_duplicate_phone(phone):
            return False, "Số điện thoại đã tồn tại trong hệ thống!"

        self.cursor.execute("INSERT INTO Contacts (user_id, first_name, last_name) VALUES (?, ?, ?)", (user_id, first_name, last_name))
        contact_id = self.cursor.lastrowid

        self.cursor.execute("INSERT INTO Phones (contact_id, phone_number) VALUES (?, ?)", (contact_id, phone))
        
        if email:
            self.cursor.execute("INSERT INTO Contact_Emails (contact_id, email_address) VALUES (?, ?)", (contact_id, email))

        if group_name and group_name != "Tất cả":
            self.cursor.execute("SELECT group_id FROM Groups WHERE user_id = ? AND group_name = ?", (user_id, group_name))
            grp = self.cursor.fetchone()
            if grp:
                self.cursor.execute("INSERT INTO Contact_Group_Mapping (contact_id, group_id) VALUES (?, ?)", (contact_id, grp[0]))

        self.conn.commit()
        return True, "Thêm liên hệ thành công!"

    # --- SỬA LIÊN HỆ (Mục 2.4 DFD) ---
    def update_contact(self, contact_id, user_id, first_name, last_name, phone, email, group_name):
        if self.check_duplicate_phone(phone, contact_id):
            return False, "Số điện thoại đã bị trùng với liên hệ khác!"

        self.cursor.execute("UPDATE Contacts SET first_name = ?, last_name = ?, updated_at = CURRENT_TIMESTAMP WHERE contact_id = ?", (first_name, last_name, contact_id))
        
        # Cập nhật SĐT
        self.cursor.execute("UPDATE Phones SET phone_number = ? WHERE contact_id = ? AND is_primary = 1", (phone, contact_id))
        
        # Cập nhật Email
        self.cursor.execute("DELETE FROM Contact_Emails WHERE contact_id = ?", (contact_id,))
        if email:
            self.cursor.execute("INSERT INTO Contact_Emails (contact_id, email_address) VALUES (?, ?)", (contact_id, email))

        # Cập nhật Nhóm
        self.cursor.execute("DELETE FROM Contact_Group_Mapping WHERE contact_id = ?", (contact_id,))
        if group_name and group_name != "Tất cả":
            self.cursor.execute("SELECT group_id FROM Groups WHERE user_id = ? AND group_name = ?", (user_id, group_name))
            grp = self.cursor.fetchone()
            if grp:
                self.cursor.execute("INSERT INTO Contact_Group_Mapping (contact_id, group_id) VALUES (?, ?)", (contact_id, grp[0]))

        self.conn.commit()
        return True, "Cập nhật thành công!"

    # --- XÓA LIÊN HỆ (Mục 2.5 DFD) ---
    def delete_contact(self, contact_id):
        self.cursor.execute("DELETE FROM Contacts WHERE contact_id = ?", (contact_id,))
        self.conn.commit()
        return True, "Đã xóa liên hệ thành công!"

    def get_user_groups(self, user_id):
        self.cursor.execute("SELECT group_name FROM Groups WHERE user_id = ?", (user_id,))
        return [r[0] for r in self.cursor.fetchall()]