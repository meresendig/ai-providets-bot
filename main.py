import logging
from aiogram import Bot, Dispatcher, executor, types
import requests
import json

API_TOKEN = '7659610571:AAFhbF0NT101W7RTTzNjEWil4sO7d44KQ1s'
SERVER_URL = 'https://your-backend-url.com'  # замените на реальный backend url

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    buttons = ["Хиромантия", "Натальная карта", "Гороскоп: день", "Гороскоп: неделя", "Гороскоп: месяц", "Гороскоп: год"]
    keyboard.add(*buttons)
    await message.answer("Добро пожаловать в AI-Провидец. Выберите тип анализа или введите /buy для получения доступа.", reply_markup=keyboard)

@dp.message_handler(lambda msg: msg.text == "Гороскоп: день")
async def horoscope_day(message: types.Message):
    await message.answer("Введите дату рождения в формате: ГГГГ-ММ-ДД")
    dp.register_message_handler(handle_horoscope_day_date, content_types=types.ContentTypes.TEXT)

async def handle_horoscope_day_date(message: types.Message):
    birth_date = message.text.strip()
    response = requests.post(f"{SERVER_URL}/astrology/horoscope", data={"period": "день", "birth_date": birth_date})
    await message.answer(response.json().get("result", "Ошибка при получении гороскопа."))

@dp.message_handler(content_types=['photo'])
async def handle_photo(message: types.Message):
    await message.answer("Спасибо за фото. Пожалуйста, укажите — это правая или левая ладонь?")

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
