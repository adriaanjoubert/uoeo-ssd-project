from unittest import TestCase

from api import User
from insecure_api import InsecureApp
from tests.mixins import TestAppMixin


class TestInsecureApp(TestAppMixin, InsecureApp):
    db_name = "test_insecure.db"


class InsecureAppTestCase(TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        cls.app = TestInsecureApp()

    def test_create_user_ok(self) -> None:
        user = self.app.create_user(email="test1@example.com", password="Abcde12345!")
        self.assertIsInstance(user, User)
        self.assertEqual(user.email, "test1@example.com")
        self.assertEqual(user.password, "Abcde12345!")

    def test_create_user_ok_weak_password(self) -> None:
        user = self.app.create_user(email="test2@example.com", password="a")
        self.assertIsInstance(user, User)
        self.assertEqual(user.email, "test2@example.com")
        self.assertEqual(user.password, "a")
