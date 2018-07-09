# -*- coding: utf-8 -*-
#!MUSS NOCH AN EVENT ANGEPASST WERDEN!!!

from decimal import Decimal, getcontext
getcontext().prec = 15

import sys
sys.path.insert(0, '/home/pi/Desktop/Updated Project/sample')
from events import BaseEvent, RotationEvent, ButtonEvent, TouchEvent
from events import EVENT_BASE, EVENT_ROTATE, EVENT_BUTTON, EVENT_TOUCH

from dataManager import DataManager

class RecordingError(Exception):

    def __init__(self, message):
        self.message = message

class Calculator:
    def getMatchingScore(self, m1, m2):
        oddRotation = Decimal('1') - self.getAverageRotationDifference(m1, m2) / Decimal('800')
        oddButton = Decimal('1') - self.getAverageButtonDifference(m1, m2) / Decimal('1')

        odds = oddRotation * oddButton
        odds.normalize()
        return odds

    def getAverageButtonDifference(self, m1, m2):
        buttonEventsM1 = []
        buttonEventsM2 = []

        differences = []

        for event in m1.getEvents():
            if isinstance(event, ButtonEvent):
                buttonEventsM1.append(event)

        for event in m2.getEvents():
            if isinstance(event, ButtonEvent):
                buttonEventsM2.append(event)

        if len(buttonEventsM1) != len(buttonEventsM2):
            print("b1", len(buttonEventsM1))
            print("b2", len(buttonEventsM2))
            raise NameError('Es gab einen Fehler in der Button Länge')

        length = len(buttonEventsM1)
        
        #Falls der Button nie Benutzt wurde
        if length == 0:
            print('Achtung der Button wurde nie gedrückt')
            return Decimal('0')

        for i in range(length):
            x = abs(buttonEventsM1[i].getValue() - buttonEventsM2[i].getValue())
            x = x.normalize()
            differences.append(x)

        sum = Decimal('0')
        for difference in differences:
            sum = sum + difference
            sum = sum.normalize()

        x = sum / Decimal(len(buttonEventsM1))
        x = x.normalize()
        return x

    def getAverageRotationDifference(self, m1, m2):
        rotationEventsM1 = []
        rotationEventsM2 = []

        differences = []

        for event in m1.getEvents():
            if isinstance(event, RotationEvent):
                rotationEventsM1.append(event)

        for event in m2.getEvents():
            if isinstance(event, RotationEvent):
                rotationEventsM2.append(event)

        if len(rotationEventsM1) != len(rotationEventsM2):
            raise NameError('Es gab einen Fehler in der Rotation Länge')

        length = len(rotationEventsM1)

        for i in range(length):
            x = abs(rotationEventsM1[i].getSum() - rotationEventsM2[i].getSum())
            x = x.normalize()
            differences.append(x)

        sum = Decimal('0')
        for difference in differences:
            sum = sum + difference
            sum = sum.normalize()

        x = sum / Decimal(len(rotationEventsM1))
        x = x.normalize()
        return x

class Interpolator:

    def linearInterpolation(self, events, n):
        if isinstance(events[0], RotationEvent):
            return self.linearSumInterpolation(events, n)
        elif isinstance(events[0], ButtonEvent):
            return self.linearButtonInterpolation(events, n)
        elif isinstance(events[0], TouchEvent):
            return self.linearTouchInterpolation(events, n)
        elif isinstance(events[0], BaseEvent):
            raise NameError("Es ist nicht möglich übers BaseEvent zu interpolieren")

    def linearTouchInterpolation(self, events, n):
        time = []
        val = []
        for event in events:
            if event.getValue() == None:
                raise NameError('Kein Value vorhanden')

            time.append(event.getTime())
            val.append(event.getValue())

        return self._linearInterpolation(time, val, n)
        
    def linearButtonInterpolation(self, events, n):
        time = []
        val = []
        for event in events:
            if event.getValue() == None:
                raise NameError('Kein Value vorhanden')

            time.append(event.getTime())
            val.append(event.getValue())

        return self._linearInterpolation(time, val, n)

    def linearSumInterpolation(self, events, n):
        time = []
        sum = []
        for event in events:
            if event.getSum() == None:
                raise NameError('Kein Value sollte während einer Interpolation None sein')
            
            time.append(event.getTime())
            sum.append(event.getSum())
            
        return self._linearInterpolation(time, sum, n)

    #Bug: Es kann passieren dass die Startzeit = der Endzeit ist.
    #Dies ist der Fall wenn es zum Beispiel nur ein Touch Event gibt.
    #Dann kann der Code nicht arbeiten. Was passiert dann?
    def _linearInterpolation(self, time, val, n):
        timeReference = time[0]
        I = (time[len(time) - 1] - timeReference) / Decimal('{}'.format(n - 1))
        I = I.normalize()
        D = Decimal('0')
        interpolatedTime = []
        interpolatedValue = []

        interpolatedTime.append(time[0])
        interpolatedValue.append(val[0])

        counter = Decimal('1')
        
        for i in range(1, len(time)):
            d = time[i] - time[i - 1]
            d = d.normalize()
            sum = D + d
            sum = sum.normalize()
            if sum >= I:
                loopCounter = 0
                while sum >= I:
                    loopCounter = loopCounter + 1
                    newVal = val[i-1] + (((timeReference + counter * I) - time[i - 1]) / d) * (val[i] - val[i-1])
                    newVal = newVal.normalize()
                    interpolatedTime.append(timeReference + (counter * I))
                    interpolatedValue.append(newVal)
                    counter = counter + Decimal('1')
                    sum = sum - I
                    su = sum.normalize()
                    if sum < I:
                        D = D + d - (loopCounter * I)
                        D = D.normalize()
            else:
                D = D + d
                D = D.normalize()

        result = []
        result.append(interpolatedTime)
        result.append(interpolatedValue)

        #Manchmal geht aufgrund von Rundungen
        #der letzte Eintrag verloren. Dieser wird
        #hier künstlich wieder hinzugefügt
        if len(result[0]) != 64:
            if len(result[0]) == 63:
                result[0].append(time[len(time)-1])
                result[1].append(val[len(val)-1])
                print('Werte wurden nachkorrigiert')
            else:
                raise NameError("Ein unerwarteter Fehler ist aufgetreten")
        
        return result

class NotEnoughEntriesException(Exception):

    def __init__(self, message):
        self.message = message

if __name__ == '__main__':
    from motion import Motion
    n = 9
    
    #print(myLinearInterpolation(
    #    [(0, 1), (1.5, 2), (1.7, 3), (3, 4), (3.1, 5),
    #     (4, 6), (5, 7), (6, 8), (7, 9), (10, 10),
    #     (11, 11), (13, 12), (14, 13), (15, 14), (16, 15),
    #     (17, 16), (18, 17), (19, 18), (19.5, 19), (20, 20)
    #     ], n))

    #print(myLinearInterpolation(
    #    [(0, 1), (1.5, 2), (1.7, 3), (3, 4), (3.1, 5),
    #     (4, 6), (5, 7), (6, 8), (6.5, 9), (11, 10),
    #     (11.5, 11), (13, 12), (14, 13), (15, 14), (16, 15),
    #     (17, 16), (18, 17), (19, 18), (19.5, 19), (20, 20)
    #     ], n))

    #print(myLinearInterpolation(
    #    [(0, 1), (6, 3), (13, 8), (20, 12)], n))

    r1 = RotationEvent(1, 1, 1)
    r2 = RotationEvent(2, 2, 3)
    r3 = RotationEvent(3, 1, 4)
    r4 = RotationEvent(4, 1, 5)
    r5 = RotationEvent(5, -2, 3)

    r6 = RotationEvent(1, 1, 1)
    r7 = RotationEvent(2, -1, 0)
    r8 = RotationEvent(3, 2, 2)
    r9 = RotationEvent(4, 4, 6)
    r10 = RotationEvent(5, -2, 3)

    m1 = Motion()
    m2 = Motion()

    m1.addEvent(r1)
    m1.addEvent(r2)
    m1.addEvent(r3)
    m1.addEvent(r4)
    m1.addEvent(r5)
    
    m2.addEvent(r6)
    m2.addEvent(r7)
    m2.addEvent(r8)
    m2.addEvent(r9)
    m2.addEvent(r10)

    c = Calculator()
    print(c.getMotionDifference(m1, m2))
