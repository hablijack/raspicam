import RPi.GPIO as GPIO
from picamera import PiCamera, Color
import time

SHUTTER_BTN_GPIO = 27
SETTING_NEXT_BTN_GPIO = 23
SETTING_PREV_BTN_GPIO = 25

MODE_NEXT_BTN_GPIO = 22
MODE_PREV_BTN_GPIO = 24

current_cam_fx_index = 0
current_cam_mode = 0

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

def load_fx_mode(n):
    global current_cam_fx_index
    current_cam_fx_index = (current_cam_fx_index + n) % len(FX_LIST)
    fx = FX_LIST[current_cam_fx_index]
    return fx

def generate_overlay_text(effect):
    overlay_text = None
    if effect == 'none':
        overlay_text = ' 4k '
    else:
        overlay_text = ' ' + effect + ' '
    return overlay_text

if __name__ == "__main__":
    initializeGPIOs()
    with PiCamera() as camera:
        camera.led = False
        camera.resolution = (3840, 2160)
        camera.framerate = 30
        camera.annotate_text_size = 120
        camera.annotate_foreground = Color('black')
        camera.annotate_background = Color('white')
        camera.annotate_text = generate_overlay_text(load_fx_mode(0))
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
            elif shutter_btn_state == False:
                camera.annotate_text = None
                camera.capture('/home/pi/Pictures/%03d.jpg' % int(time.time_ns()))
                camera.annotate_text = generate_overlay_text(load_fx_mode(0))
                time.sleep(0.2)
