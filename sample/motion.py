class Motion:

    def __init__(self):
        self.times = None
        self.events = None
        self.values = None
        self.summen = None

        self.associatedDevice = None

    def isAssociated(self):
        return self.associatedDevice != None

    def isEmpty(self):
        if self.times == None and self.events == None and self.values == None and self.summen == None:
            return True
        else:
            return False

    def setTimes(self, times):
        self.times = times

    def setEvent(self, events):
        self.events = events

    def setValues(self, values):
        self.values = values

    def setSummen(self, summen):
        self.summen = summen

    def getTimes(self):
        return self.times

    def getEvent(self):
        return self.events

    def getValues(self):
        return self.values

    def getSummen(self):
        return self.summen
