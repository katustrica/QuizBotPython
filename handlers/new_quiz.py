from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup

from misc import dp, bot, admin_id
from quizzer import Quiz, Question, quiz, current_round


class CreateQuiz(StatesGroup):
    waiting_for_quiz_name = State()
    waiting_for_round_name = State()
    waiting_for_time_between_questions = State()
    waiting_for_question = State()
    waiting_for_quiz = State()


@dp.message_handler(state=CreateQuiz.waiting_for_quiz_name, content_types=types.ContentTypes.TEXT)
async def set_name_for_quiz(message: types.Message):
    global quiz
    quiz = Quiz(message.text) # Подставьте сюда свой Telegram ID
    await CreateQuiz.waiting_for_round_name.set()
    await message.reply(
        'Пришлите название Вашего раунда (например, «История математики»).',
        reply_markup=types.ReplyKeyboardRemove()
    )


@dp.message_handler(state=CreateQuiz.waiting_for_round_name, content_types=types.ContentTypes.TEXT)
async def set_name_for_round(message: types.Message):
    global quiz
    quiz.add_round(message.text)
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add('15 сек.', '30 сек.', '1 мин.', '5 мин.', '10 мин.', '15 мин.')
    await CreateQuiz.waiting_for_time_between_questions.set()
    await message.reply('Какой промежуток будет между вопросами?', reply_markup=keyboard)


@dp.message_handler(state=CreateQuiz.waiting_for_time_between_questions, content_types=types.ContentTypes.TEXT)
async def set_time_between_questions(message: types.Message):
    global quiz
    quiz.set_time_between_quiestions(message.text)
    poll_keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    poll_keyboard.add(types.KeyboardButton(text="Создать вопрос",
                                           request_poll=types.KeyboardButtonPollType(type=types.PollType.QUIZ)))
    await CreateQuiz.waiting_for_question.set()
    await message.answer("Создайте вопрос, для этого используйте кнопку ниже.",
                         reply_markup=poll_keyboard)

