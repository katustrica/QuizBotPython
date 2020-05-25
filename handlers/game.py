from misc import dp
from user import get_all_users, set_all_users
from aiogram.types import PollAnswer
from quizzer import get_current_question_correct_id

@dp.poll_answer_handler()
async def handle_poll_answer(quiz_answer: PollAnswer):
    if get_current_question_correct_id() == quiz_answer.option_ids[0]:
        all_users = get_all_users()
        all_users[quiz_answer.user.id].add_score()
        set_all_users(all_users)
