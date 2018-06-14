import threading
import sys
sys.path.insert(0, '/home/pi/Desktop/Griffin')
from pypowermate import powermate

devicePath = '/dev/input/by-id/usb-Griffin_Technology__Inc._Griffin_PowerMate-event-if00'

class MicroControllerListener(threading.Thread):
    
    def __init__(self, signals, signalsLock):
        threading.Thread.__init__(self)
        self.signals = signals
        self.signalsLock = signalsLock
        self.knob = powermate.Powermate(devicePath)
    
    def run(self):
        print('Starting Listening Thread')
        self.startListening()
    
    def startListening(self):

        tapTimeStamp = None
        timeout = 0.5
        
        while True:
            (timeStamp, event, val) = self.knob.read_event()
            tupel = (timeStamp, event, val)

            if event == powermate.Powermate.EVENT_BUTTON and val == 0:
                print('Button Event')
                if tapTimeStamp != None and (timeStamp - tapTimeStamp) <= timeout:
                    print('Double Klicked')
                    break
                else:
                    tapTimeStamp = timeStamp
            
            self.signalsLock.acquire()
            self.signals.append(tupel)
            self.signalsLock.release()
