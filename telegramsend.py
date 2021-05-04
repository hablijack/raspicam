from os import system, environ
from telegram import Bot
import os


def send_picture_via_telegram_and_cleanup(bot, chat_id, filename):
    bot.send_photo(chat_id, photo=open(
        '/home/pi/Pictures/' + filename + '.jpg', 'rb'))
    system("rm /home/pi/Pictures/" + filename + ".jpg")


def send_gif_via_telegram_and_cleanup(bot, chat_id, filename):
    bot.send_animation(chat_id, animation=open(
        '/home/pi/Pictures/gif/' + filename + '.gif', 'rb'))
    system('rm /home/pi/Pictures/gif/' + filename + '.gif')


if __name__ == "__main__":
    telegram_bot_id = environ['TELEGRAM_BOT_ID']
    telegram_chat_id = environ['TELEGRAM_CHAT_ID']

    bot = Bot(telegram_bot_id)
    directory = os.fsencode('/home/pi/Pictures')
    for file in os.listdir(directory):
        filename = os.fsdecode(file)
        if filename.endswith(".jpg"):
            send_picture_via_telegram_and_cleanup(
                bot, telegram_chat_id, filename)
        elif filename.endswith(".gif"):
            send_gif_via_telegram_and_cleanup(bot, telegram_chat_id, filename)
        else:
            continue
