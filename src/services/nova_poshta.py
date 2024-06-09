from typing import Optional


def parse_input(input_str: str) -> tuple[str, Optional[str]]:
    parts = input_str.split(",")
    city_name = parts[0].strip()
    area_name = parts[1].strip() if len(parts) > 1 else None
    return city_name, area_name
