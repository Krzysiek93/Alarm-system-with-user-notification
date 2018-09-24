import RPi.GPIO as GPIO
import threading

import sys
sys.path.append('/home/pi/PycharmProjects/Alarm')
from Threads_ import Sounds
import datetime
import Creating_threads

import picamera
from time import sleep, gmtime, strftime


from multiprocessing import Queue


PIR_state = "Alarm is not active" # it is easier to create one common global variable, which controls pir state because it is not possible to run
                                  # more than one PIR_detector object at the same time


class PIR_detector(object):

    def __init__(self, q, timee):                               #setting pins in right mode
        self.event = threading.Event()
        self.q = q
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        self.time_to_run = timee

        pins = [16, 24, 12, 23, 18]                   #16,24 -> red leds, 12,23 -> green leds (out)
        for i in pins:
            GPIO.setup(i, GPIO.OUT)
        GPIO.setup(21, GPIO.IN)                       #signal from PIR (in)
        global PIR_state
        PIR_state = "Alarm is not active"


    def Start_alarm(self):                            #this method turns on and turns off leds when movement is detected
                                                      # 16,24 -> red leds, 12,23 -> green leds (out)
        GPIO.output(23, 1)
        GPIO.output(24, 1)

        proj = True

        while not self.event.is_set():

            if GPIO.input(21) == 0:
                GPIO.output(12, 0)
                GPIO.output(16, 0)
                sleep(0.1)
            elif GPIO.input(21) == 1 and proj:    # time of '1' Pir state is 5.8sek


                event_time = str(datetime.datetime.today())
                event_time = event_time[0:19]


                self.queue1 = Queue()
                takingPhoto = Creating_threads.Creating_threads.Photo_thread(self.queue1)
                takingPhoto.start()


                salert_sound = Creating_threads.Creating_threads.Sound_thread("alert")
                salert_sound.start()

                try:
                    SMS = Creating_threads.Creating_threads.SMS()
                    SMS.start()
                    pass
                except:
                    pass

                try:
                    takingPhoto.join()                          # wait for picture
                    path_to_photo = self.queue1.get()
                    Mail = Creating_threads.Creating_threads.Email(path_to_photo, event_time)
                    Mail.start()
                except:
                    pass

                for i in range(0,7):           # 3sec loop
                    sleep(0.25)
                    GPIO.output(12, 1)
                    GPIO.output(16, 1)
                    sleep(0.25)
                    GPIO.output(12, 0)
                    GPIO.output(16, 0)
                # 3sec loop + 1.3sec sleep = 4.3sek
                proj = False



        global PIR_state
        PIR_state = "Alarm is not active"
        Turn_off_pins()


    def Set_Data(self):                # informations from user. It should be in GUI
        GPIO.output(18, 1)
        global PIR_state
        PIR_state = "Alarm is set but not active yet"
        init_sound = Creating_threads.Creating_threads.Sound_thread("Initializing_system")
        init_sound.start()
        if self.Countdown(self.time_to_run):
            Start_sound = Creating_threads.Creating_threads.Sound_thread("alarm_is_armed")
            Start_sound.start()
            PIR_state = "Alarm is active"
            self.Start_alarm()


    def Countdown(self, time_to_run):           # just counting down to zero, "if not self.event.is_set()" controls state of thread
        for i in range(time_to_run, -1, -1):    # it should be in GUI
            if not self.event.is_set():
                self.q.put(i)
                #print('{} '.format(i), end='\n', flush=True)
                if i == 10:
                    Leave_sound = Creating_threads.Creating_threads.Sound_thread("Leave")
                    Leave_sound.start()
                sleep(1)
            else:
                return False
        return True


    def Info_to_file(self):
        time = str(datetime.datetime.today())
        time = time[0:19]
        with open('/home/pi/PycharmProjects/Alarm/Data.txt', 'a') as file:  # the "with" will automatically close the file after nested block
            file.write("Move detected " + time + "\n")                      # and it guaranteed to close the file no matter hot the nested block ex
        return time

    def photo(self):
        showtime = str(strftime('%Y-%m-%d %H:%M:%S', gmtime()))
        print(showtime)
        camera = picamera.PiCamera()
        camera.start_preview()
        camera.hflip = True
        camera.vflip = True
        camera.brightness = 60
        sleep(0.5)
        camera.capture(showtime + '.jpg')


def Get_state_PIR():
    return(PIR_state)


def Turn_off_pins():
    pins = [16, 24, 12, 23, 18]
    for i in pins:
        GPIO.output(i, 0)

