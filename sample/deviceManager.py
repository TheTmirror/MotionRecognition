# -*- coding: utf-8 -*-
class DeviceManager:

    __devices = dict()

    def __init__(self):
        pass

    #Ggf. automatisiert möglich?
    def initDevices(self):
        #Hier alle Devices intitialisieren
        device = PhillipsHueLightBulb()
        device.connect()
        self.__devices[device.getName()] = device

        device = Door()
        device.connect()
        self.__devices[device.getName()] = device

    def getAllDevices(self):
        return self.__devices

    def getDevice(self, key):
        return self.__devices[key]

class Device:

    def __init__(self, name):
        self.setName(name)

    def setName(self, name):
        self.name = name

    def getName(self):
        return self.name

class PhillipsHueLightBulb(Device):

    def __init__(self):
        Device.__init__(self, type(self).__name__)
        self.setStatus('off')
        self.connectioNEstablished = False

    def getStatus(self):
        return self.status

    def setStatus(self, status):
        self.status = status

    def switch(self):
        if self.getStatus() == 'off':
            self.setStatus('on')
        else:
            self.setStauts('off')

    def isConnected(self):
        return self.connectionEstablished

    def connect(self):
        self.connectionEstablished = True

    def disconnect(self):
        self.connectionEstablished = False

class Door(Device):

    def __init__(self):
        Device.__init__(self, type(self).__name__)
        self.setStatus('closed')
        self.connectionEstablished = False

    def getStatus(self):
        return self.status

    def setStatus(self, status):
        self.status = status

    def open(self):
        self.setStatus('open')

    def close(self):
        self.setStatus('closed')

    def isConnected(self):
        return self.connectionEstablished

    def connect(self):
        self.connectionEstablished = True

    def disconnect(self):
        self.connectionEstablished = False   
