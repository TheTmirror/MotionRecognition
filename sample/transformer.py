import sys
sys.path.insert(0, '/home/pi/Desktop/Updated Project/math')
from myMath import Interpolator, Calculator

from motion import Motion
from events import BaseEvent, RotationEvent, ButtonEvent, TouchEvent
from events import EVENT_BASE, EVENT_ROTATE, EVENT_BUTTON, EVENT_TOUCH

class MotionTransformer:

    def __init__(self):
        self.recordedRotations = []
        self.recordedButtons = []
        self.recordedTouches = []

    def transformMotion(self, signals):
        self.signals = signals
        interpolator = Interpolator()
        n = 64

        startTime = None
        endTime = None
        
        for event in self.signals:
            if startTime == None:
                startTime = event.getTime()
            elif startTime > event.getTime():
                startTime = event.getTime()

            if endTime == None:
                endTime = event.getTime()
            elif endTime < event.getTime():
                endTime = event.getTime()
            
            
            if isinstance(event, RotationEvent):
                self.recordedRotations.append(event)
            elif isinstance(event, ButtonEvent):
                self.recordedButtons.append(event)
            elif isinstance(event, TouchEvent):
                self.recordedTouches.append(event)
            else:
                pass

        if startTime is None or endTime is None:
            raise NotEnoughSignals()

        #Construct Motion
        transformedMotion = Motion()
        transformedMotion.setStartTime(startTime)
        transformedMotion.setEndTime(endTime)

        self.addNeutralValues(startTime, endTime)
        
        #Rotation Part of Motion
        result = interpolator.linearInterpolation(self.recordedRotations, n)

        transformedTime = result[0]
        transformedSum = result[1]

        for i in range(len(transformedTime)):
            event = RotationEvent(transformedTime[i], None, transformedSum[i])
            transformedMotion.addEvent(event)

        print("Rotations: {}".format(len(transformedTime)))

        #Button Part of Motion
        result = interpolator.linearInterpolation(self.recordedButtons, n)

        transformedTime = result[0]
        transformedValue = result[1]
                
        for i in range(len(transformedTime)):
            event = ButtonEvent(transformedTime[i], transformedValue[i])
            transformedMotion.addEvent(event)

        print("Buttons: {}".format(len(transformedTime)))

        #Touch Part of Motion
        result = interpolator.linearInterpolation(self.recordedTouches, n)

        transformedTime = result[0]
        transformedValue = result[1]
                
        for i in range(len(transformedTime)):
            event = TouchEvent(transformedTime[i], None, transformedValue[i])
            transformedMotion.addEvent(event)

        print("Touches: {}".format(len(transformedTime)))

        #Scaling and adjustment
        self.scaleMotion(transformedMotion)
        self.adjustValues(transformedMotion)
        
        return transformedMotion

    #Needed for alignment of time
    def addNeutralValues(self, startTime, endTime):
        from decimal import Decimal, getcontext
        getcontext().prec = 15
        
        #Add startTime and endTime if not present
        #Should be able to workaround this with adapted calculations
        if len(self.recordedRotations) > 0:
            if self.recordedRotations[0].getTime() != startTime:
                newEvent = RotationEvent(startTime, Decimal('0'), Decimal('0'))
                self.recordedRotations.insert(0, newEvent)
            if self.recordedRotations[len(self.recordedRotations)-1].getTime() != endTime:
                lastEvent = self.recordedRotations[len(self.recordedRotations)-1]
                newEvent = RotationEvent(endTime, (Decimal('-1') * lastEvent.getValue()).normalize(), Decimal('0'))
                self.recordedRotations.append(newEvent)
        else:
            newEvent = RotationEvent(startTime, Decimal('0'), Decimal('0'))
            self.recordedRotations.append(newEvent)
            newEvent = RotationEvent(endTime, Decimal('0'), Decimal('0'))
            self.recordedRotations.append(newEvent)

        if len(self.recordedButtons) > 0:
            if self.recordedButtons[0].getTime() != startTime:
                newEvent = ButtonEvent(startTime, Decimal('0'))
                self.recordedButtons.insert(0, newEvent)
            if self.recordedButtons[len(self.recordedButtons)-1].getTime() != endTime:
                newEvent = ButtonEvent(endTime, Decimal('0'))
                self.recordedButtons.append(newEvent)
        else:
            newEvent = ButtonEvent(startTime, Decimal('0'))
            self.recordedButtons.append(newEvent)
            newEvent = ButtonEvent(endTime, Decimal('0'))
            self.recordedButtons.append(newEvent)

        if len(self.recordedTouches) > 0:
            if self.recordedTouches[0].getTime() != startTime:
                newEvent = TouchEvent(startTime, None, Decimal('0'))
                self.recordedTouches.insert(0, newEvent)
            if self.recordedTouches[len(self.recordedTouches)-1].getTime() != endTime:
                newEvent = TouchEvent(endTime, None, Decimal('0'))
                self.recordedTouches.append(newEvent)
        else:
            newEvent = TouchEvent(startTime, None, Decimal('0'))
            self.recordedTouches.append(newEvent)
            newEvent = TouchEvent(endTime, None, Decimal('0'))
            self.recordedTouches.append(newEvent)

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

        #Wenn keine Rotation vorhanden war, dann muss/kann nicht
        #skaliert werden, da eh alle Werte = 0 sind.
        if maxValue == Decimal('0'):
            return
        else:
            for event in motion.getEvents():
                if isinstance(event, RotationEvent):
                    event.sum = event.sum * (Decimal('400') / maxValue)
                    event.sum = event.sum.normalize()

    #Zur Korrektur der Differenz der einzelnen Summen der Rotation
    #Nachdem diese Transformiert wurden
    def adjustValues(self, motion):
        rotationEvents = []
        
        for event in motion.getEvents():
            if isinstance(event, RotationEvent):
                rotationEvents.append(event)

        for i in range(len(rotationEvents)):
            if i == 0:
                rotationEvents[i].value = rotationEvents[i].getSum()
                rotationEvents[i].value = rotationEvents[i].value.normalize()
            else:
                rotationEvents[i].value = rotationEvents[i].getSum() - rotationEvents[i-1].getSum()
                rotationEvents[i].value = rotationEvents[i].value.normalize()

class NotEnoughSignals(Exception):
    pass
