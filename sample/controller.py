import threading
import motionRecognizer
import mcListener
from motionDetecter import MotionDetecter

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
        #recognizerThread = motionRecognizer.MotionRecognizer(self.signals, signalsLock, self.devices)
        detectionThread = MotionDetecter(self.signals, signalsLock,
                                         MotionDetecter.MODE_RECOGNITION)
        
        listenerThread.start()
        #recognizerThread.start()
        detectionThread.start()
        
        listenerThread.join()
        #recognizerThread.join()
        detectionThread.join()

        #self.detect()
        
        print('Controller wird beendet')

    def detect(self):
        sys.path.insert(0, '/home/pi/Desktop/Updated Project/math')
        from myMath import myLinearInterpolation

        from dataManager import DataManager
        dm = DataManager()

        n = 64
        data = []

        for signal in self.signals:
            (t, e, v, s) = signal

            if s != None:
                data.append((t, s))

        results = myLinearInterpolation(data, n)

        piPathTime = '/home/pi/Desktop/Updated Project/logs/pi/mappedTime.txt'
        piPathSumme = '/home/pi/Desktop/Updated Project/logs/pi/mappedSumme.txt'

        exPathTime = '/home/pi/Desktop/Updated Project/logs/excel/mappedTime.txt'
        exPathSumme = '/home/pi/Desktop/Updated Project/logs/excel/mappedSumme.txt'

        times = []
        summen = []

        for result in results:
            (t, s) = result
            times.append(t)
            summen.append(s)

        dm._saveTimes(times, piPathTime, exPathTime)
        dm._saveSummen(summen, piPathSumme, exPathSumme)
            

    def initDevices(self):
        self.devices = []
        
        phueBulbKitchen = philipsHueLightBulb.PhilipsHueLightBulb()
        self.devices.append(['Philips Hue Light Bulb Kitchen', phueBulbKitchen])
        
        phueBulbLivingRoom = philipsHueLightBulb.PhilipsHueLightBulb()
        self.devices.append(['Philips Hue Light Bulb Living Room', phueBulbLivingRoom])

        knob = powermate.Powermate(mcListener.devicePath)
        self.devices.append(['Knob', knob])
