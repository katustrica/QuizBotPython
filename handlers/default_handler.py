from aiogram import types

from misc import dp


@dp.message_handler(content_types=types.ContentTypes.ANY, state='*')
async def all_other_messages(message: types.Message):
    """
    Обработчик только текстовых сообщений, если иначе, выбивает ошибку.

    Parameters
    ----------
    message : types.Message
        Текст сообщения
    """
    if message.content_type == 'text':
        await message.reply('Ничего не понимаю!')
    else:
        await message.reply('Этот бот принимает только текстовые сообщения!')
