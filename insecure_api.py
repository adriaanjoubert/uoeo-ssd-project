from api import App


class InsecureApp(App):
    db_name = "insecure.db"

    def __init__(self) -> None:
        super().__init__()
        self.cur.execute(
            """
            CREATE TABLE users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT NOT NULL UNIQUE,
                password TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                mfa_token TEXT NOT NULL,
            );
            """
        )
