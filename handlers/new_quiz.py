from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher.filters import Text
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
    quiz = Quiz(message.text)
    await CreateQuiz.waiting_for_round_name.set()
    await message.reply(
        'Пришлите название Вашего раунда (например, «История математики»).',
        reply_markup=types.ReplyKeyboardRemove()
    )


@dp.message_handler(state=CreateQuiz.waiting_for_round_name, content_types=types.ContentTypes.TEXT)
async def set_name_for_round(message: types.Message):
    global current_round
    current_round = message.text
    quiz.add_round(message.text)
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add('15 сек.', '30 сек.', '1 мин.', '5 мин.', '10 мин.', '15 мин.')
    await CreateQuiz.waiting_for_time_between_questions.set()
    await message.reply('Какой промежуток будет между вопросами?', reply_markup=keyboard)


@dp.message_handler(state=CreateQuiz.waiting_for_time_between_questions, content_types=types.ContentTypes.TEXT)
async def set_time_between_questions(message: types.Message):
    quiz.set_time_between_quiestions(message.text)
    poll_keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    poll_keyboard.add(types.KeyboardButton(text="Создать вопрос",
                                           request_poll=types.KeyboardButtonPollType(type=types.PollType.QUIZ)))
    await CreateQuiz.waiting_for_question.set()
    await message.answer("Создайте вопрос, для этого используйте кнопку ниже.",
                         reply_markup=poll_keyboard)


@dp.message_handler(state=CreateQuiz.waiting_for_question, content_types=types.ContentTypes.POLL)
async def setup_question_for_quiz(message: types.Message):
    quiz.add_question(message.poll.question, message.poll.options, message.poll.correct_option_id)
    poll_keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    poll_keyboard.add(types.KeyboardButton(text="Создать еще вопрос",
                                           request_poll=types.KeyboardButtonPollType(type=types.PollType.QUIZ)))
    poll_keyboard.add(types.KeyboardButton(text="Закончить создание вопросов и создать новый раунд."))
    poll_keyboard.add(types.KeyboardButton(text="Закончить создание квиза."))
    await message.reply(f"Был добавлен вопрос '{message.poll.question}'", reply_markup=poll_keyboard)


@dp.message_handler(Text(equals="Закончить создание вопросов и создать новый раунд.", ignore_case=True), state='*')
async def cmd_cancel_creating_poll(message: types.Message):
    poll_keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    await message.reply(
        f'Имя игры: {quiz.quiz_name}\n'
        f'Текущий раунд: {current_round}\n'
        f'Задержка между вопросами (сек.): {quiz.times_between_questions[current_round]}\n'
        f'Количество вопросов: {len(quiz.rounds[current_round])}\n',
        reply_markup=types.ReplyKeyboardRemove()
    )
    await CreateQuiz.waiting_for_round_name.set()
    await message.reply(
        'Пришлите название Вашего раунда (например, «История математики»).',
        reply_markup=types.ReplyKeyboardRemove()
    )


@dp.message_handler(Text(equals="Закончить создание квиза.", ignore_case=True), state='*')
async def cmd_finish_quiz(message: types.Message):
    poll_keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    CreateQuiz.waiting_for_quiz.set()
    await message.reply(
        f'Имя игры: {quiz.quiz_name}\n'
        f'Названия раундов: {list(quiz.rounds.keys())}\n'
        f'Задержка между вопросами (сек.): {list(quiz.times_between_questions.values())}\n'
        f'Количество раундов: {len(quiz.rounds.values())}\n', #нахуй не вперлось
        reply_markup=types.ReplyKeyboardRemove()
    )
    quiz.to_json()