import RPi.GPIO as GPIO
from picamera import PiCamera
import time

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.setup(27, GPIO.IN, pull_up_down=GPIO.PUD_UP)

with PiCamera() as camera:
  camera.led = False
  camera.resolution = (1920, 1080)
  camera.framerate = 30
  frame = int(time.time())
  camera.start_preview()
  while True:
    input_state = GPIO.input(27)
    if input_state == False:
      camera.capture('/home/pi/Pictures/%03d.jpg' % frame)
      frame += 1
