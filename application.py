from typing import Any

from exceptions import WeakPasswordError
from insecure_api import InsecureApp
from secure_api import SecureApp


class Session:

    def __init__(self) -> None:
        while True:
            menu = (
                "1. Run the software securely\n"
                "2. Run the software insecurely\n"
                "3. Exit"
            )
            print(menu)
            input_ = self._select_option()
            match input_:
                case 1:
                    self.app = SecureApp()
                case 2:
                    self.app = InsecureApp()
                case 3:
                    exit(0)
                case _ as c:
                    print(f"Invalid option: {c}")
                    continue

    def run(self) -> None:
        while True:
            self.main_menu()

    @staticmethod
    def _select_option() -> Any:
        return input("Select an option: ")

    def authenticate(self) -> None:
        menu = (
            "1. Log in\n"
            "2. Create account"
        )
        print(menu)
        input_ = self._select_option()
        match input_:
            case 1:
                pass
            case 2:
                self.create_account()
            case _:
                pass

    def create_account(self) -> None:
        email = input("email: ")
        password = input("Password: ")
        try:
            user = self.app.create_user(self, email=email, password=password)
        except WeakPasswordError:
            print("Weak password.")
        user.log_in()


def main() -> None:
    session = Session()
    session.run()


if __name__ == "__main__":
    main()
