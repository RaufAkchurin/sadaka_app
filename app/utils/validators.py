import phonenumbers
import validators
from tld import get_tld


def validate_link_url(value: str) -> str:
    if not value.startswith("https://"):
        raise ValueError("Ссылка должна начинаться с https://")

    if not validators.url(value):
        raise ValueError("Ссылка должна быть валидным URL")

    try:
        # Убедимся, что из URL можно извлечь валидный TLD
        # Например: example.com → com
        _ = get_tld(value, fail_silently=False)
    except Exception:
        raise ValueError("Ссылка содержит недопустимый или несуществующий домен")

    return value


def validate_phone(value: str) -> str:
    try:
        parsed = phonenumbers.parse(value, None)  # автоопределение страны по +XXX
        if not phonenumbers.is_valid_number(parsed):
            raise ValueError("Неверный формат номера телефона")
    except phonenumbers.NumberParseException:
        raise ValueError("Номер телефона только в формате +7xxxxxxxxxx")

    return phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.E164)
