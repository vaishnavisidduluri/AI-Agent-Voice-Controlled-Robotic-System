import time
import RPi.GPIO as GPIO

class UltrasonicSensor:
    def __init__(self, trig=23, echo=24):
        self.trig = trig
        self.echo = echo

        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.trig, GPIO.OUT)
        GPIO.setup(self.echo, GPIO.IN)

    def get_distance(self):
        GPIO.output(self.trig, True)
        time.sleep(0.00001)
        GPIO.output(self.trig, False)

        while GPIO.input(self.echo) == 0:
            start = time.time()

        while GPIO.input(self.echo) == 1:
            end = time.time()

        distance = (end - start) * 17150
        return round(distance, 2)