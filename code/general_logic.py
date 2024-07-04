from datetime import datetime, timedelta
import logging
from typing import Union

logging.basicConfig(level=logging.DEBUG)


def get_dates_and_type(
    text: dict[str],
) -> Union[tuple[datetime, datetime, str], Exception]:
    """Проверка на месяц/день/час/неделя, возвращает слайс времени и тип запроса"""
    try:
        type_of_request = text["group_type"]

        # Проверка, что dt_from и dt_upto являются строками и имеют правильный формат
        dt_from_raw, dt_upto_raw = text["dt_from"], text["dt_upto"]

        dt_from, dt_upto = datetime.fromisoformat(dt_from_raw), datetime.fromisoformat(
            dt_upto_raw
        )

        return dt_from, dt_upto, type_of_request
    except KeyError as e:
        return e
    except ValueError as e:
        return e


def prepare_dataset(data: list) -> str:
    """Обработка сырых данных, приводит к формату dataset:[], labels: []"""
    dataset = []
    labels = []

    if data[0]["_id"].get("week", None):
        for entry in data:
            labels.append(f"{entry["_id"]['year']}-{entry["_id"]['week']}")
            dataset.append(entry["total_value"])
        return str({"dataset": dataset, "labels": labels})

    for entry in data:
        _id = entry["_id"]

        year = _id.get("year")
        month = _id.get(
            "month", 1
        )  # Если ключ 'month' отсутствует, используется январь
        day = _id.get(
            "day", 1
        )  # Если ключ 'day' отсутствует, используется первый день месяца
        hour = _id.get("hour", 0)  # Если ключ 'hour' отсутствует, используется 000000

        date_str = datetime(year, month, day, hour).isoformat()

        labels.append(date_str)
        dataset.append(entry["total_value"])

    result = {"dataset": dataset, "labels": labels}
    return str(result)


def check_result_for_hours(dates: tuple[datetime, datetime], data: list[dict]) -> list:
    """Добавляет пустые значения для часовых данных"""
    start_date, end_date = dates
    expected_date = start_date

    datetime_to_dict = lambda dt: {
        "year": dt.year,
        "month": dt.month,
        "day": dt.day,
        "hour": dt.hour,
    }

    create_empty_value = lambda date_time: {
        "_id": {
            "year": date_time.year,
            "month": date_time.month,
            "day": date_time.day,
            "hour": date_time.hour,
        },
        "total_value": 0,
    }

    # Проверка и добавление пустых значений
    if data and data[0]["_id"] != datetime_to_dict(expected_date):
        data.insert(0, create_empty_value(expected_date))
        logging.debug("Inserting smth on first place")

    for i in range(1, len(data)):
        current_date = datetime(**data[i]["_id"])
        expected_date += timedelta(hours=1)

        if current_date != expected_date:
            data.insert(i, create_empty_value(expected_date))
            logging.debug("Just Inserting")

    if data[-1]["_id"] != datetime_to_dict(end_date):
        data.append(create_empty_value(end_date))
        logging.debug("Inserting last")

    return data


def check_result_for_days(dates: tuple[datetime, datetime], data: list[dict]) -> list:
    """Добавляет пустые значения для данных по дням"""
    start_date, end_date = dates
    expected_date = start_date

    datetime_to_dict = lambda dt: {"year": dt.year, "month": dt.month, "day": dt.day}

    create_empty_value = lambda date_time: {
        "_id": {"year": date_time.year, "month": date_time.month, "day": date_time.day},
        "total_value": 0,
    }

    # Проверка и добавление пустых значений
    if data and data[0]["_id"] != datetime_to_dict(expected_date):
        data.insert(0, create_empty_value(expected_date))

    for i in range(1, len(data)):
        current_date = datetime(**data[i]["_id"])
        expected_date += timedelta(days=1)

        if datetime_to_dict(current_date) != datetime_to_dict(expected_date):
            data.insert(i, create_empty_value(expected_date))

    if data[-1]["_id"] != datetime_to_dict(end_date):
        data.append(create_empty_value(end_date))
        logging.debug("Inserting last")

    return data


def check_result_for_weeks(dates: tuple[datetime, datetime], data: list[dict]) -> list:
    """Добавляет пустые значения для данных по неделям"""
    start_date, end_date = dates
    expected_date = start_date

    datetime_to_dict = lambda dt: {"year": dt.year, "week": dt.isocalendar()[1]}

    create_empty_value = lambda date_time: {
        "_id": {"year": date_time.year, "week": date_time.isocalendar()[1]},
        "total_value": 0,
    }
    print(start_date, end_date)

    # Проверка что существует первое значение, если нет - то заполняем его пустым
    if data[0]["_id"] != datetime_to_dict(expected_date):
        data.insert(0, create_empty_value(expected_date))

    for i in range(1, len(data)):
        current_date = datetime.fromisocalendar(
            **data[i]["_id"], day=expected_date.isoweekday()
        )
        expected_date += timedelta(weeks=1)

        if datetime_to_dict(current_date) != datetime_to_dict(expected_date):
            data.insert(i, create_empty_value(expected_date))

    return data


def check_result_for_months(dates: tuple[datetime, datetime], data: list[dict]) -> list:
    """Добавляет пустые значения для данных по месяцам"""
    start_date, end_date = dates
    expected_date = start_date.replace(day=1)

    datetime_to_dict = lambda dt: {"year": dt.year, "month": dt.month}

    create_empty_value = lambda date_time: {
        "_id": {"year": date_time.year, "month": date_time.month},
        "total_value": 0,
    }

    # Проверка и добавление пустых значений
    if data and data[0]["_id"] != datetime_to_dict(expected_date):
        data.insert(0, create_empty_value(expected_date))

    for i in range(1, len(data)):
        current_date = datetime(**data[i]["_id"], day=1)
        expected_date = (
            expected_date.replace(month=expected_date.month + 1)
            if expected_date.month + 1 < 13
            else datetime(year=expected_date.year + 1, month=1, day=1)
        )

        if datetime_to_dict(current_date) != datetime_to_dict(expected_date):
            data.insert(i, create_empty_value(expected_date))

    return data


check_result_dict = {
    # Словарь для выбора метода
    "hour": check_result_for_hours,
    "day": check_result_for_days,
    "week": check_result_for_weeks,
    "month": check_result_for_months,
}
