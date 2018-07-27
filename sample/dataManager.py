# -*- coding: utf-8 -*-
import sys
sys.path.insert(0, '/home/pi/Desktop/Updated Project')

from decimal import Decimal, getcontext
getcontext().prec = 15

from events import BaseEvent, RotationEvent, ButtonEvent, TouchEvent
from events import EVENT_BASE, EVENT_ROTATE, EVENT_BUTTON, EVENT_TOUCH

from motion import Motion
from deviceManager import DeviceManager

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

        f.write("Name:{};\n".format(motion.getName()))
        if motion.isDeviceAssigned():
            f.write("Device:{};\n".format(motion.getAssignedDevice().getName()))
        else:
            f.write("Device:{};\n".format(None))

        #String must always have form:
        #Time, Event, Location, Value, Sum
        for event in motion.getEvents():
            string = "Time:{};Event:{};".format(event.getTime(), event.getEvent())
            if isinstance(event, RotationEvent):
                string = string + "Location:{};Value:{};Sum:{};".format(None, event.getValue(), event.getSum())
            elif isinstance(event, ButtonEvent):
                string = string + "Location:{};Value:{};Sum:{};".format(None, event.getValue(), None)
            elif isinstance(event, TouchEvent):
                string = string + "Location:{};Value:{};Sum:{};".format(event.getLocation(), event.getValue(), None)
            else:
                raise NameError('Should not happen, just for safty')

            f.write(string + "\n")

        f.close()

    def getMotion(self, path):
        deviceManager = DeviceManager()
        f = open(path, 'r')

        motion = Motion()

        for line in f:
            if line[:len("Name")] == "Name":
                motion.setName(line[len("Name:"):line.find(";")])
                continue
            elif line[:len("Device")] == "Device":
                deviceName = line[len("Device:"):line.find(";")]
                if deviceName == 'None':
                    continue
                device = deviceManager.getDevice(deviceName)
                motion.assignDevice(device)
                continue
            
            time = line[line.find("Time:")+len("Time:"):line.find(";")]
            time = Decimal(time)
            line = line[line.find(";")+1:]
            event = line[line.find("Event:")+len("Event:"):line.find(";")]
            line = line[line.find(";")+1:]
            location = line[line.find("Location:")+len("Location:"):line.find(";")]
            line = line[line.find(";")+1:]
            if location == 'None':
                location = None
            value = line[line.find("Value:")+len("Value:"):line.find(";")]
            if value == 'None':
                value = None
            else:
                value = Decimal(value)
            line = line[line.find(";")+1:]
            sum = line[line.find("Sum:")+len("Sum:"):line.find(";")]
            if sum == 'None':
                sum = None
            else:
                sum = Decimal(sum)
            line = line[line.find(";"):]

            if event == EVENT_BASE:
                event = BaseEvent(time)
            elif event == EVENT_ROTATE:
                event = RotationEvent(time, value, sum)
            elif event == EVENT_BUTTON:
                event = ButtonEvent(time, value)
            elif event == EVENT_TOUCH:
                event = TouchEvent(time, location, value)

            motion.addEvent(event)

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
