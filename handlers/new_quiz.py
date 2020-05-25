from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher.filters import Text

from misc import dp
from .menu import menu_keyboard
from quizzer import Quiz, set_quiz, get_quiz, get_current_round, set_current_round


class CreateQuiz(StatesGroup):
    waiting_for_quiz_name = State()
    waiting_for_round_name = State()
    waiting_for_time_between_questions = State()
    waiting_for_question = State()


@dp.message_handler(Text(equals='Создать новый квиз', ignore_case=True), state='*')
async def create_new_quiz(message: types.Message):
    await message.reply('Вы решили создать новый Квиз.\n'
                        'Для начала, пожалуйста, пришлите название\n'
                        'Вашего теста (например, «Квиз на знание математики»).\n'
                        'Или отправьте /cancel для отмены.', reply_markup=types.ReplyKeyboardRemove())
    await CreateQuiz.waiting_for_quiz_name.set()


@dp.message_handler(state=CreateQuiz.waiting_for_quiz_name, content_types=types.ContentTypes.TEXT)
async def set_name_for_quiz(message: types.Message):
    set_quiz(Quiz(message.text))
    await CreateQuiz.waiting_for_round_name.set()
    await message.reply(
        'Пришлите название Вашего раунда (например, «История математики»).',
        reply_markup=types.ReplyKeyboardRemove()
    )


@dp.message_handler(state=CreateQuiz.waiting_for_round_name, content_types=types.ContentTypes.TEXT)
async def set_name_for_round(message: types.Message):
    set_current_round(message.text)
    quiz = get_quiz()
    quiz.add_round(message.text)
    set_quiz(quiz)
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add('15 сек.', '30 сек.', '1 мин.', '5 мин.', '10 мин.', 'Отмена')
    await CreateQuiz.waiting_for_time_between_questions.set()
    await message.reply('Какой промежуток будет между вопросами?', reply_markup=keyboard)


@dp.message_handler(state=CreateQuiz.waiting_for_time_between_questions, content_types=types.ContentTypes.TEXT)
async def set_time_between_questions(message: types.Message):
    quiz = get_quiz()
    quiz.set_time_between_quiestions(message.text)
    set_quiz(quiz)
    poll_keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    poll_keyboard.add(types.KeyboardButton(text='Создать вопрос',
                                           request_poll=types.KeyboardButtonPollType(type=types.PollType.QUIZ)))
    poll_keyboard.add(types.KeyboardButton(text='Отмена'))
    await CreateQuiz.waiting_for_question.set()
    await message.answer('Создайте вопрос, для этого используйте кнопку ниже.',
                         reply_markup=poll_keyboard)


@dp.message_handler(state=CreateQuiz.waiting_for_question, content_types=types.ContentTypes.POLL)
async def setup_question_for_quiz(message: types.Message):
    quiz = get_quiz()
    quiz.add_question(message.poll.question, message.poll.options, message.poll.correct_option_id)
    poll_keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    poll_keyboard.add(types.KeyboardButton(text='Создать еще вопрос',
                                           request_poll=types.KeyboardButtonPollType(type=types.PollType.QUIZ)))
    poll_keyboard.add(types.KeyboardButton(text='Cоздать новый раунд.'))
    poll_keyboard.add(types.KeyboardButton(text='Cохранить квиз.'))
    poll_keyboard.add(types.KeyboardButton(text='Отмена'))

    await message.reply(
        f'Имя игры: {quiz.quiz_name}\n'
        f'Текущий раунд: {get_current_round()}\n'
        f'Задержка между вопросами (сек.): {quiz.times_between_questions[get_current_round()]}\n'
        f'Количество вопросов: {len(quiz.rounds[get_current_round()])}\n',
        reply_markup=types.ReplyKeyboardRemove()
    )
    set_quiz(quiz)
    await message.reply(f'Был добавлен вопрос {message.poll.question}', reply_markup=poll_keyboard)


@dp.message_handler(Text(equals='Cоздать новый раунд.', ignore_case=True),
                    state=CreateQuiz.waiting_for_question)
async def new_round(message: types.Message):
    await CreateQuiz.waiting_for_round_name.set()
    await message.reply(
        'Пришлите название Вашего раунда (например, «История математики»).',
        reply_markup=types.ReplyKeyboardRemove()
    )


@dp.message_handler(Text(equals='Cохранить квиз.', ignore_case=True), state=CreateQuiz.waiting_for_question)
async def save_quiz(message: types.Message, state: FSMContext):
    quiz = get_quiz()
    quiz.save()
    await message.reply(
        f'Имя игры: {quiz.quiz_name}\n'
        f'Названия раундов: {list(quiz.rounds.keys())}\n'
        f'Задержка между вопросами (сек.): {list(quiz.times_between_questions.values())}\n'
        f'Количество раундов: {len(quiz.rounds.values())}\n',
        reply_markup=types.ReplyKeyboardRemove()
    )
    await state.finish()
    await message.answer(
        'Начните новый квиз или выберете из существующих.', reply_markup=menu_keyboard
    )
