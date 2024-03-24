import re

phone_pattern = re.compile(r'^(?:\+380|380|0)\d{9}$')
password_pattern = re.compile(r"^(?=.*[A-Z])(?=.*\d)(?=.*[^\w\s]).+$")


def validate_phone_number(phone_number: str):
    if phone_number:
        if not phone_pattern.match(phone_number):
            raise ValueError(
                'Phone number is not valid! The phone number must first consist of the symbols "+380" '
                'or "380" or "0" and than followed by nine digits.'
            )
        return phone_number
    return ""


def validate_password(password):
    if not password_pattern.match(password):
        raise ValueError(
            "Password is not valid! The password must consist of at least one lowercase, "
            "uppercase letter, number and symbols."
        )
