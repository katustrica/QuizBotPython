from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
import time
from misc import dp, bot, admin_id
from user import User, all_users
from .new_quiz import CreateQuiz
from .menu import get_current_quiz
current_question_correct_id = None

@dp.message_handler(commands='cancel', state='*')
@dp.message_handler(Text(equals='Отмена', ignore_case=True), state='*')
async def cmd_cancel(message: types.Message, state: FSMContext):
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
            all_users[message.from_user.id] = User(message.from_user.full_name)
        except AttributeError:
            await message.answer(f"Квиз не загружен. Увы :(")
        for round_name, quiz_round in quiz.rounds.items():
            await message.answer(f"Раунд - {round_name}")
            await message.answer(f"Задержка между вопросами {quiz.times_between_questions[round_name]} сек.")
            for number, question in enumerate(quiz_round):
                global current_question_correct_id
                current_question_correct_id = question.correct_option_id
                await bot.send_poll(chat_id=message.chat.id, question=question.question_text,
                                    is_anonymous=False, options=question.options, type="quiz",
                                    correct_option_id=question.correct_option_id, open_period=question.open_time)
                time.sleep(quiz.times_between_questions[round_name])
                if number == len(quiz.rounds[round_name]):
                    await message.answer(f"Раунд {round_name} закончен")
            time.sleep(5)

        await message.answer(f'Поздравляю!!! Квиз окончен, вы набрали {all_users[message.from_user.id].score} очков.')

        results = '\n'.join([user.result for user in all_users.values()])
        for id in admin_id:
            await bot.send_message(id, results)

@dp.poll_answer_handler()
async def handle_poll_answer(quiz_answer: types.PollAnswer):
    if current_question_correct_id == quiz_answer.option_ids[0]:
        all_users[quiz_answer.user.id].add_score()
