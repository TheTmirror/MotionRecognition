# -*- coding: utf-8 -*-
#!MUSS NOCH AN EVENT ANGEPASST WERDEN!!!

from decimal import Decimal, getcontext
getcontext().prec = 15

import sys
sys.path.insert(0, '/home/pi/Desktop/Updated Project/sample')
from events import BaseEvent, RotationEvent, ButtonEvent
from events import EVENT_BASE, EVENT_ROTATE, EVENT_BUTTON

class Interpolator:

    def linearInterpolation(self, events, n):
        if isinstance(events[0], RotationEvent):
            return self.linearSumInterpolation(events, n)
        elif isinstance(events[0], ButtonEvent):
            pass
        elif isinstance(events[0], BaseEvent):
            raise NameError("Es ist nicht möglich übers BaseEvent zu interpolieren")
        
    def linearValueInterpolation(self, data, n):
        time = []
        val = []
        for (t, e, v, s) in data:
            time.append(t)
            val.append(v)
            
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

    def _linearInterpolation(self, time, val, n):
        timeReference = time[0]
        I = (time[len(time) - 1] - timeReference) / Decimal('{}'.format(n - 1))
        D = Decimal('0')
        interpolatedTime = []
        interpolatedValue = []

        interpolatedTime.append(time[0])
        interpolatedValue.append(val[0])

        counter = Decimal('1')
        
        for i in range(1, len(time)):
            d = time[i] - time[i - 1]
            sum = D + d
            if sum >= I:
                loopCounter = 0
                while sum >= I:
                    loopCounter = loopCounter + 1
                    newVal = val[i-1] + (((timeReference + counter * I) - time[i - 1]) / d) * (val[i] - val[i-1])
                    interpolatedTime.append(timeReference + (counter * I))
                    interpolatedValue.append(newVal)
                    counter = counter + Decimal('1')
                    sum = sum - I
                    if sum < I:
                        D = D + d - (loopCounter * I)
            else:
                D = D + d

        result = []
        result.append(interpolatedTime)
        result.append(interpolatedValue)
        return result

if __name__ == '__main__':
    n = 9
    
    print(myLinearInterpolation(
        [(0, 1), (1.5, 2), (1.7, 3), (3, 4), (3.1, 5),
         (4, 6), (5, 7), (6, 8), (7, 9), (10, 10),
         (11, 11), (13, 12), (14, 13), (15, 14), (16, 15),
         (17, 16), (18, 17), (19, 18), (19.5, 19), (20, 20)
         ], n))

    print(myLinearInterpolation(
        [(0, 1), (1.5, 2), (1.7, 3), (3, 4), (3.1, 5),
         (4, 6), (5, 7), (6, 8), (6.5, 9), (11, 10),
         (11.5, 11), (13, 12), (14, 13), (15, 14), (16, 15),
         (17, 16), (18, 17), (19, 18), (19.5, 19), (20, 20)
         ], n))

    print(myLinearInterpolation(
        [(0, 1), (6, 3), (13, 8), (20, 12)], n))
