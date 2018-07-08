import threading
import sys
import serial
import time

from decimal import Decimal, getcontext
getcontext().prec = 15

from events import TouchEvent, EVENT_TOUCH

class TouchListener(threading.Thread):

    usbPath = '/dev/ttyACM0'
    baudrate = 9600
    
    def __init__(self, signals, signalsLock):
        threading.Thread.__init__(self)
        self.signals = signals
        self.signalsLock = signalsLock
        try:
            self.ser = serial.Serial(self.usbPath, self.baudrate)
            self.ser.flush()
        except:
            print("Something went wrong")
    
    def run(self):
        print('Starting Listening Thread')
        self.setupArduino()
        self.startListening()

    def setupArduino(self):
        while True:
            text = self.convertText(self.ser.readline())
            if text == "TIME_REQUEST":
                break
            else:
                print("WRONG TEXT")
                print(text)
        self.ser.write("T{}".format(time.time()).encode())
        print("Done")
    
    def startListening(self):
        tapTimeStamp = None
        timeout = 0.5

        sum = 0
        
        while True:
            input = self.ser.readline()
            input = self.convertText(input)
            time = input[:input.find(';')]
            input = input[input.find(';')+1:]
            event = input[:input.find(';')]
            input = input[input.find(';')+1:]
            location = input[:input.find(';')]
            input = input[input.find(';')+1:]
            val = input[:input.find(';')]
            time = Decimal('{}'.format(time)).normalize()
            val = Decimal('{}'.format(val)).normalize()

            print("Time: {}\nEvent: {}\nLocation: {}\nValue: {}".format(time, event, location, val));
            
            if event == EVENT_TOUCH:
                event = TouchEvent(time, location, val)

            if event.getEvent() == EVENT_TOUCH and event.getValue() == Decimal('0'):
                if tapTimeStamp != None and (event.getTime() - tapTimeStamp) <= Decimal('{}'.format(timeout)):
                    self.signalsLock.acquire()
                    self.signals.append(event)
                    self.signalsLock.release()
                    print('Double Touched')
                    
                    break
                else:
                    tapTimeStamp = event.getTime()
            
            self.signalsLock.acquire()
            self.signals.append(event)
            self.signalsLock.release()

    def convertText(self, text = None):
            text = text[:len(text)-2]
            text = text.decode('utf-8')
            return text

    def debug(self):
        while True:
            print(self.ser.readline())

if __name__ == '__main__':
    t = TouchListener([], threading.Lock())
    t.run()
