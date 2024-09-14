from aiogram import types
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

start = types.ReplyKeyboardMarkup(resize_keyboard=True)

info = types.KeyboardButton("Информация")
stats = types.KeyboardButton("Статистика бота")
razrab = types.KeyboardButton("Разработчик бота")
user = types.KeyboardButton("Пользователь")
photo = types.KeyboardButton("Смешная картинка")
location = types.KeyboardButton("Моя геолокация", request_location=True)

start.add(info, stats, user, photo, razrab, location)

big_button_1 = InlineKeyboardButton(
    text='да',
    callback_data='join'
)

big_button_2 = InlineKeyboardButton(
    text='нет',
    callback_data='cancel'
)

stats = InlineKeyboardMarkup(
    inline_keyboard=[[big_button_1],
                     [big_button_2]]
)

user_id = InlineKeyboardButton(
    text='Хочу увидеть id',
    callback_data='user_id'
)

user_exit = InlineKeyboardButton(
    text='Вернуться обратно',
    callback_data='exit'
)

buttons_for_user = InlineKeyboardMarkup(
    inline_keyboard=[[user_id],
                     [user_exit]]
)