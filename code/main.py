import asyncio, logging, sys, os
import json.decoder

from aiogram import Bot, Dispatcher, html
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import CommandStart

from general_logic import get_dates_and_type, prepare_dataset, check_result_dict
from tg_logic import check_message, split_message
from db_interaction import execute_request_db
from aiogram.types import Message
from dotenv import load_dotenv
from exceptions import NotCorrectMessage, EmptyMessage

load_dotenv(dotenv_path="../.env")

BOT_TOKEN = os.getenv("BOT_TOKEN")

bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()


@dp.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    """Стартовая команда"""
    await message.answer(f"Hello, {html.bold(message.from_user.full_name)}!")


@dp.message()
async def handle_json(message: Message) -> None:
    """Handles json. Checks pattern, forwards logic"""
    try:
        correct_dataset = "Something occurred!"
        clean_message = check_message(message)  # Validation

        if isinstance(clean_message, tuple):
            await message.answer(clean_message[0])
            await message.answer(answers_str["format"])
            return None

        request_data = get_dates_and_type(
            clean_message
        )  # returns type of request day/hour/week/month
        raw_dataset = await execute_request_db(request_data)  # db interaction

        if not raw_dataset:
            await message.answer("Empty output")
            return None

        dataset = check_result_dict[request_data[2]](
            request_data[:2], raw_dataset
        )  # checks correctness
        correct_dataset = prepare_dataset(dataset)  # reformats to tg form

        await message.answer(correct_dataset)

    except TelegramBadRequest:
        list_of_responses = split_message(correct_dataset)
        for answers in list_of_responses:
            await message.answer(answers)
    except NotCorrectMessage:
        await message.answer(answers_str["possible"])
    except EmptyMessage:
        await message.answer("Ваше сообение пустое\n" + answers_str["format"])
    except json.decoder.JSONDecodeError:
        await message.answer(
            "Ваше сообение не в формате json\n" + answers_str["format"]
        )
    except Exception as e:
        logging.error(e)
        return None


async def main() -> None:
    await dp.start_polling(bot)


answers_str = {
    "possible": """Допустимо отправлять только следующие запросы:
{"dt_from": "2022-09-01T00:00:00", "dt_upto": "2022-12-31T23:59:00", "group_type": "month"}
{"dt_from": "2022-09-01T00:00:00", "dt_upto": "2022-11-30T23:59:00", "group_type": "week"}
{"dt_from": "2022-10-01T00:00:00", "dt_upto": "2022-11-30T23:59:00", "group_type": "day"}
{"dt_from": "2022-02-01T00:00:00", "dt_upto": "2022-02-02T00:00:00", "group_type": "hour"}""",
    "format": """Запрос должен быть в формате json, с подобной структурой:
dt_from и dt_upto в iso8601, group_type может быть hour/day/week/month""",
}

# Запуск бота
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
