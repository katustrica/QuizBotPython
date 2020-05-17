import logging
from typing import List, Dict
from collections import OrderedDict
from pathlib import Path
import json
import io

quiz = None
current_round = None
quiz_path = Path.cwd() / 'quizs'


class Quiz:
    def __init__(self, quiz_name):
        self.quiz_name: str = quiz_name  #Имя игры.
        self.rounds: OrderedDict[str, List[Quiz]] = OrderedDict()
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
            Question(question_text=question_text, options=options, correct_option_id=correct_option_id)
        )

    def load_json(self, quiz_name) -> 'json':
        path = quiz_path / f'{quiz_name}.json'
        if not path.exists():
            raise FileExistsError(f'No such file: {path.name}')

        with io.open(path, encoding='utf-8') as f:
            attributes = json.load(f)
            return attributes

    @classmethod
    def from_json(cls, quiz_name):
        json_str = cls.load_json(quiz_name)
        quiz = cls.__new__(cls)
        quiz.quiz_name = quiz_name
        quiz.times_between_questions = json_str[0]['Время между вопросами']
        quiz.rounds = {}
        for rounds, questions in json_str[0].items():
            if isinstance(questions, dict):
                for question, answer in questions.items():
                    new_question = Question()
                    new_question.question_text = question
                    new_question.options = answer['answers']
                    new_question.correct_option_id = answer['correct_answer']
                    quiz.rounds.update({rounds: new_question})


class Question:
    type: str = 'question'

    def __init__(self, round_name, question_text, options, correct_option_id):
        self.round_name: str = round_name                # Название раунда
        self.question_text: str = question_text          # Текст вопроса
        self.options: List[str] = [*options]             # 'Распакованное' содержимое массива m_options в массив options
        self.correct_option_id: str = correct_option_id  # str правильного ответа
