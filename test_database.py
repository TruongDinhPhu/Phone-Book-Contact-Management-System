import unittest
import os
from database import Database

class TestPhoneBookDatabase(unittest.TestCase):
    def setUp(self):
        # Tạo cơ sở dữ liệu tạm thời dành riêng cho Unit Test
        self.test_db_file = "test_phonebook.db"
        self.db = Database(self.test_db_file)
        self.user_id = 1

    def tearDown(self):
        # Xóa file DB tạm sau khi test xong để dọn dẹp bộ nhớ
        self.db.conn.close()
        if os.path.exists(self.test_db_file):
            os.remove(self.test_db_file)

    def test_add_contact_success(self):
        """Test 1: Kiểm thử thêm liên hệ thành công"""
        success, msg = self.db.add_contact(self.user_id, "Nguyễn", "Văn Test", "0999888777", "test@gmail.com", "Gia đình")
        self.assertTrue(success)
        self.assertEqual(msg, "Thêm liên hệ thành công!")

    def test_add_duplicate_phone(self):
        """Test 2: Kiểm thử bắt lỗi trùng số điện thoại (Mục 2 NFR)"""
        self.db.add_contact(self.user_id, "User", "Một", "0912345678", "u1@gmail.com", "Bạn bè")
        success, msg = self.db.add_contact(self.user_id, "User", "Hai", "0912345678", "u2@gmail.com", "Bạn bè")
        self.assertFalse(success)
        self.assertIn("đã tồn tại", msg)

    def test_search_contact(self):
        """Test 3: Kiểm thử chức năng tìm kiếm liên hệ"""
        self.db.add_contact(self.user_id, "Trần", "Tìm Kiếm", "0900111222", "find@gmail.com", "Đồng nghiệp")
        results = self.db.get_contacts(self.user_id, search_keyword="Tìm Kiếm")
        self.assertGreater(len(results), 0)

    def test_delete_contact(self):
        """Test 4: Kiểm thử chức năng xóa liên hệ"""
        self.db.add_contact(self.user_id, "Lê", "Xóa", "0933444555", "delete@gmail.com", "Nhóm khác")
        results = self.db.get_contacts(self.user_id, search_keyword="Xóa")
        contact_id = results[0][0]
        
        success, msg = self.db.delete_contact(contact_id)
        self.assertTrue(success)
        
        after_delete = self.db.get_contacts(self.user_id, search_keyword="Xóa")
        self.assertEqual(len(after_delete), 0)

if __name__ == "__main__":
    unittest.main()