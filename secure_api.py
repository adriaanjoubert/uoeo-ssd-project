from dataclasses import dataclass
from decimal import Decimal

from argon2 import PasswordHasher
from password_strength import PasswordPolicy

import settings
from api import App, User, Product
from exceptions import WeakPasswordError
from settings import (
    PASSWORD_MIN_LENGTH,
    PASSWORD_MIN_UPPERCASE_LETTERS,
    PASSWORD_MIN_NUMBERS,
    PASSWORD_MIN_SPECIAL_CHARACTERS,
)

password_hasher = PasswordHasher()
password_policy = PasswordPolicy.from_names(
    length=PASSWORD_MIN_LENGTH,
    uppercase=PASSWORD_MIN_UPPERCASE_LETTERS,
    numbers=PASSWORD_MIN_NUMBERS,
    special=PASSWORD_MIN_SPECIAL_CHARACTERS,
)


@dataclass
class SecureUser(User):
    password_hash: str | None = ""


class SecureApp(App):
    db_name = "secure.db"

    def set_up_database(self) -> None:
        self.cur.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT NOT NULL UNIQUE,
                is_admin BOOLEAN DEFAULT false,
                password_hash TEXT NOT NULL,
                mfa_token_expires_at TIMESTAMP NULL,
                mfa_token_hash TEXT NOT NULL DEFAULT '',
                CHECK (
                    (mfa_token_hash == '' AND mfa_token_expires_at IS NULL)
                    OR (
                        mfa_token_hash <> ''
                        AND mfa_token_expires_at IS NOT NULL
                    )
                )
            );
            """
        )
        self.cur.execute(
            """
            CREATE TABLE IF NOT EXISTS password_reset_requests (
                user_id INTEGER REFERENCES users(id),
                token TEXT NOT NULL,
                token_expires_at TIMESTAMP NOT NULL
            );
            """
        )

        # Add admin user
        user = self._sql_select_user_by_email(email=settings.ADMIN_USER_EMAIL)
        if user is None:
            self.create_user(
                email=settings.ADMIN_USER_EMAIL,
                password=settings.ADMIN_USER_DEFAULT_PASSWORD,
            )
        self.db_conn.commit()

        super().set_up_database()

    def create_user(self, email: str, password: str) -> SecureUser:
        if password_policy.test(password):
            raise WeakPasswordError
        password_hash = password_hasher.hash(password)
        return self._sql_insert_user(email=email, password_hash=password_hash)

    def _sql_insert_user(self, email: str, password_hash: str) -> SecureUser:
        self.cur.execute(
            """
            INSERT INTO users (
                email,
                password_hash
            ) VALUES (
                ?,
                ?
            ) RETURNING id;
            """,
            (
                email,
                password_hash,
            ),
        )
        row = self.cur.fetchone()
        self.db_conn.commit()
        return SecureUser(
            email=email,
            id=row[0],
            password_hash=password_hash,
        )

    def _sql_insert_log_in_attempt(self, result_code: int, user: User) -> None:
        self.cur.execute(
            """
            INSERT INTO log_in_attempts (
                result_code,
                user_id
            ) VALUES (
                ?,
                ?
            );
            """,
            (result_code, user.id),
        )
        self.db_conn.commit()

    def authenticate(self, email: str, password: str) -> SecureUser | None:
        user = self._sql_select_user_by_email(email=email)
        if user is None:
            return None
        if password_hasher.verify(user.password_hash, password):
            return user
        return None

    def _sql_select_user_by_email(self, email: str) -> SecureUser | None:
        result = self.cur.execute(
            """
            SELECT email, id, password_hash FROM users WHERE email = ?;
            """,
            (email,),
        )
        row = result.fetchone()
        if row is None:
            return None
        user = SecureUser(
            email=row[0],
            id=row[1],
            password_hash=row[2],
        )
        return user

    def _sql_insert_product(self, price: Decimal, title: str) -> Product:
        self.cur.execute(
            """
            INSERT INTO products (
                price,
                title
            ) VALUES (
                ?,
                ?
            ) RETURNING id;
            """,
            (price, title),
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
            """
            SELECT id, price, title FROM products WHERE id = ?;
            """,
            (id_,),
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
