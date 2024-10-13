import uuid
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
                    break
                case 2:
                    self.app = InsecureApp()
                    break
                case 3:
                    exit(0)
                case _ as c:
                    print(f"Invalid option: {c}")
                    continue
        self.authenticate()

    @staticmethod
    def _select_option() -> Any:
        input_ = input("Select an option: ")
        while True:
            try:
                return int(input_)
            except ValueError:
                print(f"Invalid option: {input_}")

    def authenticate(self) -> None:
        while True:
            menu = (
                "1. Log in\n"
                "2. Create account\n"
                "3. Reset password\n"
                "4. Exit"
            )
            print(menu)
            input_ = self._select_option()
            match input_:
                case 1:
                    self.log_in()
                    break
                case 2:
                    self.create_account()
                    break
                case 3:
                    self.reset_password()
                    break
                case 4:
                    exit(0)
                case _:
                    print("Invalid option")
        self.main_menu()

    def log_in(self) -> None:
        while True:
            email = input("Email: ")
            password = input("Password: ")
            user = self.app.authenticate(email=email, password=password)
            if user is None:
                print("Incorrect email or password")
                continue
            else:
                self.user = user
                break
        print("You are now logged in")
        self.main_menu()

    def create_account(self) -> None:
        while True:
            email = input("Email: ")
            password = input("Password: ")
            try:
                user = self.app.create_user(email=email, password=password)
                self.user = user
                break
            except WeakPasswordError:
                print("Weak password.")
                continue
        self.authenticate()

    def reset_password(self) -> None:
        email = input("Email: ")
        user = self.app._sql_select_user_by_email(email=email)
        if user is not None:
            token = uuid.uuid4()
            self.app._sql_insert_password_reset_request(
                token=token,
                user_id=user.id,
            )
            self.app.email(
                content=f"Your password reset token is {token}",
                email=user.email,
            )
        print(
            "If an account with that email exists then we will send it"
            " the password reset instructions shortly."
        )
        self.authenticate()

    def main_menu(self) -> None:
        while True:
            menu = (
                "1. List products\n"
                "2. View cart & checkout\n"
                "3. Log out\n"
                "4. Exit"
            )
            print(menu)
            input_ = self._select_option()
            match input_:
                case 1:
                    self.list_products()
                case 2:
                    self.view_cart()
                case 3:
                    self.log_out()
                case 4:
                    exit(0)

    def list_products(self) -> None:
        pass

    def view_cart(self) -> None:
        pass

    def log_out(self) -> None:
        self.user = None
        self.authenticate()


def main() -> None:
    Session()


if __name__ == "__main__":
    main()
