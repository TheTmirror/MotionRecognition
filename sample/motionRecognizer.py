import threading
import time
import sys

sys.path.insert(0, '/home/pi/Desktop/Griffin')
from pypowermate import powermate

class MotionRecognizer(threading.Thread):
    
    def __init__(self, signals, signalsLock, devices):
        threading.Thread.__init__(self)
        self.signals = signals
        self.signalsLock = signalsLock
        self.devices = devices
        
    def run(self):
        self.startDetection()
    
    def startDetection(self):
        print('Started Motion Detection')
        counter = 0
        while True:
            #Aktives warten ist scheiße
            #Gibt es bei Python eine Möglichkeit
            #für wait() und notify()
            self.signalsLock.acquire()
            if len(self.signals) <= counter:
                #print('Zu wenig Einträge')
                self.signalsLock.release()
                continue
            #print('Started Recognition')
            signal = self.signals[counter]
            counter = counter + 1
            self.signalsLock.release()
            
            if self.motionIsDetected(signal):
                print('Motion recognized')
                self.startTransmission()
                counter = 0
            
            
    def motionIsDetected(self, signal):
        (timeStamp, event, value) = signal
        if event == powermate.Powermate.EVENT_BUTTON and value == 0:
            return True
        else:
            return False
    
    #Muss ggf. in einem eigenem Thread
    #gestartet werden, da parallel immer noch
    #überprüft werden muss, dass dieselbe Geste
    #ausgeführt wird
    def startTransmission(self):
        print('Simulating transmitting the signals')

        inMotion = True
        lastTimeStamp = None
        timeout = 2
        
        selectedDevice = None
        for device in self.devices:
            if device[0] == 'Knob':
                print('Found Device: ', device[0])
                selectedDevice = device[1]
                break
        
        counter = 0
        #self.signalsLock.acquire()

        while inMotion:
            self.signalsLock.acquire()
            if counter >= len(self.signals):
               self.signalsLock.release()
               continue
            
            (timeStamp, event, value) = self.signals[counter]
            self.signalsLock.release()
            print(timeStamp)
            counter = counter + 1

            if lastTimeStamp != None and (timeStamp - lastTimeStamp) > timeout:
                inMotion = False
                print('Timeout')
                continue

            if event == powermate.Powermate.EVENT_ROTATE:
                #Dies ggf hinzufügen, falls die Signale mit dem selben
                #delay wie beim input ausgeführt werden sollen
                if False and lastTimeStamp != None:
                    time.sleep(timeStamp - lastTimeStamp)
                selectedDevice.set_steady_led(selectedDevice.brightness + value)

            lastTimeStamp = timeStamp
               
        self.signalsLock.acquire()
        del self.signals[:counter]
        self.signalsLock.release()
        print('Transmission done')
        print('Brightness is: ', selectedDevice.brightness)
            
    def exampleCode(self):
        self.fillDevicesWithExamples()
        for device in self.devices:
            print(device)
