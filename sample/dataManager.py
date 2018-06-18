import sys
sys.path.insert(0, '/home/pi/Desktop/Updated Project')

from decimal import Decimal, getcontext
getcontext().prec = 15

class DataManager:

    def __init__(self):
        import os
        
        self.timePathPiFormat = '/home/pi/Desktop/Updated Project/logs/pi/times.txt'
        self.valuePathPiFormat = '/home/pi/Desktop/Updated Project/logs/pi/values.txt'
        self.summePathPiFormat = '/home/pi/Desktop/Updated Project/logs/pi/summe.txt'
        self.eventPathPiFormat = '/home/pi/Desktop/Updated Project/logs/pi/events.txt'

        self.timePathExcelFormat = '/home/pi/Desktop/Updated Project/logs/excel/times.txt'
        self.valuePathExcelFormat = '/home/pi/Desktop/Updated Project/logs/excel/values.txt'
        self.summePathExcelFormat = '/home/pi/Desktop/Updated Project/logs/excel/summe.txt'
        self.eventPathExcelFormat = '/home/pi/Desktop/Updated Project/logs/excel/events.txt'

        if not os.path.exists(os.path.dirname(self.timePathPiFormat)):
            os.makedirs(os.path.dirname(self.timePathPiFormat))

        if not os.path.exists(os.path.dirname(self.valuePathPiFormat)):
            os.makedirs(os.path.dirname(self.valuePathPiFormat))

        if not os.path.exists(os.path.dirname(self.summePathPiFormat)):
            os.makedirs(os.path.dirname(self.summePathPiFormat))

        if not os.path.exists(os.path.dirname(self.eventPathPiFormat)):
            os.makedirs(os.path.dirname(self.eventPathPiFormat))

        if not os.path.exists(os.path.dirname(self.timePathExcelFormat)):
            os.makedirs(os.path.dirname(self.timePathExcelFormat))

        if not os.path.exists(os.path.dirname(self.valuePathExcelFormat)):
            os.makedirs(os.path.dirname(self.valuePathExcelFormat))

        if not os.path.exists(os.path.dirname(self.summePathExcelFormat)):
            os.makedirs(os.path.dirname(self.summePathExcelFormat))

        if not os.path.exists(os.path.dirname(self.eventPathExcelFormat)):
            os.makedirs(os.path.dirname(self.eventPathExcelFormat))


    def saveAllData(self, data):
        fPiTime = open(self.timePathPiFormat, 'w')
        fPiValue = open(self.valuePathPiFormat, 'w')
        fPiSumme = open(self.summePathPiFormat, 'w')
        fPiEvent = open(self.eventPathPiFormat, 'w')
        
        fExTime = open(self.timePathExcelFormat, 'w')
        fExValue = open(self.valuePathExcelFormat, 'w')
        fExSumme = open(self.summePathExcelFormat, 'w')
        fExEvent = open(self.eventPathExcelFormat, 'w')

        for (t, e, v, summe) in data:
            self.__saveTimes(t, fPiTime, fExTime)
            self.__saveValues(v, fPiValue, fExValue)
            self.__saveSummen(summe, fPiSumme, fExSumme)
            self.__saveEvents(e, fPiEvent, fExEvent)

        fPiTime.close()
        fPiValue.close()
        fPiSumme.close()
        fPiEvent.close()
        fExTime.close()
        fExValue.close()
        fExSumme.close()
        fExEvent.close()

    def saveTimes(self, time):
        self._saveTimes(time, self.timePathPiFormat, self.timePathExcelFormat)
    
    def _saveTimes(self, time, piPath, exPath):
        fPi = open(piPath, 'w')
        fEx = open(exPath, 'w')

        for t in time:
            self.__saveTimes(t, fPi, fEx)

        fPi.close()
        fEx.close()

    def __saveTimes(self, time, fPi, fEx):
        tStringPi = "{}\n".format(time)
        tStringEx = tStringPi.replace(".", ",")
        fPi.write(tStringPi)
        fEx.write(tStringEx)

    def saveValues(self, val):
        self._saveValues(val, self.valuePathPiFormat, self.valuePathExcelFormat)
        
    def _saveValues(self, val, piPath, exPath):
        fPi = open(piPath, 'w')
        fEx = open(exPath, 'w')

        for v in val:
            self.__saveValues(v, fPi, fEx)

        fPi.close()
        fEx.close()

    def __saveValues(self, val, fPi, fEx):
        vStringPi = "{}\n".format(val)
        vStringEx = vStringPi.replace(".", ",")
        fPi.write(vStringPi)
        fEx.write(vStringEx)

    def saveSummen(self, summe):
        self._saveSummen(summe, self.summePathPiFormat, self.summePathExcelFormat)

    def _saveSummen(self, summe, piPath, exPath):
        fPi = open(piPath, 'w')
        fEx = open(exPath, 'w')

        for s in summe:
            self.__saveSummen(s, fPi, fEx)

        fPi.close()
        fEx.close()

    def __saveSummen(self, summe, fPi, fEx):
        sStringPi = "{}\n".format(summe)
        sStringEx = sStringPi.replace(".", ",")
        fPi.write(sStringPi)
        fEx.write(sStringEx)

    def saveEvents(self, event):
        self._saveEvents(event, self.eventPathPiFormat, self.eventPathExcelFormat)

    def _saveEvents(self, event, piPath, exPath):
        fPi = open(piPath, 'w')
        fEx = open(exPath, 'w')

        for e in event:
            self.__saveEvents(e, fPi, fEx)

        fPi.close()
        fEx.close()

    def __saveEvents(self, event, fPi, fEx):
        eString = "{}\n".format(event)
        fPi.write(eString)
        fEx.write(eString)

    def getAllData(self):
        time = self.getTimes()
        value = self.getValues()
        summen = self.getSummen()
        event = self.getEvents()
        data = []

        for i in range(len(time)):
            data.append((time[i], event[i], value[i], summen[i]))

        return data

    def getTimes(self):
        fPi = open(self.timePathPiFormat, 'r')
        time = []
        
        for line in fPi:
            line = line[:len(line) - 1]
            time.append(Decimal(line))

        fPi.close()
        
        return time

    def getValues(self):
        fPi = open(self.valuePathPiFormat, 'r')
        value = []
        
        for line in fPi:
            line = line[:len(line) - 1]
            value.append(Decimal(line))

        fPi.close()
        
        return value

    def getSummen(self):
        fPi = open(self.summePathPiFormat, 'r')
        summen = []
        
        for line in fPi:
            line = line[:len(line) - 1]
            summen.append(Decimal(line))

        fPi.close()
        
        return summen

    def getEvents(self):
        fPi = open(self.eventPathPiFormat, 'r')
        event = []
        
        for line in fPi:
            line = line[:len(line) - 1]
            event.append(line)

        fPi.close()
        
        return event

if __name__ == '__main__':
    dm = DataManager()

    times = [0, 1.5, 1.7, 3, 3.1, 4, 5, 6, 6.5, 11, 11.5, 13, 14, 15, 16,
             17, 18, 19, 19.5, 20]
    values = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17,
              18, 19, 20]

    summe = 0
    summen = []
    for val in values:
        summe = summe + val
        summen.append(summe)

    events = ['rotate', 'rotate', 'rotate', 'rotate', 'rotate', 'rotate',
              'rotate', 'rotate', 'rotate', 'rotate', 'rotate', 'rotate',
              'rotate', 'rotate', 'rotate', 'rotate', 'rotate', 'rotate',
              'rotate', 'rotate']

    dm.saveTimes(times)
    dm.saveValues(values)
    dm.saveSummen(summen)
    dm.saveEvents(events)

    timesCheck = dm.getTimes()
    valuesCheck = dm.getValues()
    summenCheck = dm.getSummen()
    eventsCheck = dm.getEvents()

    for i in range(len(times)):
        if Decimal('{}'.format(times[i])) != timesCheck[i]:
            raise NameError('Time wurde nicht richtig gespeichert')
        if Decimal('{}'.format(values[i])) != valuesCheck[i]:
            raise NameError('Value wurde nicht richtig gespeichert')
        if Decimal('{}'.format(summen[i])) != summenCheck[i]:
            raise NameError('Summe wurde nicht richtig gespeichert')
        if events[i] != eventsCheck[i]:
            raise NameError('Event wurde nicht richtig gespeichert')

    print('Single Check ist okay')

    data = []

    for i in range(len(times)):
        t = times[i]
        v = values[i]
        s = summen[i]
        e = events[i]

        data.append((t, e, v, s))
    
    dm.saveAllData(data)

    dataCheck = dm.getAllData()

    for i in range(len(data)):
        (t, e, v, s) = data[i]
        (tc, ec, vc, sc) = dataCheck[i]

        if Decimal('{}'.format(t)) != tc:
            raise NameError('Time wurde nicht richtig gespeichert')
        if Decimal('{}'.format(v)) != vc:
            raise NameError('Value wurde nicht richtig gespeichert')
        if Decimal('{}'.format(s)) != sc:
            raise NameError('Summe wurde nicht richtig gespeichert')
        if e != ec:
            raise NameError('Event wurde nicht richtig gespeichert')


    print('Mutli Check ist okay')
