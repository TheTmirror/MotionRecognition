import sys
sys.path.insert(0, '/home/pi/Desktop/Griffin')
from pypowermate import powermate

EVENT_BASE = 'base'
EVENT_ROTATE = powermate.Powermate.EVENT_ROTATE
EVENT_BUTTON = powermate.Powermate.EVENT_BUTTON
EVENT_TOUCH = 'touchEvent'

class BaseEvent:

    def __init__(self, time):
        global EVENT_BASE
        self.time = time
        self.event = EVENT_BASE

    def __repr__(self):
        global EVENT_BASE
        return "Time: {}\nEvent: {}".format(self.time, EVENT_BASE)

    def getTime(self):
        return self.time

    def getEvent(self):
        return self.event

class TouchEvent(BaseEvent):

    def __init__(self, time, location, value):
        global EVENT_TOUCH
        BaseEvent.__init__(self, time)
        self.event = EVENT_TOUCH
        self.location = location
        self.value = value

    def __repr__(self):
        return "Time: {}\nEvent: {}\nLocation: {}\nValue: {}".format(self.time, self.event, self.location, self.value)

    def getValue(self):
        return self.value

    def getLocation(self):
        return self.location

class RotationEvent(BaseEvent):

    def __init__(self, time, value, sum):
        global EVENT_ROTATE
        BaseEvent.__init__(self, time)
        self.event = EVENT_ROTATE
        self.value = value
        self.sum = sum

    def __repr__(self):
        return "Time: {}\nEvent: {}\nValue: {}\nSum: {}".format(self.time, self.event, self.value, self.sum)

    def getValue(self):
        return self.value

    def getSum(self):
        return self.sum

class ButtonEvent(BaseEvent):

    def __init__(self, time, value):
        global EVENT_BUTTON
        BaseEvent.__init__(self, time)
        self.event = EVENT_BUTTON
        self.value = value

    def __repr__(self):
        return "Time: {}\nEvent: {}\nValue: {}".format(self.time, self.event, self.value)

    def getValue(self):
        return self.value

if __name__ == '__main__':
    event = BaseEvent(3)
    print(event)
    event = RotationEvent(4, 5, 6)
    print(event)
    event = ButtonEvent(7, 8)
    print(event)
