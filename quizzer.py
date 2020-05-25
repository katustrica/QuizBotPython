import pickle
import asyncio
import logging
from aiogram.types import Message
from misc import quizes_path, bot, admin_id
from user import get_all_users, set_all_users
from typing import List, Dict
from collections import OrderedDict

quiz = None
current_round = None
current_question_correct_id = None


def get_quiz():
    global quiz
    return quiz


def set_quiz(value):
    global quiz
    quiz = value


def get_current_round():
    global current_round
    return current_round


def set_current_round(value):
    global current_round
    current_round = value


def get_current_question_correct_id():
    global current_question_correct_id
    return current_question_correct_id


def set_current_question_correct_id(value):
    global current_question_correct_id
    current_question_correct_id = value


async def stop(self):
    users = get_all_users()
    for user_id in users:
        await bot.send_message(user_id, 'Квиз деактивирован')


class Quiz:
    def __init__(self, name):
        self.quiz_name: str = name  #Имя игры.
        self.rounds: OrderedDict[str, List[Question]] = OrderedDict()
        self.times_between_questions: Dict[str, int] = {}
        logging.info(f'Создана игра - {name}')

    def add_round(self, round_name):
        set_current_round(round_name)
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

    async def start_rounds(self):
        users = get_all_users()
        for user_id in users:
            for round_name, quiz_round in self.rounds.items():
                if not quiz:
                    await stop()
                    return
                await bot.send_message(
                    user_id,
                    f'Раунд - {round_name}.'
                    f'\n Задержка между вопросами {self.times_between_questions[round_name]} сек.'
                )
                for number, question in enumerate(quiz_round):
                    if not quiz:
                        await stop()
                        return
                    global current_question_correct_id
                    current_question_correct_id = question.correct_option_id
                    await bot.send_poll(chat_id=user_id,
                                        question=question.question_text,
                                        is_anonymous=False,
                                        options=question.options,
                                        type='quiz',
                                        correct_option_id=question.correct_option_id,
                                        open_period=question.open_time)
                    await asyncio.sleep(self.times_between_questions[round_name])
                    if number == len(self.rounds[round_name]):
                        await bot.send_message(user_id, f'Раунд {round_name} закончен')
                await asyncio.sleep(5)
            await bot.send_message(
                user_id, f'Поздравляю!!! Квиз окончен, вы набрали {users[user_id].score} очков.'
            )
        results = '\n'.join([user.result for user in users.values()])
        set_all_users(None)
        set_quiz(None)
        for id in admin_id:
            await bot.send_message(id, results)


class Question:
    type: str = 'question'

    def __init__(self, question_text, options, correct_option_id, open_time):
        self.question_text: str = question_text          # Текст вопроса
        self.options: List[str] = [*options]             # 'Распакованное' содержимое массива m_options в массив options
        self.correct_option_id: int = correct_option_id  # ID правильного ответа
        self.open_time: int = open_time                  # Время открытия (?)

