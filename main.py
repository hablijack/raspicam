import RPi.GPIO as GPIO
from picamera import PiCamera, Color
import time

SHUTTER_BTN_GPIO = 27
SETTING_NEXT_BTN_GPIO = 23
SETTING_PREV_BTN_GPIO = 25

current_cam_fx_index = 0

FX_LIST = ['none', 'sketch', 'gpen', 'pastel', 'watercolor', 'oilpaint', 'hatch',
           'negative', 'colorswap', 'posterise', 'denoise', 'blur', 'film',
           'washedout', 'emboss', 'cartoon', 'solarize']


def initializeGPIOs():
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(SHUTTER_BTN_GPIO, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(SETTING_NEXT_BTN_GPIO, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(SETTING_PREV_BTN_GPIO, GPIO.IN, pull_up_down=GPIO.PUD_UP)


def load_fx_mode(n):
    global current_cam_fx_index
    current_cam_fx_index = (current_cam_fx_index + n) % len(FX_LIST)
    fx = FX_LIST[current_cam_fx_index]
    return fx


if __name__ == "__main__":
    initializeGPIOs()
    with PiCamera() as camera:
        camera.led = False
        camera.resolution = (1920, 1080)
        camera.framerate = 30
        frame = int(time.time())
        camera.annotate_background = Color('black')
        camera.annotate_text = load_fx_mode(0)
        camera.start_preview()
        while True:
            shutter_btn_state = GPIO.input(SHUTTER_BTN_GPIO)
            setting_next_btn_state = GPIO.input(SETTING_NEXT_BTN_GPIO)
            setting_prev_btn_state = GPIO.input(SETTING_PREV_BTN_GPIO)
            if setting_next_btn_state == False:
                fx = load_fx_mode(1)
                camera.image_effect = fx
                camera.annotate_text = fx
            elif setting_prev_btn_state == False:
                fx = load_fx_mode(-1)
                camera.image_effect = fx
                camera.annotate_text = fx
            elif shutter_btn_state == False:
                camera.capture('/home/pi/Pictures/%03d.jpg' % frame)
                frame += 1
            time.sleep(0.2)
