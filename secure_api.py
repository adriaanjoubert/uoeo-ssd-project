from argon2 import PasswordHasher
from password_strength import PasswordPolicy

import settings
from api import App, User
from exceptions import WeakPasswordError
from settings import PASSWORD_MIN_LENGTH, PASSWORD_MIN_UPPERCASE_LETTERS, PASSWORD_MIN_NUMBERS, \
    PASSWORD_MIN_SPECIAL_CHARACTERS

password_hasher = PasswordHasher()
password_policy = PasswordPolicy.from_names(
    length=PASSWORD_MIN_LENGTH,
    uppercase=PASSWORD_MIN_UPPERCASE_LETTERS,
    numbers=PASSWORD_MIN_NUMBERS,
    special=PASSWORD_MIN_SPECIAL_CHARACTERS,
)


class SecureApp(App):
    db_name = "secure.db"

    def __init__(self) -> None:
        super().__init__()
        self.set_up_database()

    def set_up_database(self) -> None:
        # Create tables
        self.cur.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT NOT NULL UNIQUE,
                is_admin BOOLEAN DEFAULT false,
                password_hash TEXT NOT NULL,
                mfa_token_expires_at TIMESTAMP NULL,
                mfa_token_hash TEXT NULL,
                CHECK (
                    (mfa_token_hash IS NULL AND mfa_token_expires_at IS NULL)
                    OR (mfa_token_hash IS NOT NULL AND mfa_token_expires_at IS NOT NULL)
                )
            );
            """
        )

        # Add admin user
        user = self._sql_select_user_by_email(email=settings.ADMIN_USER_EMAIL)
        if user is None:
            self.create_user(email=settings.ADMIN_USER_EMAIL, password=settings.ADMIN_USER_DEFAULT_PASSWORD)
        self.db_conn.commit()

    def create_user(self, email: str, password: str) -> User:
        if password_policy.test(password):
            raise WeakPasswordError
        password_hash = password_hasher.hash(password)
        return self._sql_insert_user(email=email, password_hash=password_hash)

    def _sql_insert_user(self, email: str, password_hash: str) -> User:
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
        return User(
            email=email,
            id=row[0],
            password_hash=password_hash,
        )

    def authenticate(self, email: str, password: str) -> User | None:
        user = self._sql_select_user_by_email(email=email)
        if password_hasher.verify(user.password_hash, password):
            return user
        return None

    def _sql_select_user_by_email(self, email: str) -> User | None:
        result = self.cur.execute(
            """
            SELECT email, id, password_hash FROM users WHERE email = ?;
            """,
            (email,),
        )
        row = result.fetchone()
        if row is None:
            return None
        user = User(
            email=row[0],
            id=row[1],
            password_hash=row[2],
        )
        return user
