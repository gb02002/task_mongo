from datetime import datetime
from aiogram.types import Message
import json, logging
from exceptions import NotCorrectMessage, EmptyMessage

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


def validate_input(data) -> dict[str] | tuple[str, bool]:
    data_dict = json.loads(data)

    # Проверка на наличие всех необходимых ключей
    required_keys = ["dt_from", "dt_upto", "group_type"]
    for key in required_keys:
        if key not in data_dict:
            return f"Missing key: {key}", False

    # Проверка формата дат
    try:
        dt_from = datetime.fromisoformat(data_dict["dt_from"])
    except ValueError:
        raise NotCorrectMessage
    try:
        dt_upto = datetime.fromisoformat(data_dict["dt_upto"])
    except ValueError:
        raise NotCorrectMessage

    # Проверка значения group_type
    valid_group_types = ["hour", "week", "day", "month"]
    if data_dict["group_type"] not in valid_group_types:
        raise NotCorrectMessage

    # print("Valid input")
    return data_dict


def check_message(message: Message) -> dict[str] | tuple[str, Exception]:
    """Проверка формата сообщения, если прошел возвращает словарь, нет - тупл"""
    try:
        if message.text:
            logger.debug(message.text)
            data_dict = validate_input(message.text)
            if data_dict:
                return data_dict
        raise EmptyMessage
    except KeyError as e:
        logger.error(data_dict[1])
        return "Нет или не хватает ключей", e
    except NotCorrectMessage as e:
        return "Не прошла валидация", e
        # return None


def split_message(text: str, chunk_size: int = 4080) -> list[str]:
    """
    Разбивает текст на части по chunk_size символов.
    Добавляется маркировка очередности сообщений для consistence информации
    """
    return [
        f"Часть №{int(i / chunk_size)}\n" + text[i : i + chunk_size]
        for i in range(0, len(text), chunk_size)
    ]
