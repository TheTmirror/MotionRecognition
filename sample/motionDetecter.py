# -*- coding: utf-8 -*-
import threading
import sys
sys.path.insert(0, '/home/pi/Desktop/Griffin')
from pypowermate import powermate

from motion import Motion
from events import BaseEvent, RotationEvent, ButtonEvent
from events import EVENT_BASE, EVENT_ROTATE, EVENT_BUTTON

class MotionDetecter(threading.Thread):

    MODE_RECOGNITION = 'recognition'
    MODE_LEARNING = 'learning'

    TEMPLATES_PATH = '/home/pi/Desktop/Updated Project/templates/'

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
        for file in sorted(os.listdir()):
            filePath = os.getcwd() + "/" + file
            if os.path.isdir(filePath):
                continue

                motion = dm.getMotion(filePath)
                self.motions.append(motion)

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
        while os.path.exists(plainPath + "%s.txt" % i):
            i = i + 1
        else:
            plainPath = plainPath + "%s.txt" % i

        if not os.path.exists(os.path.dirname(self.TEMPLATES_PATH)):
            os.makedirs(os.path.dirname(self.TEMPLATES_PATH))

        dm.saveMotion(template, plainPath)
        print('Motion Saved')

    #Should be reuseable
    def transformMotion(self):
        import sys
        sys.path.insert(0, '/home/pi/Desktop/Updated Project/math')
        from myMath import Interpolator

        interpolator = Interpolator()
        n = 64

        #Filter for interpolation
        recordedRotations = []
        for event in self.signalsCopy:
            if isinstance(event, RotationEvent):
                recordedRotations.append(event)
            else:
                pass

        #Construct Motion
        transformedMotion = Motion()
        
        #Rotation Part of Motion
        result = interpolator.linearInterpolation(recordedRotations, n)

        transformedTime = result[0]
        transformedSum = result[1]

        for i in range(len(transformedTime)):
            if i == 0:
                event = RotationEvent(transformedTime[i], transformedSum[i], transformedSum[i])
                transformedMotion.addEvent(event)
                continue
            
            value = transformedSum[i] - transformedSum[i-1]
            event = RotationEvent(transformedTime[i], value, transformedSum[i])
            transformedMotion.addEvent(event)

        #Other Parts of Motion
            
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
            event = self.signals[counter]

            if event.getEvent() == EVENT_BUTTON and event.getValue() == 0:
                if clickTime != None and (event.getTime() - clickTime) <= timeout:
                    self.saveCopyOfSignals()
                    del self.signals[:]
                    self.signalsLock.release()
                    break
                else:
                    clickTime = event.getTime()
            
            self.signalsLock.release()
            counter = counter + 1

    #ATTENTION! LOCK MUST BE REQUIRED FIRST!!!
    def saveCopyOfSignals(self):
        self.signalsCopy = self.signals[:]
        
            
