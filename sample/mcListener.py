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

        self.tf = open('logTime.txt', 'w')
        self.vf = open('logValue.txt', 'w')
        self.ef = open('logEvent.txt', 'w')
    
    def run(self):
        print('Starting Listening Thread')
        self.startListening()
    
    def startListening(self):

        tapTimeStamp = None
        timeout = 0.5

        firstLogTime = None
        start = 0
        
        while True:
            (timeStamp, event, val) = self.knob.read_event()
            tupel = (timeStamp, event, val)

            if event == powermate.Powermate.EVENT_BUTTON and val == 0:
                print('Button Event')
                if tapTimeStamp != None and (timeStamp - tapTimeStamp) <= timeout:
                    print('Double Klicked')
                    self.tf.close()
                    self.vf.close()
                    self.ef.close()
                    break
                else:
                    tapTimeStamp = timeStamp

            if event == powermate.Powermate.EVENT_ROTATE:
                if firstLogTime == None:
                    firstLogTime = timeStamp
                    
                tString = "{}\n".format(timeStamp - firstLogTime).replace(".", ",")
                start = start + val
                vString = "{}\n".format(start)
                eString = "{}\n".format(event)

                self.tf.write(tString)
                self.vf.write(vString)
                self.ef.write(eString)
            
            self.signalsLock.acquire()
            self.signals.append(tupel)
            self.signalsLock.release()

        self.saveValues()

    def saveValues(self):
        sys.path.insert(0, '/home/pi/Desktop/Updated Project/math')
        from  myMath import _myLinearInterpolotion
        from decimal import Decimal, getcontext
        getcontext().prec = 15
        
        self.tf = open('logTime.txt', 'r')
        self.vf = open('logValue.txt', 'r')

        n = 64
        time = []
        val = []
        for line in self.tf:
            line = line[:len(line) - 1].replace(",", ".")
            time.append(Decimal(line))

        for line in self.vf:
            line = line[:len(line) - 1].replace(",", ".")
            val.append(Decimal(line))

        result = _myLinearInterpolotion(time, val, n)

        tf = open('logTimeMapped.txt', 'w')
        vf = open('logValMapped.txt', 'w')

        for r in result:
            (t, v) = r
            tString = "{}\n".format(t).replace(".", ",")
            vString = "{}\n".format(v).replace(".", ",")
            tf.write(tString)
            vf.write(vString)

        tf.close()
        vf.close()
            
