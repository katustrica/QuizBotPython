from aiogram.types import (
    ContentTypes, Message, ReplyKeyboardRemove,
    PollType, ReplyKeyboardMarkup, KeyboardButton,
    KeyboardButtonPollType
)
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher.filters import Text

from misc import dp
from .menu import menu_keyboard
from quizzer import Quiz, set_quiz, get_quiz, get_current_round, set_current_round


media = ()


class CreateQuiz(StatesGroup):
    """
    Содержит в себе все состояния пользователя.
    """
    waiting_for_quiz_name = State()
    waiting_for_round_name = State()
    waiting_for_time_between_questions = State()
    waiting_for_question = State()


@dp.message_handler(Text(equals='Создать новый квиз', ignore_case=True), state='*')
async def create_new_quiz(message: Message):
    """
    Первое состояние пользователя. Создание квиза

    Parameters
    ----------
    message : types.Message
        Сообщение пользователя 'Создать новый квиз'
    """
    await message.reply('Вы решили создать новый Квиз.\n'
                        'Для начала, пожалуйста, пришлите название\n'
                        'Вашего теста (например, «Квиз на знание математики»).\n'
                        'Или отправьте /cancel для отмены.', reply_markup=ReplyKeyboardRemove())
    await CreateQuiz.waiting_for_quiz_name.set()


@dp.message_handler(state=CreateQuiz.waiting_for_quiz_name, content_types=ContentTypes.TEXT)
async def set_name_for_quiz(message: Message):
    """
    Принимает сообщение и ставит название квиза по этому сообщению.

    Parameters
    ----------
    message : types.Message
        Текст сообщения
    """
    set_quiz(Quiz(message.text))
    await CreateQuiz.waiting_for_round_name.set()
    await message.reply(
        'Пришлите название Вашего раунда (например, «История математики»).',
        reply_markup=ReplyKeyboardRemove()
    )


@dp.message_handler(state=CreateQuiz.waiting_for_round_name, content_types=ContentTypes.TEXT)
async def set_name_for_round(message: Message):
    """
    Ставит название раунда и предлагает выбрать время между вопросами

    Parameters
    ----------
    message : types.Message
        Текст сообщения
    """
    set_current_round(message.text)
    quiz = get_quiz()
    quiz.add_round(message.text)
    set_quiz(quiz)
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add('15 сек.', '30 сек.', '1 мин.', '5 мин.', '10 мин.', 'Отмена')
    await CreateQuiz.waiting_for_time_between_questions.set()
    await message.reply('Какой промежуток будет между вопросами?', reply_markup=keyboard)


@dp.message_handler(state=CreateQuiz.waiting_for_time_between_questions, content_types=ContentTypes.TEXT)
async def set_time_between_questions(message: Message):
    """
    Устанавливает время между сообщениями и предлагает создать следующий вопрос.

    Parameters
    ----------
    message : types.Message
        Текст сообщения
    """
    quiz = get_quiz()
    quiz.set_time_between_quiestions(message.text)
    set_quiz(quiz)
    poll_keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    poll_keyboard.add(KeyboardButton(text='Создать вопрос',
                                     request_poll=KeyboardButtonPollType(type=PollType.QUIZ)))
    poll_keyboard.add(KeyboardButton(text='Отмена'))
    await CreateQuiz.waiting_for_question.set()
    await message.answer('Создайте вопрос, для этого используйте кнопку ниже.',
                         reply_markup=poll_keyboard)


@dp.message_handler(state=CreateQuiz.waiting_for_question,
                    content_types=ContentTypes.AUDIO | ContentTypes.VIDEO | ContentTypes.PHOTO)
async def setup_media_for_quiestion(message: Message):
    """
    Устанавивает вопрос и предлагает:
    Закончить создание квиза,
    создание нового вопроса,
    сохранение квиза,
    сброс квиза

    Parameters
    ----------
    message : types.Message
        Текст сообщения
    """
    global media
    type = message.content_type
    if type == 'photo':
        media = ('photo', message.photo[-1].file_id)
    if type == 'video':
        media = ('video', message.video.file_id)
    if type == 'audio':
        media = ('audio', message.audio.file_id)
    await message.answer(f'Файл загружен. Тип - {type}')


@dp.message_handler(state=CreateQuiz.waiting_for_question, content_types=ContentTypes.POLL)
async def setup_question_for_quiz(message: Message):
    global media
    quiz = get_quiz()
    quiz.add_question(message.poll.question, message.poll.options, message.poll.correct_option_id, media)
    media = None
    poll_keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    poll_keyboard.add(KeyboardButton(text='Создать еще вопрос',
                                     request_poll=KeyboardButtonPollType(type=PollType.QUIZ)))
    poll_keyboard.add(KeyboardButton(text='Cоздать новый раунд.'))
    poll_keyboard.add(KeyboardButton(text='Cохранить квиз.'))
    poll_keyboard.add(KeyboardButton(text='Отмена'))

    await message.reply(
        f'Имя игры: {quiz.quiz_name}\n'
        f'Текущий раунд: {get_current_round()}\n'
        f'Задержка между вопросами (сек.): {quiz.times_between_questions[get_current_round()]}\n'
        f'Количество вопросов: {len(quiz.rounds[get_current_round()])}\n',
        reply_markup=ReplyKeyboardRemove()
    )
    set_quiz(quiz)
    await message.reply(f'Был добавлен вопрос {message.poll.question}', reply_markup=poll_keyboard)


@dp.message_handler(Text(equals='Cоздать новый раунд.', ignore_case=True),
                    state=CreateQuiz.waiting_for_question)
async def new_round(message: Message):
    """
    Создание нового раунда.

    Parameters
    ----------
    message : types.Message
        Текст сообщения
    """
    await CreateQuiz.waiting_for_round_name.set()
    await message.reply(
        'Пришлите название Вашего раунда (например, «История математики»).',
        reply_markup=ReplyKeyboardRemove()
    )


@dp.message_handler(Text(equals='Cохранить квиз.', ignore_case=True), state=CreateQuiz.waiting_for_question)
async def save_quiz(message: Message, state: FSMContext):
    """
    Сохранение квиза и его итог.

    Parameters
    ----------
    message : types.Message
        Текст сообщения
    state : FSMContext
        Сброс состояния
    """
    quiz = get_quiz()
    quiz.save()
    set_quiz(quiz)
    await message.reply(
        f'Имя игры: {quiz.quiz_name}\n'
        f'Названия раундов: {list(quiz.rounds.keys())}\n'
        f'Задержка между вопросами (сек.): {list(quiz.times_between_questions.values())}\n'
        f'Количество раундов: {len(quiz.rounds.values())}\n',
        reply_markup=ReplyKeyboardRemove()
    )
    await state.finish()
    await message.answer(
        'Начните новый квиз или выберете из существующих.', reply_markup=menu_keyboard
    )
