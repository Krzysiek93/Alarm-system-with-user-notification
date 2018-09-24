from pygame import mixer
from pygame import time


class Sounds:
    def __init__(self, command):
        self.command = command
        self.Generate_sound()
        self.Play_sound()


    def Generate_sound(self):
        mixer.init()
        #______________________________________________     mixer.music -> allows only one sound simultaneously
        if self.command == "welcom_sound":
            mixer.music.load('Welcome.mp3')
        elif self.command == "alarm_is_armed":
            mixer.music.load("Alarm_is_armed.mp3")
        elif self.command == "Leave":
            mixer.music.load("Leave.mp3")
        elif self.command == "logged":
            mixer.music.load("logged.mp3")
        elif self.command == "Initializing_system":
            mixer.music.load("Initializing_system.mp3")
        #_______________________________________________    mixer.Sound -> allows max 8 sounds simultaneously

        elif self.command == "alert":
            self.x = mixer.Sound("alert.wav")
        elif self.command == "passcode":
            self.x = mixer.Sound("passcode.wav")
        elif self.command == "Wrong_password":
            self.x = mixer.Sound("Wrong_password.wav")
        #_______________________________________________

    def Play_sound(self):

        if self.command != "alert" and self.command != 'Wrong_password' and self.command != "passcode" and self.command != "end_alert":
            mixer.music.play()
            while mixer.music.get_busy():    # returns True if the mixer is busy mixing any channels. If the mixer is idle then this return False
                time.Clock().tick(10)        # it wil compute how many mseconds have passed since the previous call

        elif self.command == "alert":

            self.play = self.x.play(-1)

            while self.play.get_busy():
                time.Clock().tick(10)

        elif self.command == 'Wrong_password' or self.command == "passcode":
            self.play = self.x.play()

            while self.play.get_busy():
                time.Clock().tick(10)

        elif self.command == "end_alert":
            try:
                mixer.stop()
            except:
                pass



