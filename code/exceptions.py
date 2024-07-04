# Кастомные исключения


class NotCorrectMessage(Exception):
    """Некорректное сообщение в бот, которое не удалось распарсить"""
    pass


class EmptyMessage(Exception):
    """Пустое сообщение"""
    pass
