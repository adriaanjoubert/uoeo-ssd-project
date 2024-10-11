import sqlite3
from dataclasses import dataclass
from decimal import Decimal
from typing import Any


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

    def create_user(self, email: str, password: str) -> User:
        raise NotImplementedError

    def _sql_insert_user(self, **kwargs: Any) -> User:
        raise NotImplementedError

    def authenticate(self, email: str, password: str) -> User | None:
        raise NotImplementedError
