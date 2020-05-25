from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from misc import dp, admin_id
from user import User, get_all_users, set_all_users
from quizzer import Quiz, get_quiz
from .menu import menu_keyboard

@dp.message_handler(commands='cancel', state='*')
@dp.message_handler(Text(equals='Отмена', ignore_case=True), state='*')
async def cmd_cancel(message: types.Message, state: FSMContext):
    if message.from_user.id in admin_id:
        await state.finish()
        await message.answer('Хотите создать или активировать квиз?',
                             reply_markup=menu_keyboard)


@dp.message_handler(commands=['start'], state='*')
async def cmd_start(message: types.Message):
    if message.from_user.id in admin_id:
        await message.answer('Хотите создать или активировать квиз?',
                             reply_markup=menu_keyboard)
    else:
        all_users = get_all_users()
        all_users[message.from_user.id] = User(message.from_user.full_name)
        set_all_users(all_users)
        quiz_game = get_quiz()
        if isinstance(quiz_game, Quiz):
            await quiz_game.start_rounds()
        else:
            await message.answer(f'Квиз не загружен.')

