import re

phone_pattern = re.compile(r'^(?:\+380|380|0)\d{9}$')


def validate_phone_number(phone_number: str):
    if not phone_pattern.match(phone_number):
        raise ValueError(
            'Phone number is not valid! The phone number must first consist of the symbols "+380" '
            'or "380" or "0" and than followed by nine digits.'
        )
