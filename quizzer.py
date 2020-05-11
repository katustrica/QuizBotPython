from typing import List, Dict
from collections import OrderedDict

quiz = None
current_round = None

class Quiz:
    def __init__(self, quiz_name):
        self.quiz_name: str = quiz_name #Имя игры.
        self.rounds: OrderedDict[List[Quiz]] = OrderedDict()

    def add_round(self, round_name)
        self.rounds[round_name] = []

    def add_question(self, question_text, )
        self.rounds[current_round].append(
            Quiz(quiz_id=message.poll.id,
                 question=message.poll.question,
                 options=[o.text for o in message.poll.options],
                 correct_option_id=message.poll.correct_option_id,
                 owner_id=message.from_user.id)
            )
        )


    # Сохраняем себе викторину в память
    quizzes_database[str(message.from_user.id)].append(Quiz(
        quiz_id=message.poll.id,
        question=message.poll.question,
        options=[o.text for o in message.poll.options],
        correct_option_id=message.poll.correct_option_id,
        owner_id=message.from_user.id)
    )

class Question:
    type: str = "quiz"

    def __init__(self, quiz_id, question_text, options, correct_option_id, owner_id):
        # Используем подсказки типов, чтобы было проще ориентироваться.
        self.quiz_id: str = quiz_id                      # ID викторины. Изменится после отправки от имени бота
        self.question_text: str = question_text          # Текст вопроса
        self.options: List[str] = [*options]             # "Распакованное" содержимое массива m_options в массив options
        self.correct_option_id: int = correct_option_id  # ID правильного ответа
        self.owner: int = owner_id                       # Владелец опроса
        self.winners: List[int] = []                     # Список победителей
        self.chat_id: int = 0                            # Чат, в котором опубликована викторина
        self.message_id: int = 0                         # Сообщение с викториной (для закрытия)
