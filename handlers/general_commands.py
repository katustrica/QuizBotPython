from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
import time
from misc import dp, bot, admin_id
from .new_quiz import CreateQuiz
from .menu import get_current_quiz


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
    if message.from_user.id in admin_id:
        keyboard = types.ReplyKeyboardMarkup([
                ["Создать новый квиз"], ["Готовые квизы"]
            ], resize_keyboard=True)
        await message.answer("Хотите создать или активировать квиз?",
                              reply_markup=keyboard)
    else:
        try:
            quiz = get_current_quiz()
            await message.answer(f"Начался квиз - {quiz.quiz_name}")
        except AttributeError:
            await message.answer(f"Квиз не загружен. Увы :(")
        for round_name, quiz_round in quiz.rounds.items():
            current_round = round_name
            await message.answer(f"Раунд - {round_name}")
            await message.answer(f"Задержка между вопросами {quiz.times_between_questions[current_round]} сек.")
            for number, question in enumerate(quiz_round):

                await message.answer(f"Вопрос ")
                msg = await bot.send_poll(chat_id=message.chat.id, question=question.question_text,
                                          is_anonymous=False, options=question.options, type="quiz",
                                          correct_option_id=question.correct_option_id, open_period=question.open_period)
                time.sleep(quiz.times_between_questions[current_round])
                #TODO: тут надо сделать запись результатов.
                if number == len(quiz.rounds[current_round]):
                    await message.answer(f"Раунд {round_name} закончен")
            time.sleep(5)

# @dp.message_handler(commands='set_commands', state='*')
# async def cmd_set_commands(message: types.Message):
#     if message.from_user.id in admin_id:  # Подставьте сюда свой Telegram ID
#         commands = [types.BotCommand(command='/new_quiz', description='Создать новый Квиз.'),
#                     types.BotCommand(command='/show_quiz', description='Посмотреть список Квизов.'),
#                     types.BotCommand(command='/delete_quiz', description='Удалить Квиз')]
#         await bot.set_my_commands(commands)
#         await message.answer('Команды настроены.')
