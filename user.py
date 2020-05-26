all_users = {}


def get_all_users():
    """
    Возвращает всех пользователей
    """
    global all_users
    return all_users


def set_all_users(value):
    """
    Устанавливает всех пользователей по значению value

    Parameters
    ----------
    value :
        Список пользователей
    """
    global all_users
    all_users = value


class User():
    def __init__(self, name: str, score: int = 0):
        """
        Класс пользователя

        Parameters
        ----------
        name : str
            Имя пользователя
        score : int, optional
            Количество очков пользователя, by default 0
        """
        self.name = name
        self.score = score

    def add_score(self):
        """
        Добавляет пользователю 1 балл за правильный ответ
        """
        self.score += 1

    @property
    def result(self) -> str:
        """
        Отправляет результат администратору после конца викторины
        """
        return f'Пользователь {self.name} набрал {self.score} очков.'