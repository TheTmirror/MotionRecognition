# -*- coding: utf-8 -*-
import sys
sys.path.insert(0, '/home/pi/Desktop/Updated Project')

from decimal import Decimal, getcontext
getcontext().prec = 15

from events import BaseEvent, RotationEvent, ButtonEvent
from events import EVENT_BASE, EVENT_ROTATE, EVENT_BUTTON

from motion import Motion

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


    def saveMotion(self, motion, path):
        f = open(path, 'w')

        f.write("Device:{};\n".format(motion.getAssociatedDevice()))

        #String must always have form:
        #Time, Event, Value, Sum
        for event in motion.getEvents():
            string = "Time:{};Event:{};".format(event.getTime(), event.getEvent())
            if isinstance(event, RotationEvent):
                string = string + "Value:{};Sum:{};".format(event.getValue(), event.getSum())
            elif isinstance(event, ButtonEvent):
                string = string + "Value:{};Sum:{};".format(event.getValue(), None)
            else:
                raise NameError('Should not happen, just for safty')

            f.write(string + "\n")

        f.close()

    def getMotion(self, path):
        f = open(path, 'r')

        motion = Motion()

        for line in f:
            if line[:len("Device")] == "Device":
                motion.associate(line[len("Device:"):line.find(";")])
                continue
            
            time = line[line.find("Time:")+len("Time:"):line.find(";")]
            time = Decimal(time)
            line = line[line.find(";")+1:]
            event = line[line.find("Event:")+len("Event:"):line.find(";")]
            line = line[line.find(";")+1:]
            value = line[line.find("Value:")+len("Value:"):line.find(";")]
            value = Decimal(value)
            line = line[line.find(";")+1:]
            sum = line[line.find("Sum:")+len("Sum:"):line.find(";")]
            sum = Decimal(sum)
            line = line[line.find(";"):]

            if event == EVENT_BASE:
                event = BaseEvent(time)
            elif event == EVENT_ROTATE:
                event = RotationEvent(time, value, sum)
            elif event == EVENT_BUTTON:
                event = ButtonEvent(time, value)

            motion.addEvent(event)

        print("Länge: ", len(motion.getEvents()))

        return motion     

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
            self._saveData(t, fPiTime, fExTime)
            self._saveData(v, fPiValue, fExValue)
            self._saveData(summe, fPiSumme, fExSumme)
            self._saveData(e, fPiEvent, fExEvent)

        fPiTime.close()
        fPiValue.close()
        fPiSumme.close()
        fPiEvent.close()
        
        fExTime.close()
        fExValue.close()
        fExSumme.close()
        fExEvent.close()

    def saveTimes(self, times):
        return self.saveData(times, self.timePathPiFormat, self.timePathExcelFormat)

    def saveEvents(self, events):
        return self.saveData(events, self.eventPathPiFormat, self.eventPathExcelFormat)

    def saveValues(self, values):
        return self.saveData(values, self.valuePathPiFormat, self.valuePathExcelFormat)

    def saveSummen(self, summen):
        return self.saveData(summen, self.summePathPiFormat, self.summePathExcelFormat)
        
    def saveData(self, data, piPath, exPath = None):
        fPi = open(piPath, 'w')
        fEx = None
        if exPath != None:        
            fEx = open(exPath, 'w')

        for d in data:
            self._saveData(d, fPi, fEx)

        fPi.close()
        if exPath != None:
            fEx.close()

    def _saveData(self, data, fPi, fEx):
        stringPi = "{}\n".format(data)
        fPi.write(stringPi)

        if fEx != None:
            stringEx = stringPi.replace(".", ",")
            fEx.write(stringEx)

    def getAllData(self):
        time = self.getTimes()
        value = self.getValues()
        summen = self.getSummen()
        event = self.getEvents()
        data = []

        for i in range(len(time)):
            data.append((time[i], event[i], value[i], summen[i]))

        return data

    #Returns Array with found data as strings
    def getData(self, path):
        f = open(path, 'r')
        result = []

        for line in f:
            line = line[:len(line)-1]
            result.append(line)

        f.close()
        
        return result
        

    def getTimes(self, path = None):
        if path == None:
            path = self.timePathPiFormat
        result = self.getData(path)
        times = []

        for res in result:
            times.append(Decimal(res))

        return times

    def getValues(self, path = None):
        if path == None:
            path = self.valuePathPiFormat
        result = self.getData(path)
        values = []

        for res in result:
            values.append(Decimal(res))

        return values

    def getSummen(self, path = None):
        if path == None:
            path = self.summePathPiFormat
        result = self.getData(path)
        summen = []

        for res in result:
            summen.append(Decimal(res))

        return summen

    def getEvents(self, path = None):
        if path == None:
            path = self.eventPathPiFormat
        return self.getData(path)

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
