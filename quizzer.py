import io
import json
import pickle
import asyncio
import logging
from aiogram.types import Message
from misc import quizes_path, bot, admin_id
from user import User, all_users
from typing import List, Dict
from collections import OrderedDict
from handlers.new_quiz import current_quiz

quiz = None
current_round = None
current_question_correct_id = None

class Quiz:
    def __init__(self, quiz_name):
        self.quiz_name: str = quiz_name  #Имя игры.
        self.rounds: OrderedDict[str, List[Question]] = OrderedDict()
        self.times_between_questions: Dict[str, int] = {}
        logging.info(f'Создана игра - {quiz_name}')

    def add_round(self, round_name):
        global current_round
        current_round = round_name
        self.rounds[round_name] = []
        logging.info(f'Добавлен раунд - {round_name}')

    def set_time_between_quiestions(self, time):
        time_list = time.split()
        time_in_seconds = int(time_list[0]) if time_list[1] == 'сек.' else int(time_list[0])*60
        self.times_between_questions[current_round] = time_in_seconds  #Задает время между вопросоами в секундах.
        logging.info(f'Для раунда {current_round} задано время между вопросами - {time_in_seconds} секунд')

    def add_question(self, question_text, options, correct_option_id):
        self.rounds[current_round].append(
            Question(question_text=question_text,
                     options=[o.text for o in options],
                     correct_option_id=correct_option_id,
                     open_time=self.times_between_questions[current_round]))
        logging.info(f'Для раунда {current_round} добавлен новый вопрос - {question_text}')

    def save(self):
        filepath = quizes_path / f'{self.quiz_name}.pickle'
        filepath.parent.mkdir(parents=True, exist_ok=True)
        with open(filepath, 'wb') as f:
            pickle.dump(self, f)

    async def start_rounds(self, message: Message):
        for round_name, quiz_round in self.rounds.items():
            await message.answer(
                f'Раунд - {round_name}.'
                f'\n Задержка между вопросами {self.times_between_questions[round_name]} сек.'
            )
            for number, question in enumerate(quiz_round):
                global current_question_correct_id
                current_question_correct_id = question.correct_option_id
                await bot.send_poll(chat_id=message.chat.id, question=question.question_text,
                                    is_anonymous=False, options=question.options, type='quiz',
                                    correct_option_id=question.correct_option_id, open_period=question.open_time)
                await asyncio.sleep(self.times_between_questions[round_name])
                if number == len(self.rounds[round_name]):
                    await message.answer(f'Раунд {round_name} закончен')
            await asyncio.sleep(5)
        await message.answer(f'Поздравляю!!! Квиз окончен, вы набрали {all_users[message.from_user.id].score} очков.')

        results = '\n'.join([user.result for user in all_users.values()])
        for id in admin_id:
            await bot.send_message(id, results)


class Question:
    type: str = 'question'

    def __init__(self, question_text, options, correct_option_id, open_time):
        self.question_text: str = question_text          # Текст вопроса
        self.options: List[str] = [*options]             # 'Распакованное' содержимое массива m_options в массив options
        self.correct_option_id: int = correct_option_id  # ID правильного ответа
        self.open_time: int = open_time                  # Время открытия (?)


async def start_quiz_for_user(message: Message):
    quiz_game = current_quiz
    import pdb; pdb.set_trace()
    if isinstance(quiz_game, Quiz):
        await message.answer(f'Начался квиз - {quiz_game.quiz_name}')
        all_users[message.from_user.id] = User(message.from_user.full_name)
        quiz_game.start_rounds(message)
    else:
        await message.answer(f'Квиз не загружен.')
