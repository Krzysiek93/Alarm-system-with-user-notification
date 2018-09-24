import picamera
from time import sleep, gmtime, strftime



class Camera():
    def __init__(self, queue2):
        try:
            self.queue3 = queue2
            self.camera = picamera.PiCamera()
        except:
            pass

    def take_photo(self):
        try:
            self.showtime = str(strftime('%Y-%m-%d %H:%M:%S', gmtime()))
            self.camera.start_preview(fullscreen=True)
            self.camera.hflip = True
            self.camera.vflip = True
            self.camera.brightness = 60
            self.path = '/home/pi/PycharmProjects/Alarm/Photos/'+self.showtime+'.jpg'
            self.path = str(self.path.replace(' ', '__'))

            self.queue3.put(self.path)
            sleep(0.5)
            self.camera.capture(self.path)
        except:
            pass
        finally:
            self.camera.stop_preview()
            self.camera.close()










