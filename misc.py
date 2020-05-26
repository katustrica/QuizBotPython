import logging
from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from pathlib import Path


bot = Bot(token='1257852776:AAG-7JRrDxX-9A7MB6PdM4Z4OGNkoR5jWmE') #Ключ телеграм бота.
admin_id = [84203003, 241071293]  # Список админов.
quizes_path = Path('.') / 'quizes'
memory_storage = MemoryStorage()
dp = Dispatcher(bot, storage=memory_storage)
logging.basicConfig(level=logging.INFO)
