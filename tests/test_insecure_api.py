from decimal import Decimal
from unittest import TestCase

from api import User, Product
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

    def test_sql_select_product_by_id_injection(self) -> None:
        # Insert new product
        product_1 = self.app._sql_insert_product(price=Decimal(42), title="Product 1")

        # Check product exists
        product_2 = self.app._sql_select_product_by_id(id_=product_1.id)
        self.assertIsInstance(product_2, Product)
        self.assertEqual(product_2.id, product_1.id)
        self.assertEqual(product_2.price, Decimal(42))
        self.assertEqual(product_2.title, "Product 1")

        # Insert new product
        product_3 = self.app._sql_insert_product(price=Decimal(43), title="Product 2")

        # Check product exists
        product_4 = self.app._sql_select_product_by_id(id_=product_3.id)
        self.assertIsInstance(product_4, Product)
        self.assertEqual(product_4.id, product_3.id)
        self.assertEqual(product_4.price, Decimal(43))
        self.assertEqual(product_4.title, "Product 2")

        # Do SQL injection. This will always return the first row in the table regardless of the ID we pass.
        product_5 = self.app._sql_select_product_by_id(id_="abc123' OR '1'='1")
        self.assertIsInstance(product_5, Product)
        self.assertEqual(product_5.id, product_1.id)
        self.assertEqual(product_5.price, Decimal(42))
        self.assertEqual(product_5.title, "Product 1")
