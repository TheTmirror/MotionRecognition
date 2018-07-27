# -*- coding: utf-8 -*-
#System
import os

#Project
from dataManager import DataManager
from motion import Motion

class MotionManager:

    TEMPLATES_PATH = '/home/pi/Desktop/Updated Project/templates/'
    __motions = dict()
    __motionFiles = dict()

    def __init__(self):
        pass

    #Ggf. automatisiert möglich?
    def initMotions(self):
        dm = DataManager()
        #Hier alle Devices intitialisieren
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
            self.__motions[motion.getName()] = motion
            self.__motionFiles[motion.getName()] = file

        os.chdir(oldPath)

    def addMotions(self, newMotions):
        for motion in newMotions:
            self.addMotion(motion)

    def addMotion(self, newMotion):
        self.__motions[newMotion.getName()] = newMotion
        self.saveMotion(newMotion)

    def saveMotion(self, template):
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

    #Sollte von der Logik her wahrscheinlich in saveMotion mit rein
    def updateMotion(self, motion):
        dm = DataManager()
        path = self.TEMPLATES_PATH + self.getMotionFile(motion.getName())
        dm.saveMotion(motion, path)
        print('Motion Updated')

    def getAllMotions(self):
        return self.__motions

    def getMotion(self, key):
        return self.__motions[key]

    def getAllMotionFiles(self):
        return self.__motionFiles

    def getMotionFile(self, key):
        return self.__motionFiles[key]
