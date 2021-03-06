from misc import quizes_path, dp
from pickle import load
from quizzer import set_quiz, get_quiz
from aiogram.types import ReplyKeyboardMarkup, Message
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher.filters import Text
import logging


class ShowQuiz(StatesGroup):
    waiting_for_quiz_name = State()


class ControllQuiz(StatesGroup):
    waiting_for_action = State()
    waiting_for_delete_confirmation = State()


menu_keyboard = ReplyKeyboardMarkup(
    [['Создать новый квиз'], ['Готовые квизы'], ['Управление квизом']], resize_keyboard=True
)

control_quiz_keyboard = ReplyKeyboardMarkup(
    [['Деактивировать'], ['Удалить'], ['Отмена']], resize_keyboard=True
)


@dp.message_handler(Text(equals='Готовые квизы', ignore_case=True), state='*')
async def show_quizes(message: Message):
    """
    Показывает все сохраненные квизы.

    Parameters
    ----------
    message : Message
        Текст сообщения
    """
    quizes = list(quizes_path.glob('*.pickle'))
    keyboard = ReplyKeyboardMarkup(
        [['Отмена']]
        + [[quiz.name.replace(quiz.suffix, '')] for quiz in quizes if quizes], resize_keyboard=True
    )
    logging.info(f'Админ {message.from_user.full_name} смотрит готовые тесты.')
    await ShowQuiz.waiting_for_quiz_name.set()
    await message.answer('Какой квиз активировать?', reply_markup=keyboard)


@dp.message_handler(state=ShowQuiz.waiting_for_quiz_name)
async def set_quiz_menu(message: Message, state: FSMContext):
    """
    Показывает пользователю меню.

    Parameters
    ----------
    message : Message
        Текст сообщения
    state : FSMContext
        Сброс состояния пользователя.
    """
    if message.text == 'Отмена':
        await state.finish()
        await message.answer(f'Хотите создать или активировать квиз?', reply_markup=menu_keyboard)
    else:
        with open(quizes_path / f'{message.text}.pickle', 'rb') as f:
            set_quiz(load(f))
        logging.info(f'Админ {message.from_user.full_name} стартанул квиз {message.text}')
        await state.finish()
        await message.answer(f'Вы выбрали квиз - {message.text}, он начинается!!!',
                             reply_markup=menu_keyboard)
        await get_quiz().start_rounds()


@dp.message_handler(Text(equals='Управление квизом', ignore_case=True), state='*')
async def select_quiz_actions(message: Message):
    """
    Меню взаимодействия с квизом.

    Parameters
    ----------
    message : Message
        Текст сообщения
    """
    quiz = get_quiz()
    if quiz:
        await ControllQuiz.waiting_for_action.set()
        await message.answer(
            f'Выбран квиз - {quiz.quiz_name}\n. Что вы хотите с ним сделать?',
            reply_markup=control_quiz_keyboard
        )
    else:
        await message.answer('Квиз не выбран.')


@dp.message_handler(Text(equals=['Деактивировать', 'Удалить'], ignore_case=True),
                    state=ControllQuiz.waiting_for_action)
async def quiz_action(message: Message, state: FSMContext):
    """
    Обрабатывает команды Деактивировать и Удалить

    Parameters
    ----------
    message : Message
        Текст сообщения. Деактивировать\Удалить
    state : FSMContext
        Сброс состояния пользователя
    """
    quiz = get_quiz()
    if message.text == 'Деактивировать':
        await message.answer(f'Квиз {quiz.quiz_name} деактивирован.', reply_markup=menu_keyboard)
        await state.finish()
        logging.info(f'Админ {message.from_user.full_name} деактивировал квиз.')
        set_quiz(None)
    elif message.text == 'Удалить':
        await ControllQuiz.waiting_for_delete_confirmation.set()
        keyboard = ReplyKeyboardMarkup([['Да'], ['Нет']], resize_keyboard=True)
        await message.answer(f'Вы точно хотите удалить квиз - {quiz.quiz_name}?', reply_markup=keyboard)
        logging.info(f'Админ {message.from_user.full_name} удаляет квиз.')


@dp.message_handler(Text(equals=['Да', 'Нет'], ignore_case=True),
                    state=ControllQuiz.waiting_for_delete_confirmation)
async def delete_quiz_confirmation(message: Message, state: FSMContext):
    """
    Подтверждение удаления пользователя

    Parameters
    ----------
    message : Message
        Текст сообщения. Да\Нет
    state : FSMContext
        Сброс состояний пользователя.
    """
    quiz = get_quiz()
    if message.text == 'Да':
        file_to_rem = quizes_path / f'{quiz.quiz_name}.pickle'
        file_to_rem.unlink()
        await state.finish()
        await message.answer(f'Вы удалили квиз - {quiz.quiz_name}',
                             reply_markup=menu_keyboard)
        set_quiz(None)
        logging.info(f'Админ {message.from_user.full_name} удалил квиз.')
    elif message.text == 'Нет':
        await ControllQuiz.waiting_for_action.set()
        await message.answer(
            f'Выбран квиз - {quiz.quiz_name}\n. Что вы хотите с ним сделать?',
            reply_markup=control_quiz_keyboard
        )
        logging.info(f'Админ {message.from_user.full_name} отменил удаление квиза.')
