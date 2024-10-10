import os
from unittest import TestCase

from api import User
from exceptions import WeakPasswordError
from secure_api import SecureApp, password_hasher


class TestSecureApp(SecureApp):
    db_name = "test_secure.db"

    def __init__(self) -> None:
        print("Deleting test database...")
        if os.path.exists(self.db_name):
            os.remove(self.db_name)
        print("Creating test database...")
        super().__init__()


class SecureAppTestCase(TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        cls.app = TestSecureApp()

    def test_create_user_ok(self) -> None:
        user = self.app.create_user(email="test@example.com", password="Abcde12345!")
        self.assertIsInstance(user, User)
        self.assertEqual(user.email, "test@example.com")
        self.assertTrue(password_hasher.verify(user.password_hash, "Abcde12345!"))

    def test_create_user_ko_weak_password(self) -> None:
        self.assertRaises(WeakPasswordError, self.app.create_user, email="test@example.com", password="abc123")
