# -*- coding: utf-8 -*-
#System
import threading
import sys
import serial
import time

#Project
from ipc import IPCMemory
from decimal import Decimal, getcontext
from events import BaseEvent, AboartEvent, TouchEvent
from events import EVENT_BASE, EVENT_ABOART, EVENT_TOUCH

#Scriptsetup
getcontext().prec = 15

class TouchListener(threading.Thread):

    usbPath = '/dev/ttyACM0'
    baudrate = 9600
    
    def __init__(self, signals, signalsLock):
        threading.Thread.__init__(self)
        self.signals = signals
        self.signalsLock = signalsLock

        self.sm = IPCMemory()
        self.smCounter = 0
        
        self.ser = serial.Serial(self.usbPath, self.baudrate)
        self.ser.flush()

    
    def run(self):
        print('TouchListener is running')
        self.startListening()

    
    def startListening(self):
        tapTimeStamp = None
        timeout = 0.5

        sum = 0

        while True:
            self.checkSharedMemory()
            if(self.ser.inWaiting() <= 0):
                continue


                continue
            
            event = input[:input.find(';')]
            input = input[input.find(';')+1:]
            location = input[:input.find(';')]
            input = input[input.find(';')+1:]
            val = input[:input.find(';')]
            val = Decimal('{}'.format(val)).normalize()

            t = time.time()
            t = Decimal('{}'.format(t)).normalize()
            print(t)
            
            if event == EVENT_TOUCH:
                event = TouchEvent(t, location, val)

            if event.getEvent() == EVENT_TOUCH and event.getValue() == Decimal('0'):
                if tapTimeStamp != None and (event.getTime() - tapTimeStamp) <= Decimal('{}'.format(timeout)):
                    self.signalsLock.acquire()
                    self.aboart()
                    #print('Gestenende wurde erkannt')
                    self.signalsLock.release()
                else:
                    tapTimeStamp = event.getTime()
            
            self.signalsLock.acquire()
            self.signals.append(event)
            self.signalsLock.release()

        self.cleanUp()

    #ATTENTION NOT THREAD SAFE! LOCK ME REQUIRED BEFORE AND RELEASED AFTER
    def aboart(self):
        aboartEvent = AboartEvent(time.time())
        self.signals.append(aboartEvent)
        
        counter = 0
        for i in range(len(self.signals)-1, -1, -1):
            if self.signals[i].getEvent() == EVENT_TOUCH and counter < 3:
                self.signals[i] = None
                counter = counter + 1
            elif counter == 3:
                break

    def convertText(self, text = None):
            text = text[:len(text)-2]
            text = text.decode('utf-8')
            return text

    def synchronizeTime(self):
        self.ser.write("T{}".format(time.time()).encode())
        print("Time: {} - Synchronization Forced", time.time())

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

    def cleanUp(self):
        print('TouchListener wurde beendet')
