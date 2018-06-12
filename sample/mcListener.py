import serial
import threading

class MicroControllerListener(threading.Thread):
    
    usbPath = '/dev/ttyACM0'
    baudrate = 9600
    
    def __init__(self, signals, signalsLock):
        threading.Thread.__init__(self)
        self.signals = signals
        self.signalsLock = signalsLock
    
    def run(self):
        print('Starting Listening Thread')
        self.startListening()
    
    def startListening(self):
        ser = None
        
        try:
            ser = serial.Serial(self.usbPath, self.baudrate)
        except serial.serialutil.SerialException:
            print('Auf den Microcontroller konnte nicht zugegriffen werden')
            return
            
        self.flushAll(ser)
        
        while True:
            text = ser.readline()
            text = self.convertText(text)
            
            self.signalsLock.acquire()
            self.signals.append(text)
            self.signalsLock.release()
            
            #breakout = False
            #for signal in self.signals:
            #    if signal == '5.00':
            #        breakout = True
            #        break
                
            #if breakout:
            #    print(self.signals)
            #    break
    
    def convertText(self, text = None):
            text = text[:len(text)-2]
            text = text.decode('utf-8')
            return text
        
    def flushAll(self, ser):
        ser.flushInput()
        ser.flushOutput()
        ser.flush()
        print('All Flushed')