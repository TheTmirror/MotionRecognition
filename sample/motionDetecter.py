# -*- coding: utf-8 -*-
import threading
import sys
sys.path.insert(0, '/home/pi/Desktop/Griffin')
from pypowermate import powermate

from motion import Motion

class MotionDetecter(threading.Thread):

    MODE_RECOGNITION = 'recognition'
    MODE_LEARNING = 'learning'

    TEMPLATES_PATH = '/home/pi/Desktop/Updated Project/templates/'
    ROTATION_SUFFIX = 'rotation.txt'
    TIME_SUFFIX = 'times.txt'

    def __init__(self, signals, signalsLock, mode):
        threading.Thread.__init__(self)
        self.signals = signals
        self.signalsLock = signalsLock
        self.mode = mode

        self.loadMotions()

    def loadMotions(self):
        import os
        from dataManager import DataManager

        dm = DataManager()

        self.motions = []

        oldPath = os.getcwd()
        try:
            os.chdir(self.TEMPLATES_PATH)
        except FileNotFoundError:
            return

        #For jede Geste
        #For jeden Bestandteil einer Geste
        for dir in sorted(os.listdir()):
            if os.path.isfile(os.getcwd() + "/" + dir):
                continue

            motion = Motion()

            os.chdir(os.getcwd() + "/" + dir)
            for file in sorted(os.listdir()):
                filePath = os.getcwd() + "/" + file
                
                if os.path.isdir(filePath):
                    continue

                if file == self.TIME_SUFFIX:
                    motion.setTimes(dm.getTimes(filePath))
                elif file == self.ROTATION_SUFFIX:
                    motion.setSummen(dm.getSummen(filePath))

            if motion.isEmpty():
                continue
            else:
                self.motions.append(motion)
            os.chdir(os.pardir)

        os.chdir(oldPath)

    def run(self):
        if self.mode == self.MODE_RECOGNITION:
            self.startRecognition()
        elif self.mode == self.MODE_LEARNING:
            self.startLearning()

    def startRecognition(self):
        print('Jetzt bitte Geste ausführen und mit Doppelklick bestätigen')
        self.waitForDoubleClick()

        motion = self.transformMotion()

    def startLearning(self):
        self.signalsLock.acquire()
        del self.signals[:]
        self.signalsLock.release()
        
        print('Jetzt bitte Geste ausführen und mit Doppelklick bestätigen')

        self.waitForDoubleClick()

        motion = self.transformMotion()

        self.saveMotion(motion)

    def saveMotion(self, template):
        import os
        from dataManager import DataManager

        dm = DataManager()

        i = 0
        plainPath = self.TEMPLATES_PATH + 'template'
        while os.path.exists(plainPath + "%s/" % i):
            i = i + 1
        else:
            plainPath = plainPath + "%s/" % i

        if not os.path.exists(os.path.dirname(plainPath)):
            os.makedirs(os.path.dirname(plainPath))

        timePath = plainPath + self.TIME_SUFFIX
        dm.saveData(template.getTimes(), timePath)

        rotationPath = plainPath + self.ROTATION_SUFFIX
        dm.saveData(template.getSummen(), rotationPath)
        #Do the same for the others

        print('Motion Saved')

    #Should be reuseable
    def transformMotion(self):
        import sys
        sys.path.insert(0, '/home/pi/Desktop/Updated Project/math')
        from myMath import Interpolator

        interpolator = Interpolator()
        n = 64

        #Rotation
        recorded = []
        for signal in self.signalsCopy:
            (time, event, value, summe) = signal
            
            if event == powermate.Powermate.EVENT_ROTATE:
                recorded.append(signal)

        rotationResult = interpolator.linearSummeInterpolation(recorded, n)

        #Buttons etc...

        transformedMotion = Motion()
        transformedTime = []
        transformedSumme = []
        for (t, s) in rotationResult:
            transformedTime.append(t)
            transformedSumme.append(s)

        transformedMotion.setTimes(transformedTime)
        transformedMotion.setSummen(transformedSumme)
            
        return transformedMotion

        

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
        
            
