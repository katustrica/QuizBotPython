from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text

from misc import dp, bot, admin_id
from .new_quiz import CreateQuiz


@dp.message_handler(commands='cancel', state='*')
@dp.message_handler(Text(equals='Отмена', ignore_case=True), state='*')
async def cmd_cancel(message: types.Message, state: FSMContext):  # обратите внимание на второй аргумент
    if message.from_user.id in admin_id:
        await state.finish()
        keyboard = types.ReplyKeyboardMarkup([
                ["Создать новый квиз"], ["Готовые квизы"]
            ], resize_keyboard=True)
        await message.answer("Хотите создать или активировать квиз?",
                              reply_markup=keyboard)

@dp.message_handler(commands=['start'], state='*')
async def cmd_start(message: types.Message, state: FSMContext):
    if message.from_user.id in admin_id:  # Подставьте сюда свой Telegram ID
        keyboard = types.ReplyKeyboardMarkup([
                ["Создать новый квиз"], ["Готовые квизы"]
            ], resize_keyboard=True)
        await message.answer("Хотите создать или активировать квиз?",
                              reply_markup=keyboard)


# @dp.message_handler(commands='set_commands', state='*')
# async def cmd_set_commands(message: types.Message):
#     if message.from_user.id in admin_id:  # Подставьте сюда свой Telegram ID
#         commands = [types.BotCommand(command='/new_quiz', description='Создать новый Квиз.'),
#                     types.BotCommand(command='/show_quiz', description='Посмотреть список Квизов.'),
#                     types.BotCommand(command='/delete_quiz', description='Удалить Квиз')]
#         await bot.set_my_commands(commands)
#         await message.answer('Команды настроены.')
