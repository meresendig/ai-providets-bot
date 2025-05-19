
import logging
import os
from aiogram import Bot, Dispatcher, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils import executor
from dotenv import load_dotenv
import requests

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
SERVER_URL = os.getenv("SERVER_URL")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)
logging.basicConfig(level=logging.INFO)

# Меню
menu_keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
menu_keyboard.add(
    KeyboardButton("Хиромантия"),
    KeyboardButton("Натальная карта")
).add(
    KeyboardButton("Гороскоп: день"),
    KeyboardButton("Гороскоп: неделя")
).add(
    KeyboardButton("Гороскоп: месяц"),
    KeyboardButton("Гороскоп: год")
)

# Статус пользователя
user_states = {}

@dp.message_handler(commands=["start"])
async def start(message: types.Message):
    await message.answer(
        "Добро пожаловать в AI-Провидец.\nВыберите тип анализа или введите /buy для получения доступа.",
        reply_markup=menu_keyboard
    )

@dp.message_handler(commands=["buy"])
async def buy(message: types.Message):
    user_states[message.from_user.id] = {"access": True, "used_free": False}
    await message.answer("Бесплатный доступ активирован. Вы можете использовать функционал.")

@dp.message_handler(lambda m: m.text == "Хиромантия")
async def palmistry_prompt(message: types.Message):
    await message.answer("Пришлите фото **левой ладони**.")

@dp.message_handler(content_types=["photo"])
async def palm_analysis(message: types.Message):
    user_id = message.from_user.id
    if not user_states.get(user_id, {}).get("access"):
        await message.answer("Нет доступа. Введите /buy для активации.")
        return
    photo = message.photo[-1]
    photo_bytes = await photo.download(destination=bytes)
    files = {"file": photo_bytes.read()}
    resp = requests.post(f"{SERVER_URL}/palm", files=files)
    await message.answer(resp.json().get("result", "Ошибка анализа."))

@dp.message_handler(lambda m: m.text.startswith("Гороскоп"))
async def handle_horoscope(message: types.Message):
    period = message.text.split(": ")[-1]
    resp = requests.post(f"{SERVER_URL}/astrology/horoscope", data={"period": period})
    await message.answer(resp.json().get("result", "Ошибка гороскопа."))

@dp.message_handler(lambda m: m.text == "Натальная карта")
async def natal_chart_prompt(message: types.Message):
    await message.answer("Введите дату, время и город рождения в формате: 2020-01-01, 12:30, Москва")

@dp.message_handler(lambda m: "," in m.text and len(m.text.split(",")) == 3)
async def natal_chart_data(message: types.Message):
    try:
        date, time, city = map(str.strip, message.text.split(","))
        resp = requests.post(f"{SERVER_URL}/astrology/natal", data={
            "date": date,
            "time": time,
            "place": city
        })
        await message.answer(resp.json().get("result", "Ошибка натальной карты."))
    except Exception:
        await message.answer("Неверный формат. Введите как: 2020-01-01, 12:30, Москва")

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
