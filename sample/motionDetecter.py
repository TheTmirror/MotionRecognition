# -*- coding: utf-8 -*-
import threading
import sys
sys.path.insert(0, '/home/pi/Desktop/Griffin')
from pypowermate import powermate

sys.path.insert(0, '/home/pi/Desktop/Updated Project/math')
from myMath import Interpolator, Calculator

from motion import Motion
from events import BaseEvent, AboartEvent, RotationEvent, ButtonEvent
from events import EVENT_BASE, EVENT_ABOART, EVENT_ROTATE, EVENT_BUTTON

from transformer import MotionTransformer

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
        print("Motion Detecter is running")
        if self.mode == self.MODE_RECOGNITION:
            self.startRecognition()
        elif self.mode == self.MODE_LEARNING:
            self.startLearning()

    def startRecognition(self):
        print('Jetzt bitte Geste ausführen und mit Doppelklick bestätigen')
        self.waitForDoubleClick()

        transformer = MotionTransformer()
        motionToCompare = transformer.transformMotion(self.signalsCopy)

        c = Calculator()
        bestMotion = None
        bestScore = None
        for motion in self.motions:
            matchingScore = c.getMatchingScore(motion, motionToCompare)
            print("Matching Score with '{}': {}".format(motion.getName(), matchingScore))

            if bestMotion == None:
                  bestScore = matchingScore
                  bestMotion = motion
                  continue

            if matchingScore > bestScore:
                  bestScore = matchingScore
                  bestMotion = motion

        if bestMotion == None:
            print("Es sind noch keine Motions angelernt")
        else:
            print("Motion {} für Device {} erkannt".format(bestMotion.getName(), bestMotion.getAssociatedDevice()))

    def startLearning(self):
        self.signalsLock.acquire()
        del self.signals[:]
        self.signalsLock.release()
        
        print('Jetzt bitte Geste ausführen')

        self.waitForAboart()

        name = input('Wie soll die Motion heißen?')

        transformer = MotionTransformer()
        motion = transformer.transformMotion(self.signalsCopy)
        motion.setName(name)

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

    def waitForAboart(self):
        counter = 0

        while True:
            self.signalsLock.acquire()
            if len(self.signals) <= counter:
                self.signalsLock.release()
                continue
            event = self.signals[counter]

            if event != None and event.getEvent() == EVENT_ABOART:
                self.saveCopyOfSignals()
                self.removeAboartEvent(self.signalsCopy)
                self.removeNones(self.signalsCopy)
                del self.signals[:]
                self.signalsLock.release()
                break

            self.signalsLock.release()
            counter = counter + 1

    def removeAboartEvent(self, signals):
        for i in range(len(signals)-1, -1, -1):
            if signals[i].getEvent() == EVENT_ABOART:
                del signals[i]
                break

    #Signales that triggered the aboart are marked as None
    def removeNones(self, signals):
        for i in range(len(signals)-1, -1, -1):
            if signals[i] == None:
                del signals[i]

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
            
