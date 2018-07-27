# -*- coding: utf-8 -*-
#System
import threading
import sys

#Systempaths
sys.path.insert(0, '/home/pi/Desktop/Griffin')
sys.path.insert(0, '/home/pi/Desktop/Updated Project/math')

#Project
from ipc import IPCMemory
from pypowermate import powermate
from myMath import Interpolator, Calculator
from motion import Motion
from motionManager import MotionManager
from events import BaseEvent, AboartEvent, RotationEvent, ButtonEvent
from events import EVENT_BASE, EVENT_ABOART, EVENT_ROTATE, EVENT_BUTTON
from transformer import MotionTransformer, NotEnoughSignals

class MotionDetecter(threading.Thread):

    MODE_RECOGNITION = 'recognition'
    MODE_LEARNING = 'learning'

    def __init__(self, signals, signalsLock):
        threading.Thread.__init__(self)
        self.signals = signals
        self.signalsLock = signalsLock
        self.sm = IPCMemory()
        self.smCounter = 0

        self.motionManager = MotionManager()

    def run(self):
        print("Motion Detecter is running")
        print(self.motionManager.getAllMotions())
        if not self.motionManager.getAllMotions():
            self.learnLearningMotion()
        self.startRecognition()

    def startRecognition(self):
        self.mode = self.MODE_RECOGNITION
        while True:
            self.waitForAboart()
            print('Geste wurde erkannt')
            self.sm.add(IPCMemory.RESET_ROTATION_SUM)

            transformer = MotionTransformer()
            motionToCompare = transformer.transformMotion(self.signalsCopy)

            c = Calculator()
            bestMotion = None
            bestScore = None
            for motion in self.motionManager.getAllMotions():
                matchingScore = c.getMatchingScore(self.motionManager.getMotion(motion), motionToCompare)
                print("Matching Score with '{}': {}".format(self.motionManager.getMotion(motion).getName(), matchingScore))

                if bestMotion == None:
                      bestScore = matchingScore
                      bestMotion = self.motionManager.getMotion(motion)
                      continue

                if matchingScore > bestScore:
                      bestScore = matchingScore
                      bestMotion = self.motionManager.getMotion(motion)

            if bestMotion == None:
                print("Es sind noch keine Motions angelernt")
            else:
                print("Motion {} für Device {} erkannt".format(bestMotion.getName(), bestMotion.getAssignedDevice()))

            if bestMotion.getName() == 'startLearning':
                self.sm.add(IPCMemory.START_LEARNING)

    def startLearning(self):
        self.mode = self.MODE_LEARNING
        self.signalsLock.acquire()
        del self.signals[:]
        self.signalsLock.release()

        self.waitForAboart()

        self.sm.add(IPCMemory.RESET_ROTATION_SUM)

        transformer = MotionTransformer()
        try :
            motion = transformer.transformMotion(self.signalsCopy)
        except NotEnoughSignals:
            print("Die Geste beinhaltet keine Aktionen. Sie wird nicht gespeichert")
            return

        name = input('Wie soll die Motion heißen?')
        motion.setName(name)

        self.motionManager.addMotion(motion)

        self.mode = self.MODE_RECOGNITION

    def learnLearningMotion(self):
        self.mode = self.MODE_LEARNING
        self.signalsLock.acquire()
        del self.signals[:]
        self.signalsLock.release()
        
        print('Jetzt bitte Geste ausführen mit der später neue Gesten angelernt werden sollen')

        self.waitForAboart()

        self.sm.add(IPCMemory.RESET_ROTATION_SUM)

        transformer = MotionTransformer()
        try :
            motion = transformer.transformMotion(self.signalsCopy)
        except NotEnoughSignals:
            print("Die Geste beinhaltet keine Aktionen. Sie wird nicht gespeichert")
            return

        motion.setName('startLearning')

        self.motionManager.addMotion(motion)

    def waitForAboart(self):
        print('Jetzt bitte Geste ausführen und mit Doppelklick bestätigen')
        counter = 0

        while True:
            self.checkSharedMemory()
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

    def checkSharedMemory(self):
        import time
        #print('Checking Size')
        #print('SmCounter = {}'.format(self.smCounter))
        #print('SmSize = {}'.format(self.sm.getSize()))
        if self.smCounter < self.sm.getSize():
            message = self.sm.get(self.smCounter)
            #print(message)

            self.smCounter = self.smCounter + 1

            if message == IPCMemory.SHUTDOWN:
                print('I shall shutdown')
                time.sleep(2)
                sys.exit()
            elif message == IPCMemory.START_LEARNING:
                if self.mode == self.MODE_LEARNING:
                    print("I'm already learning")
                else:
                    print('I shall start learning')
                    time.sleep(2)
                    self.startLearning()
            elif message == IPCMemory.START_RECOGNIZING:
                if self.mode == self.MODE_RECOGNITION:
                    print("I'm already recognizing")
                else:
                    print('I shall start recognition')
                    time.sleep(2)
                    self.startRecognition()
