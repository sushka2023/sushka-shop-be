import re
from typing import Optional

NUMBER_REGEX = re.compile(r"№(\d+)")


def extract_warehouse_number(address: str, regex: re.Pattern) -> Optional[str]:
    match = regex.search(address)
    return match.group(1) if match else ""
