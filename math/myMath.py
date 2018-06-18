# -*- coding: utf-8 -*-

from decimal import Decimal, getcontext
getcontext().prec = 15

class Interpolator:

    def linearValueInterpolation(data, n):
        time = []
        val = []
        for (t, e, v, s) in data:
            time.append(t)
            val.append(v)
            
        return _linearInterpolation(time, val, n)

    def linearSummeInterpolation(data, n):
        time = []
        summe = []
        for (t, e, v, s) in data:
            if s == None:
                raise NameError('Kein Value sollte während einer Interpolation None sein')
            
            time.append(t)
            summe.append(s)
            
        return _linearInterpolation(time, summe, n)

    def _linearInterpolation(time, val, n):
        timeReference = time[0]
        I = (time[len(time) - 1] - timeReference) / Decimal('{}'.format(n - 1))
        D = Decimal('0')
        result = []
        result.append((time[0], val[0]))

        counter = Decimal('1')
        
        for i in range(1, len(time)):
            d = time[i] - time[i - 1]
            sum = D + d
            if sum >= I:
                loopCounter = 0
                while sum >= I:
                    loopCounter = loopCounter + 1
                    newVal = val[i-1] + (((timeReference + counter * I) - time[i - 1]) / d) * (val[i] - val[i-1])
                    #print("New Val calc: {} + (({} * {} - {}) / {}) * ({} - {})".format(
                         #val[i-1], counter, I, time[i-1], d, val[i], val[i-1]))
                    #newVal = val[i-1] + ((I - D) / d) * (val[i] - val[i-1])
                    #print("New Val", float(newVal))
                    result.append((timeReference + (counter * I), newVal))
                    counter = counter + Decimal('1')
                    sum = sum - I
                    #print("Sum - I = ", sum)
                    if sum < I:
                        D = D + d - (loopCounter * I)
                    #print("Calculated")
            else:
                D = D + d

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
