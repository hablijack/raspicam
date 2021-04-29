import RPi.GPIO as GPIO
from picamera import PiCamera, Color
import time
from os import system, environ
from telegram import Bot

SHUTTER_BTN_GPIO = 27
SETTING_NEXT_BTN_GPIO = 23
SETTING_PREV_BTN_GPIO = 25

MODE_NEXT_BTN_GPIO = 22
MODE_PREV_BTN_GPIO = 24

current_cam_fx_index = 0
current_cam_mode_index = 0

FX_LIST = ['none', 'sketch', 'gpen', 'pastel', 'watercolor', 'oilpaint', 'hatch',
           'negative', 'colorswap', 'posterise', 'washedout', 'emboss', 'cartoon', 'solarize']
CAM_MODE_LIST = ['PIC', 'GIF']


def initializeGPIOs():
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(SHUTTER_BTN_GPIO, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(SETTING_NEXT_BTN_GPIO, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(SETTING_PREV_BTN_GPIO, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(MODE_NEXT_BTN_GPIO, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(MODE_PREV_BTN_GPIO, GPIO.IN, pull_up_down=GPIO.PUD_UP)

def load_cam_mode(n):
    global current_cam_mode_index
    current_cam_mode_index = (current_cam_mode_index + n) % len(CAM_MODE_LIST)
    return CAM_MODE_LIST[current_cam_mode_index]

def load_fx_mode(n):
    global current_cam_fx_index
    current_cam_fx_index = (current_cam_fx_index + n) % len(FX_LIST)
    return FX_LIST[current_cam_fx_index]

def set_cam_to_gif_mode():
    camera.annotate_foreground = Color('white')
    camera.annotate_background = Color('black')
    camera.annotate_text_size = 25
    camera.resolution = (512, 288)
    camera.framerate = 30

def set_cam_to_pic_mode():
    camera.annotate_foreground = Color('black')
    camera.annotate_background = Color('white')
    camera.annotate_text_size = 120
    camera.resolution = (3840, 2160)
    camera.framerate = 30

def generate_overlay_text(effect):
    overlay_text = None
    if effect == 'none':
        overlay_text = ' 4k '
    else:
        overlay_text = ' ' + effect + ' '
    return overlay_text

def generate_gif_and_cleanup():
    graphicsmagick_cmd = "gm convert -delay 15 /home/pi/Pictures/gif/*.jpg /home/pi/Pictures/gif/animation.gif"
    system(graphicsmagick_cmd)
    system("rm /home/pi/Pictures/gif/*.jpg")

def send_picture_via_telegram_and_cleanup(bot, chat_id):
    bot.send_photo(chat_id, photo=open('/home/pi/Pictures/image.jpg', 'rb'))
    system("rm /home/pi/Pictures/image.jpg")

def send_gif_via_telegram_and_cleanup(bot, chat_id):
    bot.send_animation(chat_id, animation=open('/home/pi/Pictures/gif/animation.gif', 'rb'))
    system("rm /home/pi/Pictures/gif/animation.gif")

if __name__ == "__main__":
    telegram_bot_id = environ['TELEGRAM_BOT_ID']
    telegram_chat_id = environ['TELEGRAM_CHAT_ID']
    bot = Bot(telegram_bot_id)
    initializeGPIOs()
    with PiCamera() as camera:
        camera.led = False
        camera.resolution = (3840, 2160)
        camera.framerate = 30
        fx = load_fx_mode(0)
        camera.annotate_text = generate_overlay_text(fx)
        mode = load_cam_mode(0)
        if mode == 'GIF':
            set_cam_to_gif_mode()
        elif mode == 'PIC':
            set_cam_to_pic_mode()
        camera.start_preview()
        while True:
            shutter_btn_state = GPIO.input(SHUTTER_BTN_GPIO)
            setting_next_btn_state = GPIO.input(SETTING_NEXT_BTN_GPIO)
            setting_prev_btn_state = GPIO.input(SETTING_PREV_BTN_GPIO)
            mode_next_btn_state = GPIO.input(MODE_NEXT_BTN_GPIO)
            mode_prev_btn_state = GPIO.input(MODE_PREV_BTN_GPIO)
            if setting_next_btn_state == False:
                fx = load_fx_mode(1)
                camera.image_effect = fx
                camera.annotate_text = generate_overlay_text(fx)
                time.sleep(0.2)
            elif setting_prev_btn_state == False:
                fx = load_fx_mode(-1)
                camera.image_effect = fx
                camera.annotate_text = generate_overlay_text(fx)
                time.sleep(0.2)
            elif mode_next_btn_state == False:
                mode = load_cam_mode(1)
                if mode == 'GIF':
                    set_cam_to_gif_mode()
                elif mode == 'PIC':
                    set_cam_to_pic_mode()
                time.sleep(0.2)
            elif mode_prev_btn_state == False:
                mode = load_cam_mode(-1)
                if mode == 'GIF':
                    set_cam_to_gif_mode()
                elif mode == 'PIC':
                    set_cam_to_pic_mode()
                time.sleep(0.2)
            elif shutter_btn_state == False:
                camera.annotate_text = None
                if mode == 'PIC':
                    camera.capture('/home/pi/Pictures/image.jpg')
                    camera.annotate_text = generate_overlay_text(load_fx_mode(0))
                    send_picture_via_telegram_and_cleanup(bot, telegram_chat_id)
                    time.sleep(0.2)
                elif mode == 'GIF':
                    for filename in camera.capture_continuous('/home/pi/Pictures/gif/{counter:03d}.jpg', burst=True):
                        shutter_btn_state = GPIO.input(SHUTTER_BTN_GPIO)
                        if shutter_btn_state == True:
                            break
                    generate_gif_and_cleanup()
                    send_gif_via_telegram_and_cleanup(bot, telegram_chat_id)
                    time.sleep(0.2)
                camera.annotate_text = generate_overlay_text(load_fx_mode(0))
