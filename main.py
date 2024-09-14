from aiogram import Bot, types
from aiogram.utils import executor
import asyncio
from aiogram.dispatcher import Dispatcher
from aiogram.types import (ReplyKeyboardRemove, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup,
                           InlineKeyboardButton)

from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Command
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import StatesGroup, State

import keyboard
import config
import logging

storage = MemoryStorage()
bot = Bot(token=config.botkey, parse_mode=types.ParseMode.HTML)
dp = Dispatcher(bot, storage=storage)
logging.basicConfig(format=u'%(filename)s [LINE:%(lineno)d] #%(levelname)-8s [%(asctime)s] %(message)s',
                    level=logging.INFO)


class MeInfo(StatesGroup):
    Q1 = State()
    Q2 = State()


@dp.message_handler(Command("me"), state=None)  # создаем комупндк me для админа
async def enter_MeInfo(message: types.Message):
    if message.chat.id == config.admin:
        await message.answer("начинаем настройку \n"  # бот спрашивает ссылку
                             f"введите линк на ваш профиль")

        await MeInfo.Q1.set()


@dp.message_handler(state=MeInfo.Q1)  # как только бот получит ответ выполнится вот это
async def answer_Q1(message: types.Message, state: FSMContext):
    answer = message.text
    await state.update_data(answer1=answer)  # тут же он записывает наш ответ (линк)
    await message.answer("линк сохранен\n"
                         "введите текст")
    await MeInfo.Q2.set()  # жлет пока мы вводим текст


@dp.message_handler(state=MeInfo.Q2)  # текст пришел переходим сюда
async def answer_Q2(message: types.Message, state: FSMContext):
    answer = message.text
    await state.update_data(answer2=answer)  # записываем второй ответ

    await message.answer("текст сохранен")

    data = await state.get_data()
    answer1 = data.get("answer1")  # ответы в перменную, чтобы они были вмесет в файле
    answer2 = data.get("answer2")

    joinedFile = open('link.txt', 'w', encoding='UTF-8')
    joinedFile.write(str(answer1))
    joinedFile = open('text.txt', 'w', encoding='UTF-8')
    joinedFile.write(str(answer2))

    await message.answer(f'ваша ссылка {answer1}, ваш текст {answer2}')

    await state.finish()


@dp.message_handler(Command("start"), state=None)
async def welcome(message):
    file = open("user.txt", "r")
    user = set()
    for line in file:
        user.add(line.strip())

    if not str(message.chat.id) in user:
        file = open('user.txt', "a")
        file.write(str(message.chat.id) + "\n")
        user.add(message.chat.id)

    await bot.send_message(message.chat.id, f'привт *{message.from_user.first_name}* бот работает',
                           reply_markup=keyboard.start, parse_mode='Markdown')


@dp.message_handler(commands=['rassilka'])
async def rassilka(message):
    if message.chat.id == config.admin:
        await bot.send_message(message.chat.id, f"*рассылка началась"
                                                f"\n бот оповестит, кодга рассылка закончится*", parse_mode="Markdown")
        receive_users, block_users = 0, 0
        file = open('user.txt', 'r')
        users = set()
        for line in file:
            users.add(line.strip())
        file.close()
        for user in users:
            try:
                await bot.send_photo(user, open('crocodil.png', 'rb'))
                receive_users += 1
            except:
                block_users += 1
            await asyncio.sleep(0.4)
        await bot.send_message(message.chat.id, f'расслыка завершена\n'
                                                f'получили сообщение: {receive_users} \n'
                                                f'заблокировали бота: {block_users}', parse_mode='Markdown')


@dp.message_handler(content_types=['location'])
async def handle_location(message: types.Message):
    if message.location:
        latitude = message.location.latitude
        longitude = message.location.longitude
        await bot.send_message(message.chat.id, text=f'Ваша геолокация: долгота {longitude}, широта {latitude}',
                               parse_mode='Markdown')


@dp.message_handler(content_types=['text'])
async def get_message(message):
    if message.text == "Информация":
        await bot.send_message(message.chat.id, text='Информация \n Бот создан специально для обучения',
                               parse_mode='Markdown')

    if message.text == "Статистика":
        await bot.send_message(message.chat.id, text='ХОчешь просмотреть статистику бота', reply_markup=keyboard.stats,
                               parse_mode='Markdown')

    if message.text == "Разработчик":
        link1 = open('link.txt', encoding="utf-8")
        link = link1.read()

        text1 = open('text.txt', encoding="utf-8")
        text = text1.read()

        await bot.send_message(message.chat.id, text=f'Сохдатель бота: {link, text}', parse_mode='HTML')

    if message.text == "Пользователь":
        await bot.send_message(message.chat.id, text='ХОчешь просмотреть статистику бота',
                               reply_markup=keyboard.buttons_for_user, parse_mode='Markdown')

    if message.text == "Фото":
        await bot.send_photo(message.chat.id, open('png.png', 'rb'), parse_mode='Markdown')



@dp.callback_query_handler(text_contains='user_id')
async def callback(call: types.CallbackQuery):
    user_id = call.from_user.id
    await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                text=f'твой id {user_id}', parse_mode='Markdown')


@dp.callback_query_handler(text_contains='exit')
async def callback(call: types.CallbackQuery):
    await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                text=f'Вы отменили выбор', parse_mode='Markdown')


@dp.callback_query_handler(text_contains='join')
async def callback(call: types.CallbackQuery):
    if call.message.chat.id == config.admin:
        d = sum(1 for line in open('user.txt'))
        await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                    text=f'Вот статистика: *{d}* человек', parse_mode='Markdown')
    else:
        await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                    text=f'Ты балбеска', parse_mode='Markdown')


@dp.callback_query_handler(text_contains=['cancel'])
async def callback(call: types.CallbackQuery):
    await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                text='В галвное меню акрнулся', parse_mode='Markdown')


if __name__ == '__main__':
    print("бот запущен")
    executor.start_polling(dp)
