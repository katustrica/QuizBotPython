from misc import quizes_path, dp
from pickle import load
from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher.filters import Text
from quizzer import quiz

class ShowQuiz(StatesGroup):
    waiting_for_quiz_name = State()


@dp.message_handler(Text(equals="Готовые квизы", ignore_case=True), state='*')
async def show_quizes(message: types.Message):
    quizes = list(quizes_path.glob('*.pickle'))
    keyboard = types.ReplyKeyboardMarkup(
        [['Отмена']]
        + [[quiz.name.replace(quiz.suffix, '')] for quiz in quizes if quizes], resize_keyboard=True
    )
    await ShowQuiz.waiting_for_quiz_name.set()
    await message.answer('Какой квиз активировать?', reply_markup=keyboard)

@dp.message_handler(state=ShowQuiz.waiting_for_quiz_name)
async def show_quizes(message: types.Message, state: FSMContext):
    keyboard = types.ReplyKeyboardMarkup([
            ["Создать новый квиз"], ["Готовые квизы"]
        ], resize_keyboard=True)
    with open(quizes_path / f'{message.text}.pickle', 'rb') as f:
        global quiz
        quiz = load(f)
    await state.finish()
    await message.answer(f'Вы выбрали квиз - {message.text}',
                         reply_markup=keyboard)

def get_current_quiz():
    return quiz

