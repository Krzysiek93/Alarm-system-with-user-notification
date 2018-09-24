import threading
import socket

import sys
sys.path.append('/home/pi/PycharmProjects/Alarm')
from Threads_ import PIR_detector
from Threads_ import Temperature_detector
from Threads_ import Sounds
from Threads_ import Camera
#from Serwer import serwerFTP
from twilio.rest import Client

from multiprocessing import Queue



import os
import smtplib
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart




#_______________________________________________________________________________________________________________________
# PIR_thread class is responsible for creating threads, which are linked with PIR detector
# and it is determined by "operation" variable

list_of_PIRth = []  # list of pir threads. Only one thread!

class PIR_thread(threading.Thread):

    def __init__(self, operation, Qu, timee):
        self.Q = Qu
        self.operation = operation
        threading.Thread.__init__(self)

        if self.operation == "Creating_PIR_thread":  # if a new thread is created,
            try:
                global list_of_PIRth

                for x in list_of_PIRth:
                    x.end()
                    list_of_PIRth=[]
                list_of_PIRth.append(self)
            except:
                pass

         #  self.end()                               # end previous thread (if it exists) and call PIR_detector constructor
            self.PIR = PIR_detector.PIR_detector(self.Q, timee)


    def run(self):

        if self.operation == "Creating_PIR_thread":  # call proper method using self.PIR object
            self.PIR.Set_Data()

        elif self.operation=="Creating_check_PIR_thread": # the same, but get state of PIR
            state = PIR_detector.Get_state_PIR()
            if state == "Alarm is not active":
                alarm_not_act_sound = Sound_thread("Alarm is not active")
                alarm_not_act_sound.start()
            elif state == "Alarm is active":
                alarm_act_sound = Sound_thread("Alarm is active")
                alarm_act_sound.start()
            else:
                pass


    def end(self):                                         # if thread exists then kill it, otherwise do nothing
        try:
            #print("niszcze watek pir")
            self.PIR.event.set()
        except AttributeError:
            pass

#_______________________________________________________________________________________________________________________


class Temp_thread(threading.Thread):

    def __init__(self, Qu):
        threading.Thread.__init__(self)
        self.Q = Qu
        self.thermometer = Temperature_detector.Temperature_detector(self.Q)

    def run(self):
        self.thermometer.measure()


    def end(self):
        try:
            self.thermometer.event.set()
        except AttributeError:
            pass


#_______________________________________________________________________________________________________________________
X = True     # allows only one alert sound simultaneously ! (max 8)

class Sound_thread(threading.Thread):

    def __init__(self, command):
        threading.Thread.__init__(self)
        self.command = command


    def run(self):
        global X
        if self.command == "alert" and X:
            X = False
            self.Alert_sound = Sounds.Sounds(self.command)

        elif self.command != "alert" and self.command != "end_alert" and self.command != "set_X_when_tensor_is_ON":
            self.normal_sound = Sounds.Sounds(self.command)

        elif self.command == "end_alert":
            self.end = Sounds.Sounds(self.command)

        elif self.command == "set_X_when_tensor_is_ON":  # set X=true when alarm is off
            X = True


    #_______________________________________________________________________________________________________________________

class FTPserver(threading.Thread):

    def __init__(self):
        self.serwer = socket.socket(socket.AF_INET, socket.SOCK_STREAM, socket.getprotobyname('tcp'))
        self.serwer.bind(('192.168.0.12', 8888))
        threading.Thread.__init__(self)
        self.event = threading.Event()

    def run(self):
        self.serwer.listen(5)
        while not self.event.is_set():
            self.th = serwerFTP.FTPserverThread(self.serwer.accept(), self.serwer)
            self.th.start()

    def stop(self):
        try:
            self.th.event.set()
        except:
            pass
        self.event.set()
        socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect(('192.168.0.12', 8888))
        self.serwer.close()

# _______________________________________________________________________________________________________________________

class Photo_thread(threading.Thread):

    def __init__(self, queue1):
        threading.Thread.__init__(self)
        self.queue2 = queue1
        self.photo = Camera.Camera(self.queue2)


    def run(self):
        self.photo.take_photo()

# _______________________________________________________________________________________________________________________

class SMS(threading.Thread):

    def __init__(self):
        threading.Thread.__init__(self)
        self.account_sid = ""
        self.auth_token = ""

    def run(self):
        client = Client(self.account_sid, self.auth_token)

        message = client.messages.create(
            to="",
            from_="",
            body="Move detected!")

        #print(message.sid)

# _______________________________________________________________________________________________________________________

class Email(threading.Thread):

    def __init__(self, path, event_time):
        threading.Thread.__init__(self)
        self.path=path
        self.event_time=event_time

    def run(self):

        # r+ is used for reading, and writing mode. b is for binary. r+b mode is open the binary file in read or write mode.
        img_data = open(self.path, 'rb').read()

        msg = MIMEMultipart()
        msg['Subject'] = 'Home security guard '+self.event_time  # message subject
        msg['Text'] = 'Move detected! '+self.event_time  # message text
        msg['From'] = 'telephonersprojekty@gmail.com'  # from address ..
        msg['To'] = 'telephonersprojekty@gmail.com'  # to address ..

        text = MIMEText(msg['Text'])
        msg.attach(text)
        image = MIMEImage(img_data, name=os.path.basename(self.path))
        msg.attach(image)

        s = smtplib.SMTP('smtp.gmail.com', 587)  # specify the smtp mail server and port
        s.ehlo()  # identify yourself to the server
        s.starttls()  # start transport layer security (stl) stl -> any smtp command after this is going to be encrypted
        s.ehlo()
        s.login('telephonersprojekty@gmail.com', 'password')  # email and password
        s.sendmail(msg['From'], msg['To'], msg.as_string())  # from.. to..
        s.quit()  # close connection
