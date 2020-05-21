import io
import json
import pickle
import logging
from misc import quizes_path
from typing import List, Dict
from collections import OrderedDict
<<<<<<< HEAD
from pathlib import Path
import json
import io
import jsonpickle
=======

>>>>>>> 6aba5d2780313f0eb1b1cda8bd993a90f405b4da

quiz = None
current_round = None

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
                     options=options,
                     correct_option_id=correct_option_id,
                     open_time=times_between_questions[current_round]))
        logging.info(f'Для раунда {current_round} добавлен новый вопрос - {question_text}')

    def save(self):
        filepath = quizes_path / f'{self.quiz_name}.pickle'
        filepath.parent.mkdir(parents=True, exist_ok=True)
        with open(filepath, 'wb') as f:
            pickle.dump(self, f)

class Question:
    type: str = 'question'

    def __init__(self, question_text, options, correct_option_id, open_time):
        self.question_text: str = question_text          # Текст вопроса
        self.options: List[str] = [*options]             # 'Распакованное' содержимое массива m_options в массив options
        self.correct_option_id: int = correct_option_id
        self.open_time: int = open_time  # int правильного ответа
