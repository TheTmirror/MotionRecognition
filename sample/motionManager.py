import os
from dataManager import DataManager

class MotionManager:

    TEMPLATES_PATH = '/home/pi/Desktop/Updated Project/templates/'

    def __init__(self):
        self.dm = DataManager()

    def loadMotions(self):
        motions = []

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

            motion = self.dm.getMotion(filePath)
            motions.append(motion)

        os.chdir(oldPath)

        return motions

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

        self.dm.saveMotion(template, plainPath)
        print('Motion Saved')
