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

        #Der TouchThreshhold ist die Zeit, die vergehen muss,
        #damit ein Touch Signal als gültig erkannt wird
        self.threshhold = 0.2
        self.touchCounter = 0;
    
    def run(self):
        print('TouchListener is running')
        self.startListening()

    def startListening(self):
        self.eventsMetaInfo = dict()

        while True:
            self.checkSharedMemory()
            self.updateEvents()
            if(self.ser.inWaiting() <= 0):
                continue

            event = self.getEvent()

            if event == None:
                continue

            #Event in DIC einfügen
            subDic = None
            if event.getLocation() in self.eventsMetaInfo:
                subDic = self.eventsMetaInfo[event.getLocation()]
            else:
                subDic = {}
                subDic['lastEventValue'] = None
                subDic['event'] = None
                self.eventsMetaInfo[event.getLocation()] = subDic

            subDic['event'] = event

        self.cleanUp()

    def updateEvents(self):
        for key in self.eventsMetaInfo:
            subDic = self.eventsMetaInfo[key]
            subDic['timeSinceLastEvent'] = Decimal(time.time()) - subDic['event'].getTime()

        for key in self.eventsMetaInfo:
            subDic = self.eventsMetaInfo[key]
            if subDic['timeSinceLastEvent'] > self.threshhold:
                if subDic['lastEventValue'] == None or subDic['lastEventValue'] != subDic['event'].getValue():
                    self.addEvent(subDic['event'])
                    subDic['lastEventValue'] = subDic['event'].getValue()

    def addEvent(self, event):
        self.signalsLock.acquire()
        self.signals.append(event)
        self.signalsLock.release()

        if event.getValue() == 1:
            self.touchCounter = self.touchCounter + 1
        else:
            if self.touchCounter == 1:
                print("Gestenende wurde erkannt")
                self.signalsLock.acquire()
                self.aboart()
                self.signalsLock.release()

            self.touchCounter = self.touchCounter - 1

    def getEvent(self):
        input = self.ser.readline()
        input = self.convertText(input)
            
        event = input[:input.find(';')]
        input = input[input.find(';')+1:]
        location = input[:input.find(';')]
        input = input[input.find(';')+1:]
        val = input[:input.find(';')]
        val = Decimal('{}'.format(val)).normalize()

        t = time.time()
        t = Decimal('{}'.format(t)).normalize()

        if event == EVENT_TOUCH:
            return TouchEvent(t, location, val)
        else:
            return None

    #ATTENTION NOT THREAD SAFE! LOCK ME REQUIRED BEFORE AND RELEASED AFTER
    def aboart(self):
        aboartEvent = AboartEvent(time.time())
        self.signals.append(aboartEvent)

    def convertText(self, text = None):
            text = text[:len(text)-2]
            text = text.decode('utf-8')
            return text

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
