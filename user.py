all_users = {}

class User():
    def __init__(self, name: str, score: int = 0):
        self.name = name
        self.score = score

    def add_score(self):
        self.score += 1

    @property
    def result(self) -> str:
        return f'Пользователь {self.name} набрал {self.score} очков.'