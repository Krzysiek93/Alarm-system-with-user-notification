import threading
from PIL import Image
import os

class FTPserverThread(threading.Thread):

    def __init__(self, tup, soc):
        self.soc = soc
        self.conn = tup[0]
        self.addr = tup[1]

        self.user = 'admin'
        self.passwd = 'admin'

        threading.Thread.__init__(self)
        self.event = threading.Event()

    def run(self):
        while not self.event.is_set():
            message = self.conn.recv(64)
            print('f')
            if message:
                try:
                    print("Otrzymana wiadomosc: {} , z adresu: {}".format(message, self.addr))
                    dec = message.decode("utf-8")
                    func = getattr(self, dec[0:4].strip().upper())
                    func()
                except AttributeError:
                    print("Otrzymana wiadomosc: {} , z adresu: {}".format(message, self.addr))
                    self.conn.send("Nieznane polecenie")
            else:
                break


    def USER(self):
        while True:
            message = self.conn.recv(64).decode("utf-8")
            if message == self.user:
                print("Otrzymana wiadomosc: {} , z adresu: {}".format(message, self.addr))
                self.conn.send('ok'.encode())
                self.login = True
                break
            elif message is not self.user and message:
                print("Otrzymana wiadomosc: {} , z adresu: {}".format(message, self.addr))
                self.conn.send('bad username'.encode())
                break


    def PASS(self):
        #self.conn.send("Password: ")
        while True:
            message = self.conn.recv(64).decode("utf-8")
            if message == self.passwd:
                print("Otrzymana wiadomosc: {} , z adresu: {}".format(message, self.addr))
                self.conn.send('ok'.encode())
                self.login = True
                break
            elif message is not self.passwd and message:
                print("Otrzymana wiadomosc: {} , z adresu: {}".format(message, self.addr))
                self.conn.send('bad passwd'.encode())
                break

    def SEND(self):
        try:
            for i in os.listdir('/home/pi/PycharmProjects/Alarm/Photos'):
                data = open("/home/pi/PycharmProjects/Alarm/Photos/"+i, "rb").read()
                self.conn.send(data)
                os.remove("/home/pi/PycharmProjects/Alarm/Photos/"+i)
                print("Data sent successfully")
        except:
            pass










