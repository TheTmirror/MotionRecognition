# -*- coding: utf-8 -*-
import threading
import sys
sys.path.insert(0, '/home/pi/Desktop/Griffin')
from pypowermate import powermate

from decimal import Decimal, getcontext
getcontext().prec = 15

devicePath = '/dev/input/by-id/usb-Griffin_Technology__Inc._Griffin_PowerMate-event-if00'
class MicroControllerListener(threading.Thread):
    
    def __init__(self, signals, signalsLock):
        threading.Thread.__init__(self)
        self.signals = signals
        self.signalsLock = signalsLock
        self.knob = powermate.Powermate(devicePath)
    
    def run(self):
        print('Starting Listening Thread')
        self.startListening()
    
    def startListening(self):

        tapTimeStamp = None
        timeout = 0.5

        summe = 0
        
        while True:
            (timeStamp, event, val) = self.knob.read_event()
            timeStamp = Decimal('{}'.format(timeStamp))
            val = Decimal('{}'.format(val))
            
            if event == powermate.Powermate.EVENT_ROTATE:
                summe = Decimal(summe) + val
                tupel = (timeStamp, event, val, summe)
            else:
                tupel = (timeStamp, event, val, None)

            if event == powermate.Powermate.EVENT_BUTTON and val == Decimal('0'):
                print('Button Event')
                if tapTimeStamp != None and (timeStamp - tapTimeStamp) <= Decimal('{}'.format(timeout)):
                    self.signalsLock.acquire()
                    self.signals.append(tupel)
                    self.signalsLock.release()
                    print('Double Klicked')
                    break
                else:
                    tapTimeStamp = timeStamp
            
            self.signalsLock.acquire()
            self.signals.append(tupel)
            self.signalsLock.release()

        self.saveValues()

    def saveValues(self):
        from dataManager import DataManager

        dm = DataManager()
        #Während des Speicherns blockieren ist
        #nicht so sinnvoll. Lieber eine Copy anlegen
        self.signalsLock.acquire()
        dm.saveAllData(self.signals)
        self.signalsLock.release()
