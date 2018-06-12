import threading
import time
import sys
sys.path.insert(0, '/home/pi/Desktop/Project/devices')

import philipsHueLightBulb

class MotionRecognizer(threading.Thread):
    
    devices = []
    
    def __init__(self, signals, signalsLock):
        threading.Thread.__init__(self)
        self.signals = signals
        self.signalsLock = signalsLock
        
    def run(self):
        self.fillDevicesWithExamples()
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
        if signal == '5.00':
            return True
        else:
            return False
    
    #Muss ggf. in einem eigenem Thread
    #gestartet werden, da parallel immer noch
    #überprüft werden muss, dass dieselbe Geste
    #ausgeführt wird
    def startTransmission(self):
        print('Simulating transmitting the signals')
        
        selectedDevice = None
        for device in self.devices:
            if device[0] == 'Philips Hue Light Bulb Kitchen':
                print('Found Device: ', device[0])
                selectedDevice = device[1]
                break
        
        counter = 0
        self.signalsLock.acquire()
        while counter < len(self.signals):
            signal = self.signals[counter]
            self.signalsLock.release()
            counter = counter + 1
            #Here do something with the selected device
            if float(signal) <= 2.5:
                selectedDevice.increaseBrightness()
                print('Increased Brightness: ', selectedDevice.getBrightness())
            else:
                selectedDevice.reduceBrightness()
                print('Reduced Brightness: ', selectedDevice.getBrightness())
            
            self.signalsLock.acquire()
        self.signalsLock.release()
            
        self.signalsLock.acquire()
        del self.signals[:]
        self.signalsLock.release()
        print('Transmission done')
        print('Brightness is: ', selectedDevice.getBrightness())
            
    def exampleCode(self):
        self.fillDevicesWithExamples()
        for device in self.devices:
            print(device)
        
    def fillDevicesWithExamples(self):
        #Philips Hue Light
        phueBulbKitchen = philipsHueLightBulb.PhilipsHueLightBulb()
        self.devices.append(['Philips Hue Light Bulb Kitchen', phueBulbKitchen])
        
        phueBulbLivingRoom = philipsHueLightBulb.PhilipsHueLightBulb()
        self.devices.append(['Philips Hue Light Bulb Living Room', phueBulbLivingRoom])