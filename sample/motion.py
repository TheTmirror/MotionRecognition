from events import BaseEvent, RotationEvent, ButtonEvent

class Motion:

    def __init__(self):
        self.events = None
        self.associatedDevice = None

    def isAssociated(self):
        return self.associatedDevice != None

    def isEmpty(self):
        if events == None:
            return True
        else:
            return False

    def setEvents(self, events):
        self.events = events

    def addEvent(self, event):
        if self.events == None:
            self.events = []

        self.events.append(event)

    def associate(self, device):
        self.associatedDevice = device

    def equals(self, motion):
        eventsToCompare = motion.getEvents()

        if len(self.events) != len(eventsToCompare):
            return False

        for i in range(len(self.events)):
            if(self.events[i].getTime() != eventsToCompare[i].getTime()):
                return False
            if type (self.events[i]) != type(eventsToCompare[i]):
                return False
            if isinstance(self.events[i], BaseEvent):
                break
            if isinstance(self.events[i], RotationEvent):
                if self.events[i].getValue() != eventsToCompare[i].getValue():
                    return False
                if self.events[i].getSum() != eventsToCompare[i].getSum():
                    return False
            if isinstance(self.events[i], ButtonEvent):
                if self.events[i].getValue() != eventsToCompare[i].getValue():
                    return False

        return True

    def getEvents(self):
        return self.events

    def getAssociatedDevice(self):
        return self.associatedDevice
