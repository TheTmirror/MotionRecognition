#System
import threading
import time
import sys

#Syspaths
sys.path.insert(0, '/home/pi/Desktop/Griffin')

#Project
from rest import RestServer
from deviceManager import DeviceManager
from ipc import IPCMemory
from mcListener import MicroControllerListener
from tListener import TouchListener
from motionDetecter import MotionDetecter
from motionManager import MotionManager

from pypowermate import powermate

class Controller:
    
    def __init__(self):
        self.signals = []
        self.initManager()
        #self.startRestServer()
        self.start()
        
    def start(self):
        
        signalsLock = threading.Lock()
        self.sm = IPCMemory()
        
        listenerThread = MicroControllerListener(self.signals, signalsLock)
        tThread = TouchListener(self.signals, signalsLock)
        detectionThread = MotionDetecter(self.signals, signalsLock)
        
        listenerThread.start()
        tThread.start()
        detectionThread.start()

        #self.initMultishutdown(10)
        
        listenerThread.join()
        tThread.join()
        detectionThread.join()
        
        print('Controller wird beendet')

    def startRestServer(self):
        restServer = RestServer()
        restServer.start()

    def initMultishutdown(self, time):
        print('Multishutdown incomming')
        for i in range(time, -1, -1):
            print(i)
            time.sleep(1)
        self.sm.add(IPCMemory.SHUTDOWN)

    def initManager(self):
        deviceManager = DeviceManager()
        deviceManager.initDevices()
        
        motionManager = MotionManager()
        motionManager.initMotions()
