# -*- coding: utf-8 -*-
import threading
import sys
import serial
import time

from decimal import Decimal, getcontext
getcontext().prec = 15

from events import BaseEvent, AboartEvent, TouchEvent
from events import EVENT_BASE, EVENT_ABOART, EVENT_TOUCH

class TouchListener(threading.Thread):

    usbPath = '/dev/ttyACM0'
    baudrate = 9600
    
    def __init__(self, signals, signalsLock):
        threading.Thread.__init__(self)
        self.signals = signals
        self.signalsLock = signalsLock
        
        self.ser = serial.Serial(self.usbPath, self.baudrate)
        self.ser.flush()

        self.setupArduino()
    
    def run(self):
        print('TouchListener is running')
        self.startListening()

    def setupArduino(self, timeout = 10):
        t0 = time.time()

        print("Setting Up Arduino")
        while True:
            if time.time() - t0 >= timeout:
                raise NameError("Es gab einen Timeout beim Setup")
            if self.ser.inWaiting() > 0:
                text = self.convertText(self.ser.readline())
                if text.find("TIME_REQUEST") != -1:
                    break
        self.synchronizeTime()
        print("Arduino is Ready")
    
    def startListening(self):
        tapTimeStamp = None
        timeout = 0.5

        sum = 0

        while True:
            input = self.ser.readline()
            input = self.convertText(input)

            index = input.find("TIME_REQUEST")

            if index != -1:
                self.synchronizeTime()
                continue
            
            #time = input[:input.find(';')]
            #input = input[input.find(';')+1:]
            event = input[:input.find(';')]
            input = input[input.find(';')+1:]
            location = input[:input.find(';')]
            input = input[input.find(';')+1:]
            val = input[:input.find(';')]
            val = Decimal('{}'.format(val)).normalize()

            #print("Time: {}\nEvent: {}\nLocation: {}\nValue: {}".format(time, event, location, val));
            t = time.time()
            t = Decimal('{}'.format(t)).normalize()
            print(t)
            
            if event == EVENT_TOUCH:
                event = TouchEvent(t, location, val)

            if event.getEvent() == EVENT_TOUCH and event.getValue() == Decimal('0'):
                if tapTimeStamp != None and (event.getTime() - tapTimeStamp) <= Decimal('{}'.format(timeout)):
                    self.signalsLock.acquire()
                    #self.signals.append(event)
                    self.aboart()
                    self.signalsLock.release()
                    break
                else:
                    tapTimeStamp = event.getTime()
            
            self.signalsLock.acquire()
            self.signals.append(event)
            self.signalsLock.release()

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
