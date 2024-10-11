from unittest import TestCase

from api import User
from exceptions import WeakPasswordError
from secure_api import SecureApp, password_hasher
from tests.mixins import TestAppMixin


class TestSecureApp(TestAppMixin, SecureApp):
    db_name = "test_secure.db"


class SecureAppTestCase(TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        cls.app = TestSecureApp()

    def test_create_user_ok(self) -> None:
        user = self.app.create_user(email="test1@example.com", password="Abcde12345!")
        self.assertIsInstance(user, User)
        self.assertEqual(user.email, "test1@example.com")
        self.assertTrue(password_hasher.verify(user.password_hash, "Abcde12345!"))

    def test_create_user_ko_weak_password(self) -> None:
        self.assertRaises(WeakPasswordError, self.app.create_user, email="test2@example.com", password="abc123")
