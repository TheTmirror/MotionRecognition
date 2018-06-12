import threading
import mcListener
import motionRecognizer

import sys

class Controller:
    
    def __init__(self):
        self.signals = []
        self.start()
        
    def start(self):
        
        signalsLock = threading.Lock()
        
        listenerThread = mcListener.MicroControllerListener(self.signals, signalsLock)
        recognizerThread = motionRecognizer.MotionRecognizer(self.signals, signalsLock)
        
        listenerThread.start()
        recognizerThread.start()
        
        #listenerThread.join()
        #recognizerThread.join()
        print('Controller wird beendet')