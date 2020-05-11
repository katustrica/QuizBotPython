from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text

from misc import dp, bot, admin_id
from .new_quiz import CreateQuiz


@dp.message_handler(commands='cancel', state='*')
@dp.message_handler(Text(equals='Отмена', ignore_case=True), state='*')
async def cmd_cancel(message: types.Message, state: FSMContext):  # обратите внимание на второй аргумент
    # Сбрасываем текущее состояние пользователя и сохранённые о нём данные
    await state.finish()
    await message.answer('Действие отменено', reply_markup=types.ReplyKeyboardRemove())


@dp.message_handler(commands=['start'], state='*')
async def cmd_start(message: types.Message, state: FSMContext):
    if message.from_user.id == admin_id:  # Подставьте сюда свой Telegram ID
        await message.reply('Вы решили создать новый Квиз.\n'
                            'Для начала, пожалуйста, пришлите название'
                            'Вашего теста (например, «Квиз на знание математики»).\n'
                            'Или отправьте /cancel для отмены.', reply_markup=types.ReplyKeyboardRemove())
        await CreateQuiz.waiting_for_quiz_name.set()


# @dp.message_handler(commands='set_commands', state='*')
# async def cmd_set_commands(message: types.Message):
#     if message.from_user.id == admin_id:  # Подставьте сюда свой Telegram ID
#         commands = [types.BotCommand(command='/new_quiz', description='Создать новый Квиз.'),
#                     types.BotCommand(command='/show_quiz', description='Посмотреть список Квизов.'),
#                     types.BotCommand(command='/delete_quiz', description='Удалить Квиз')]
#         await bot.set_my_commands(commands)
#         await message.answer('Команды настроены.')
