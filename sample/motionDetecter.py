# -*- coding: utf-8 -*-
import threading
import sys
sys.path.insert(0, '/home/pi/Desktop/Griffin')
from pypowermate import powermate

sys.path.insert(0, '/home/pi/Desktop/Updated Project/math')
from myMath import Interpolator, Calculator

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
            print("Could not load Motions")
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

        motionToCompare = self.transformMotion()

        c = Calculator()
        bestMotion = None
        bestScore = None
        for motion in self.motions:
            matchingScore = c.getMatchingScore(motion, motionToCompare)
            print("Matching Score with '{}': {}".format(motion.getAssociatedDevice(), matchingScore))

            if bestMotion == None:
                  bestScore = matchingScore
                  bestMotion = motion
                  continue

            if matchingScore > bestScore:
                  bestScore = matchingScore
                  bestMotion = motion

        print("Motion für Device {} erkannt".format(bestMotion.getAssociatedDevice()))

    def startLearning(self):
        self.signalsLock.acquire()
        del self.signals[:]
        self.signalsLock.release()
        
        print('Jetzt bitte Geste ausführen und mit Doppelklick bestätigen')

        self.waitForDoubleClick()

        name = input('Wie soll die Motion heißen?')

        motion = self.transformMotion()
        motion.associate(name)

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
        interpolator = Interpolator()
        n = 64

        recordedRotations = []
        recordedButtons = []
        for event in self.signalsCopy:
            if isinstance(event, RotationEvent):
                recordedRotations.append(event)
            elif isinstance(event, ButtonEvent):
                recordedButtons.append(event)
            else:
                pass

        #Construct Motion
        transformedMotion = Motion()
        
        #Rotation Part of Motion
        result = interpolator.linearInterpolation(recordedRotations, n)

        transformedTime = result[0]
        transformedSum = result[1]

        for i in range(len(transformedTime)):
            event = RotationEvent(transformedTime[i], None, transformedSum[i])
            transformedMotion.addEvent(event)

        #Other Parts of Motion
        for event in recordedButtons:
            transformedMotion.addEvent(event)

        #Scaling and adjustment
        self.scaleMotion(transformedMotion)
        self.adjustValues(transformedMotion)
        
        return transformedMotion

    def scaleMotion(self, motion):
        from decimal import Decimal, getcontext
        getcontext().prec = 15
        
        #Find Max RotationValue
        maxValue = None
        for event in motion.getEvents():
            if isinstance(event, RotationEvent):
                if maxValue == None:
                    maxValue = abs(event.getSum())
                elif maxValue < abs(event.getSum()):
                    maxValue = abs(event.getSum())

        for event in motion.getEvents():
            if isinstance(event, RotationEvent):
                event.sum = event.sum * (Decimal('400') / maxValue)

    def adjustValues(self, motion):
        rotationEvents = []
        
        for event in motion.getEvents():
            if isinstance(event, RotationEvent):
                rotationEvents.append(event)

        for i in range(len(rotationEvents)):
            if i == 0:
                rotationEvents[i].value = rotationEvents[i].getSum()
            else:
                rotationEvents[i].value = rotationEvents[i].getSum() - rotationEvents[i-1].getSum()

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
                    self.clearDoubleClick(self.signalsCopy)
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

    def clearDoubleClick(self, signals):
        removedButtonEvents = 0
        for i in range(len(signals)-1, -1, -1):
            if removedButtonEvents == 4:
                break
            
            event = signals[i]
            if isinstance(event, ButtonEvent):
                del signals[i]
                removedButtonEvents = removedButtonEvents + 1        
            
