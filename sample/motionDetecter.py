# -*- coding: utf-8 -*-
import threading
import sys
sys.path.insert(0, '/home/pi/Desktop/Griffin')
from pypowermate import powermate

class MotionDetecter(threading.Thread):

    MODE_RECOGNITION = 'recognition'
    MODE_LEARNING = 'learning'

    def __init__(self, signals, signalsLock, mode):
        threading.Thread.__init__(self)
        self.signals = signals
        self.signalsLock = signalsLock
        self.mode = mode

    def run(self):
        if self.mode == self.MODE_RECOGNITION:
            self.startRecognition()
        elif self.mode == self.MODE_LEARNING:
            self.startLearning()

    def startRecognition(self):
        pass

    def startLearning(self):
        self.signalsLock.acquire()
        del self.signals[:]
        self.signalsLock.release()
        
        print('Jetzt bitte Geste ausführen und mit Doppelklick bestätigen')

        self.waitForDoubleClick()

        motionTemplate = self.transformMotion()

        self.saveMotion(motionTemplate)

    def saveMotion(self, template):
        from dataManager import dataManager

        dm = DataManager()

        rotationTemplate = template[0]
        templateValues = []
        for rotation in rotationTemplate:
            (time, value) = rotation
            templateValues.append(value)

        rotationPathPi = '/home/pi/Desktop/Updated Project/templates/pi/template1/rotation.txt'
        rotationPathExcel = '/home/pi/Desktop/Updated Project/templates/excel/template1/rotation.txt'
        if not os.path.exists(os.path.dirname(rotationPathPi)):
            os.makedirs(os.path.dirname(rotationPathPi))
        if not os.path.exists(os.path.dirname(rotationPathExcel)):
            os.makedirs(os.path.dirname(rotationPathExcel))
            
        dm._saveValues(templateValues, rotationPathPi, rotationPathExcel)
        #Do the same for the others

        print('Motion Saved')

    #Should be reuseable
    def transformMotion(self):
        import sys
        sys.path.insert(0, '/home/pi/Desktop/Updated Project/math')
        from myMath import Interpolator

        interpolator = Interpolator()
        resultSet = []

        #Rotation
        recorded = []
        for signal in self.signalsCopy:
            (time, event, value, summe) = signal
            
            if event == powermate.Powermate.EVENT_ROTATE:
                recorded.append(signal)

        rotationResult = interpolator.linearSummeInterpolation(recorded)

        #Buttons etc...

        resultSet.append(rotationResult)

        return resultSet

        

    def waitForDoubleClick(self):
        timeout = 0.5
        
        counter = 0
        clickTime = None
        
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
            (time, event, value, summe) = self.signals[counter]

            if event == powermate.Powermate.EVENT_BUTTON and value == 0:
                if clickTime != None and (time - clickTime) <= timeout:
                    self.saveCopyOfSignals()
                    del self.signals[:]
                    self.signalsLock.release()
                    break
                else:
                    clickTime = time
            
            self.signalsLock.release()
            counter = counter + 1

    #ATTENTION! LOCK MUST BE REQUIRED FIRST!!!
    def saveCopyOfSignals(self):
        self.signalsCopy = self.signals[:]
        
            
