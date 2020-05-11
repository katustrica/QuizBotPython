from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup

from misc import dp, bot, admin_id
from quizzer import Quiz, Question, quiz, current_round


class CreateQuiz(StatesGroup):
    waiting_for_game_name = State()
    waiting_for_round_name = State()
    waiting_for_time_between_questions = State()
    waiting_for_quiz = State()

@dp.message_handler(state=CreateQuiz.waiting_for_game_name)
async def set_name_for_quiz(message: types.Message):
    game = Quiz(message.text) # Подставьте сюда свой Telegram ID
    await CreateQuiz.waiting_for_round_name.set()
    await message.reply("Пришлите название Вашего раунда (например, «История математики»).", reply_markup=types.ReplyKeyboardRemove())

@dp.message_handler(state=CreateQuiz.waiting_for_round_name)
async def set_name_for_round(message: types.Message):

