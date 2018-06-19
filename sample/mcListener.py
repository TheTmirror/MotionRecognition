# -*- coding: utf-8 -*-
import threading
import sys
sys.path.insert(0, '/home/pi/Desktop/Griffin')
from pypowermate import powermate

from decimal import Decimal, getcontext
getcontext().prec = 15

from events import BaseEvent, RotationEvent, ButtonEvent, EVENT_BASE, EVENT_ROTATE, EVENT_BUTTON

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

        sum = 0
        
        while True:
            (time, event, val) = self.knob.read_event()
            time = Decimal('{}'.format(time))
            val = Decimal('{}'.format(val))

            if event == EVENT_ROTATE:
                sum = Decimal(sum) + val
                event = RotationEvent(time, val, sum)
            elif event == EVENT_BUTTON:
                event = ButtonEvent(time, val)

            if event.getEvent() == EVENT_BUTTON and event.getValue() == Decimal('0'):
                print('Button Event')
                if tapTimeStamp != None and (event.getTime() - tapTimeStamp) <= Decimal('{}'.format(timeout)):
                    self.signalsLock.acquire()
                    self.signals.append(event)
                    self.signalsLock.release()
                    print('Double Klicked')
                    break
                else:
                    tapTimeStamp = event.getTime()
            
            self.signalsLock.acquire()
            self.signals.append(event)
            self.signalsLock.release()
