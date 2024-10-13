from dataclasses import dataclass
from decimal import Decimal

from api import App, User, Product


@dataclass
class InsecureUser(User):
    password: str | None = ""


class InsecureApp(App):
    db_name = "insecure.db"

    def __init__(self) -> None:
        super().__init__()
        self.set_up_database()

    def set_up_database(self) -> None:
        # Create tables
        self.cur.execute(
            """
            CREATE TABLE users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT NOT NULL UNIQUE,
                password TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                mfa_token TEXT NOT NULL DEFAULT ''
            );
            """
        )

    def create_user(self, email: str, password: str) -> InsecureUser:
        return self._sql_insert_user(email=email, password=password)

    def _sql_insert_user(self, email: str, password: str) -> InsecureUser:
        self.cur.execute(
            f"""
            INSERT INTO users (
                email,
                password
            ) VALUES (
                '{email}',
                '{password}'
            ) RETURNING id;
            """
        )
        row = self.cur.fetchone()
        self.db_conn.commit()
        return InsecureUser(
            email=email,
            id=row[0],
            password=password,
        )

    def authenticate(self, email: str, password: str) -> InsecureUser | None:
        user = self._sql_select_user_by_email(email=email)
        if user.password == password:
            return user
        return None

    def _sql_select_user_by_email(self, email: str) -> InsecureUser | None:
        result = self.cur.execute(
            """
            SELECT email, id, password FROM users WHERE email = ?;
            """,
            (email,),
        )
        row = result.fetchone()
        if row is None:
            return None
        user = InsecureUser(
            email=row[0],
            id=row[1],
            password=row[2],
        )
        return user

    def _sql_insert_product(self, price: Decimal, title: str) -> Product:
        self.cur.execute(
            f"""
            INSERT INTO products (
                price,
                title
            ) VALUES (
                '{price}',
                '{title}'
            ) RETURNING id;
            """
        )
        row = self.cur.fetchone()
        self.db_conn.commit()
        return Product(
            id=row[0],
            price=price,
            title=title,
        )

    def _sql_select_product_by_id(self, id_: int) -> Product | None:
        result = self.cur.execute(
            f"""
            SELECT id, price, title FROM products WHERE id = '{id_}';
            """
        )
        row = result.fetchone()
        if row is None:
            return None
        product = Product(
            id=row[0],
            price=row[1],
            title=row[2],
        )
        return product
