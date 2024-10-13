import sqlite3
from dataclasses import dataclass
from decimal import Decimal
from typing import Any
from uuid import UUID


@dataclass
class Product:
    id: int
    price: Decimal
    title: str


@dataclass
class User:
    email: str
    id: int


class App:
    db_name: str

    def __init__(self) -> None:
        self.db_conn = sqlite3.connect(self.db_name)
        self.cur = self.db_conn.cursor()
        self.set_up_database()

    def set_up_database(self) -> None:
        # Setup tables
        self.cur.execute(
            """
            CREATE TABLE IF NOT EXISTS products (
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                price DECIMAL(10, 2) NOT NULL,
                title TEXT NOT NULL
            );
            """
        )
        self.cur.execute(
            """
            CREATE TABLE IF NOT EXISTS log_in_attempts (
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                result_code INTEGER NOT NULL,
                user_id INTEGER REFERENCES users(id)
            );
            """
        )

    def create_user(self, email: str, password: str) -> User:
        raise NotImplementedError

    def _sql_insert_user(self, **kwargs: Any) -> User:
        raise NotImplementedError

    def authenticate(self, email: str, password: str) -> User | None:
        raise NotImplementedError

    def _sql_insert_password_reset_request(
        self,
        email: str,
        token: UUID,
    ) -> None:
        raise NotImplementedError

    def _sql_select_products(self) -> list[Product]:
        result = self.cur.execute(
            """
            SELECT id, price, title FROM products;
            """
        )
        rows = result.fetchall()
        products = []
        for row in rows:
            products.append(
                Product(
                    id=row[0],
                    price=row[1],
                    title=row[2],
                )
            )
        return products

    def email(self, content: str, email: str) -> None:
        # TODO: Send email asynchronously
        pass
