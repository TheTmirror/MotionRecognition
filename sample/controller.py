import threading
import motionRecognizer
import mcListener

import sys

sys.path.insert(0, '/home/pi/Desktop/Updated Project/devices')
import philipsHueLightBulb

sys.path.insert(0, '/home/pi/Desktop/Griffin')
from pypowermate import powermate

class Controller:
    
    def __init__(self):
        self.signals = []
        self.initDevices()
        self.start()
        
    def start(self):
        
        signalsLock = threading.Lock()
        
        listenerThread = mcListener.MicroControllerListener(self.signals, signalsLock)
        recognizerThread = motionRecognizer.MotionRecognizer(self.signals, signalsLock, self.devices)
        
        listenerThread.start()
        recognizerThread.start()
        
        listenerThread.join()
        recognizerThread.join()
        print('Controller wird beendet')

    def initDevices(self):
        self.devices = []
        
        phueBulbKitchen = philipsHueLightBulb.PhilipsHueLightBulb()
        self.devices.append(['Philips Hue Light Bulb Kitchen', phueBulbKitchen])
        
        phueBulbLivingRoom = philipsHueLightBulb.PhilipsHueLightBulb()
        self.devices.append(['Philips Hue Light Bulb Living Room', phueBulbLivingRoom])

        knob = powermate.Powermate(mcListener.devicePath)
        self.devices.append(['Knob', knob])
