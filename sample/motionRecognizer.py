import threading
import time
import sys
sys.path.insert(0, '/home/pi/Desktop/Project/devices')

import philipsHueLightBulb

class MotionRecognizer(threading.Thread):
    
    devices = []
    
    def __init__(self, signals, signalsLock):
        threading.Thread.__init__(self)
        time.sleep(5)
        self.signals = signals
        self.signalsLock = signalsLock
        self.startDetection()
    
    def startDetection(self):
        print('Started Motion Detection')
        self.fillDevicesWithExamples()
        for device in self.devices:
            print(device)
        
    def fillDevicesWithExamples(self):
        #Philips Hue Light
        phueBulbKitchen = philipsHueLightBulb.PhilipsHueLightBulb()
        self.devices.append(['Philips Hue Light Bulb Kitchen', phueBulbKitchen])
        
        phueBulbLivingRoom = philipsHueLightBulb.PhilipsHueLightBulb()
        self.devices.append(['Philips Hue Light Bulb Living Room', phueBulbLivingRoom])