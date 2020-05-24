from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from misc import dp, admin_id
from quizzer import start_quiz_for_user
from .menu import menu_keyboard
from quizzer import quiz

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
        await start_quiz_for_user(message)

