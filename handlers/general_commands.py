from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from misc import bot, dp, admin_id
from user import User, get_all_users, set_all_users
from quizzer import Quiz, get_quiz
import logging
from .menu import menu_keyboard

@dp.message_handler(commands='cancel', state='*')
@dp.message_handler(Text(equals='Отмена', ignore_case=True), state='*')
async def cmd_cancel(message: types.Message, state: FSMContext):
    """
    Обработчик кнопки Отмена.

    Parameters
    ----------
    message : types.Message
        Текст сообщения (Отмена)
    state : FSMContext
        Сброс состояния пользователя.
    """
    if message.from_user.id in admin_id:
        await state.finish()
        await message.answer('Хотите создать или активировать квиз?',
                             reply_markup=menu_keyboard)


@dp.message_handler(commands=['start'], state='*')
async def cmd_start(message: types.Message):
    """
    Обработчик кнопки старт. Определяет от кого пришло сообщение.

    Parameters
    ----------
    message : types.Message
        Текст сообщения
    """
    if message.from_user.id in admin_id:
        await message.answer('Хотите создать или активировать квиз?',
                             reply_markup=menu_keyboard)
    else:
        quiz_game = get_quiz()
        if isinstance(quiz_game, Quiz):
            logging.info(f'Пользователь {message.from_user.full_name} опоздал.')
            await message.answer(f'Вы опоздали.')
        else:
            all_users = get_all_users()
            all_users[message.from_user.id] = User(message.from_user.full_name)
            set_all_users(all_users)
            for id in admin_id:
                await bot.send_message(
                    id,
                    f'Пользователь {message.from_user.full_name} ждет начала квиза.'
                    f'Всего пользователей {len(all_users)}'
                )
            logging.info(f'Пользователь {message.from_user.full_name} ждет начала квиза.')
            await message.answer(f'Ждите начала квиза.')
