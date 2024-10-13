import datetime
from dataclasses import dataclass
from decimal import Decimal

from api import App, User, Product
from constants.authentication import FAILED_LOG_IN_ACCOUNT_LOCK_MINUTES
from constants.log_in_attempt_result_codes import ACCESS_GRANTED_PASSWORD, ACCESS_DENIED_PASSWORD, \
    ACCESS_DENIED_ACCOUNT_LOCKED, ACCESS_GRANTED_TOKEN


@dataclass
class InsecureUser(User):
    password: str | None = ""


class InsecureApp(App):
    db_name = "insecure.db"

    def set_up_database(self) -> None:
        self.cur.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT NOT NULL UNIQUE,
                password TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                mfa_token TEXT NOT NULL DEFAULT ''
            );
            """
        )
        self.cur.execute(
            """
            CREATE TABLE IF NOT EXISTS password_reset_requests (
                user_id INTEGER REFERENCES users(id),
                token TEXT NOT NULL
            );
            """
        )
        super().set_up_database()

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

    def _sql_insert_log_in_attempt(self, result_code: int, user: User) -> None:
        self.cur.execute(
            f"""
            INSERT INTO log_in_attempts (
                result_code,
                user_id
            ) VALUES (
                '{result_code}',
                '{user.id}'
            );
            """
        )
        self.db_conn.commit()

    def _sql_failed_log_in_attempts(self, user: User) -> int:
        result = self.cur.execute(
            f"""
            SELECT COUNT(*)
            FROM log_in_attempts
            WHERE user_id = '{user.id}'
            AND created_at > '{datetime.datetime.now(tz=datetime.timezone.utc) - datetime.timedelta(minutes=FAILED_LOG_IN_ACCOUNT_LOCK_MINUTES)}'
            AND result_code <> '{ACCESS_GRANTED_PASSWORD}'
            AND result_code <> '{ACCESS_GRANTED_TOKEN}'
            """
        )
        row = result.fetchone()
        self.db_conn.commit()
        return row[0]

    def authenticate(self, email: str, password: str) -> InsecureUser | None:
        user = self._sql_select_user_by_email(email=email)
        if user is None:
            return None
        if self._sql_failed_log_in_attempts(user=user) >= 3:
            self._sql_insert_log_in_attempt(result_code=ACCESS_DENIED_ACCOUNT_LOCKED, user=user)
            return None
        if user.password == password:
            self._sql_insert_log_in_attempt(result_code=ACCESS_GRANTED_PASSWORD, user=user)
            return user
        self._sql_insert_log_in_attempt(result_code=ACCESS_DENIED_PASSWORD, user=user)
        return None

    def _sql_select_user_by_email(self, email: str) -> InsecureUser | None:
        result = self.cur.execute(
            f"""
            SELECT email, id, password FROM users WHERE email = '{email}';
            """
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
