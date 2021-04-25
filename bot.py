import os

from telegram import Bot
from telegram.ext import Filters, MessageHandler, Updater


def get_bot_info(token):
    bot = Bot(token=token)

    bot_info = bot.get_me()

    return {
        'bot_id': bot_info['id'], 
        'name': bot_info['first_name'], 
        'username': bot_info['username']
    }


def mirror_message(updater, context):
    updater.message.reply_text(updater.message.text)


def start_bot(token):
    updater = Updater(token=token, use_context=True)

    updater.dispatcher.add_handler(MessageHandler(Filters.text, mirror_message))

    updater.start_polling()

    return updater
    