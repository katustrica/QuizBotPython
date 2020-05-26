#!venv/bin/python
from aiogram import executor

from misc import dp
import handlers  #не удалять!

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
