import threading
import mcListener
import motionRecognizer

class Controller:
    
    def __init__(self):
        self.signals = []
        self.start()
        
    def start(self):
        
        signalsLock = threading.Lock()
        
        listenerThread = mcListener.MicroControllerListener(self.signals, signalsLock)
        listenerThread.start()
        
        recognizerThread = motionRecognizer.MotionRecognizer(self.signals, signalsLock)
        recognizerThread.start()
        
        listenerThread.join()
        recognizerThread.join()
        print('Controller wird beendet')