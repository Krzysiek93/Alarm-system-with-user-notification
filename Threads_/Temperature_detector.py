import RPi.GPIO as GPIO
import time
import threading


class Temperature_detector():
    def __init__(self, que):
        self.que = que
        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(17, GPIO.OUT)  # 17 -> temperature sensor
        GPIO.output(17, 1)
        self.event = threading.Event()

    def measure(self):                      # this method shows temperature in console (should by in GUI)
        while not self.event.is_set():
            time.sleep(0.5)                 # it checks temperature every 0,5 sec.
            try:
                file = open('/sys/bus/w1/devices/28-051681f78fff/w1_slave', 'r')
            except FileNotFoundError:
                pass
            else:                           # processing text file to get value of temperature from it
                string = str(file.read())
                x = string.find('t=')
                scope = string[x+2: x+7: 1]
                temperature = (float(scope))/1000
                self.que.put(temperature)
                #print("%.2f" % temperature)
                file.close()

        GPIO.output(17, 0)



