from os import system, environ
from telegram import Bot


def send_picture_via_telegram_and_cleanup(bot, chat_id):
    bot.send_photo(chat_id, photo=open('/home/pi/Pictures/image.jpg', 'rb'))
    system("rm /home/pi/Pictures/image.jpg")


def send_gif_via_telegram_and_cleanup(bot, chat_id):
    bot.send_animation(chat_id, animation=open(
        '/home/pi/Pictures/gif/animation.gif', 'rb'))
    system("rm /home/pi/Pictures/gif/animation.gif")


if __name__ == "__main__":
    telegram_bot_id = environ['TELEGRAM_BOT_ID']
    telegram_chat_id = environ['TELEGRAM_CHAT_ID']
    bot = Bot(telegram_bot_id)
