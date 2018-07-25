# -*- coding: utf-8 -*-
import threading
from ipc import IPCMemory
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
        self.sm = IPCMemory()
        self.smCounter = 0
        self.knob = powermate.Powermate(devicePath)
    
    def run(self):
        print('Starting Listening Thread')
        self.startListening()
    
    def startListening(self):
        tapTimeStamp = None
        timeout = 0.5

        self.sum = 0
        
        while True:
            self.checkSharedMemory()

            pollResult = self.knob.read_event(0)
            if pollResult is None:
                continue
            
            (time, event, val) = pollResult
            time = Decimal('{}'.format(time)).normalize()
            val = Decimal('{}'.format(val)).normalize()

            if event == EVENT_ROTATE:
                self.sum = Decimal(self.sum) + val
                event = RotationEvent(time, val, self.sum)
            elif event == EVENT_BUTTON:
                event = ButtonEvent(time, val)

            if event.getEvent() == EVENT_BUTTON and event.getValue() == Decimal('0'):
                if tapTimeStamp != None and (event.getTime() - tapTimeStamp) <= Decimal('{}'.format(timeout)):
                    self.sm.add(IPCMemory.START_LEARNING)
                    #print('Added Learning')
                tapTimeStamp = event.getTime()
            
            self.signalsLock.acquire()
            self.signals.append(event)
            #print(event)
            self.signalsLock.release()

        self.cleanUp()

    #ATTENTION NOT THREAD SAFE! LOCK ME REQUIRED BEFORE AND RELEASED AFTER
    def aboart(self):
        counter = 0
        for i in range(len(self.signals)-1, -1, -1):
            if self.signals[i].getEvent() == EVENT_BUTTON and counter < 3:
                self.signals[i] = None
                counter = counter + 1
            elif counter == 3:
                break

    def checkSharedMemory(self):
        import time
        if self.smCounter < self.sm.getSize():
            message = self.sm.get(self.smCounter)
            self.smCounter = self.smCounter + 1

            if message == IPCMemory.SHUTDOWN:
                print('I shall shutdown')
                time.sleep(2)
                self.cleanUp()
                sys.exit()
            elif message == IPCMemory.RESET_ROTATION_SUM:
                print('I shall reset the rotation sum')
                self.sum = 0

    def cleanUp(self):
        print('McListener wird beendet')
