import os


class TestAppMixin:
    db_name: str

    def __init__(self) -> None:
        print("\nDeleting test database...")
        if os.path.exists(self.db_name):
            os.remove(self.db_name)
        print("Creating test database...")
        super().__init__()
