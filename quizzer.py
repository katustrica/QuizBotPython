import pickle
import asyncio
import logging
from misc import quizes_path, bot, admin_id
from user import get_all_users, set_all_users
from typing import List, Dict
from collections import OrderedDict

quiz = None
current_round = None
current_question_correct_id = None


def get_quiz():
    """
    Возвращает квиз
    """
    global quiz
    return quiz


def set_quiz(value):
    """
    Устанавливает квиз в класс Quiz
    """
    global quiz
    quiz = value


def get_current_round():
    """
    Возвращает текущий раунд
    """
    global current_round
    return current_round


def set_current_round(value):
    """
    Устанавливает текущий раунд

    Parameters
    ----------
    value :
        Раунд
    """
    global current_round
    current_round = value


def get_current_question_correct_id():
    """
    Возвращает правильный ответ текущего вопроса.
    """
    global current_question_correct_id
    return current_question_correct_id


def set_current_question_correct_id(value):
    """
    Устанавливает правильный ответ для текущего вопроса
    """
    global current_question_correct_id
    current_question_correct_id = value


async def stop():
    """
    Оповещяает всех пользователей об остановке квиза.
    """
    users = get_all_users()
    for user_id in users:
        await bot.send_message(user_id, 'Квиз деактивирован')


class Quiz:
    def __init__(self, name):
        """
        Инициализует класс квиз.

        Parameters
        ----------
        name : str
            Название квиза
        """
        self.quiz_name: str = name
        self.rounds: OrderedDict[str, List[Question]] = OrderedDict()
        self.times_between_questions: Dict[str, int] = {}
        logging.info(f'Создана игра - {name}')

    def add_round(self, round_name):
        """
        Добавляет раунд к квизу

        Parameters
        ----------
        round_name : str
            Название раунда.
        """
        set_current_round(round_name)
        self.rounds[round_name] = []
        logging.info(f'Добавлен раунд - {round_name}')

    def set_time_between_quiestions(self, time):
        """
        Устанавливает время между вопросами

        Parameters
        ----------
        time : str
            Время между вопросами. Задается строго по кнопкам.
        """
        time_list = time.split()
        time_in_seconds = int(time_list[0]) if time_list[1] == 'сек.' else int(time_list[0])*60
        self.times_between_questions[current_round] = time_in_seconds  #Задает время между вопросоами в секундах.
        logging.info(f'Для раунда {current_round} задано время между вопросами - {time_in_seconds} секунд')


    def add_question(self, question_text, options, correct_option_id, media):
        """
        Добавляет вопрос в раунд.

        Parameters
        ----------
        question_text : str
            Вопрос викторины
        options :
            Варианты ответа.
        correct_option_id :
            Правильный вариант ответа.
        """
        self.rounds[current_round].append(
            Question(question_text=question_text,
                     options=[o.text for o in options],
                     correct_option_id=correct_option_id,
                     open_time=self.times_between_questions[current_round],
                     media=media))
        logging.info(f'Для раунда {current_round} добавлен новый вопрос - {question_text}')

    def save(self):
        """
        Сохраняет квиз в папку quizes_path
        """
        filepath = quizes_path / f'{self.quiz_name}.pickle'
        filepath.parent.mkdir(parents=True, exist_ok=True)
        logging.info(f'Сохранена игра - {self.quiz_name}.pickle')
        with open(filepath, 'wb') as f:
            pickle.dump(self, f)

    async def start_rounds(self):
        """
        Начинает отправлять вопросы пользователям. Старт викторины.
        """
        users = get_all_users()
        logging.info(f'Началась игра - {self.quiz_name}')
        for round_name, quiz_round in self.rounds.items():
            if not quiz:
                await stop()
                return
            logging.info(f'Начался раунд - {round_name}.')
            for user_id in users:
                await bot.send_message(
                    user_id,
                    f'Раунд - {round_name}.'
                    f'\n Задержка между вопросами {self.times_between_questions[round_name]} сек.'
                )
            for number, question in enumerate(quiz_round):
                if not quiz:
                    await stop()
                    return
                logging.info(f'Начался вопрос - {question.question_text}.')
                global current_question_correct_id
                current_question_correct_id = question.correct_option_id
                for user_id in users:
                    if question.media:
                        media = question.media
                        if media[0] == 'photo':
                            await bot.send_photo(user_id, media[1])
                        elif media[0] == 'video':
                            await bot.send_video(user_id, media[1])
                        elif media[0] == 'audio':
                            await bot.send_audio(user_id, media[1])
                    await bot.send_poll(chat_id=user_id,
                                        question=question.question_text,
                                        is_anonymous=False,
                                        options=question.options,
                                        type='quiz',
                                        correct_option_id=question.correct_option_id,
                                        open_period=question.open_time)
                await asyncio.sleep(self.times_between_questions[round_name])
                for user_id in users:
                    if number == len(self.rounds[round_name]):
                        await bot.send_message(user_id, f'Раунд {round_name} закончен')
            await asyncio.sleep(1)
        users_scores = {user.name: user.score for user in users.values()}
        users_scores_msg = '\n'.join([
            f'{s_user[0]} набрал {s_user[1]} очков.' for s_user
            in sorted(users_scores.items(), key=lambda us: (us[1], us[0]), reverse=True)]
        )
        for user_id in users:
            await bot.send_message(
                user_id, users_scores_msg
            )
        for id in admin_id:
            await bot.send_message(id, users_scores_msg)
        set_all_users({})
        set_quiz({})



class Question:
    type: str = 'question'

    def __init__(self, question_text, options, correct_option_id, open_time, media):
        self.question_text: str = question_text          # Текст вопроса
        self.options: List[str] = [*options]             # 'Распакованное' содержимое массива m_options в массив options
        self.correct_option_id: int = correct_option_id  # ID правильного ответа
        self.open_time: int = open_time                  # Время 'жизни' вопроса = времени между вопросами
        self.media: str = media

