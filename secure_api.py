from argon2 import PasswordHasher

from api import App, User


password_hasher = PasswordHasher()


class SecureApp(App):
    db_name = "secure.db"

    def __init__(self) -> None:
        super().__init__()
        self.cur.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT NOT NULL UNIQUE,
                password_hash TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                mfa_token_hash TEXT NULL,
                mfa_token_expires_at TIMESTAMP NULL,
                CHECK (
                    (mfa_token_hash IS NULL AND mfa_token_expires_at IS NULL)
                    OR (mfa_token_hash IS NOT NULL AND mfa_token_expires_at IS NOT NULL)
                )
            );
            """
        )
        self.db_conn.commit()

    def create_user(self, email: str, password: str) -> User:
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

    def _sql_select_user_by_email(self, email: str) -> User:
        row = self.cur.fetchone(
            """
            SELECT email, id, password_hash FROM users WHERE email = %s;
            """,
            email,
        )
        user = User(
            email=row[0],
            id=row[1],
            password_hash=row[2],
        )
        return user
