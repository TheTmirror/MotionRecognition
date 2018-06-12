class PhilipsHueLightBulb:
    
    def __init__(self):
        self.brightness = 0
        
    def increaseBrightness(self, value = 5):
        if (self.brightness + value) <= 255:
            self.brightness = self.brightness + value
        else:
            self.brightness = 255
        
    def reduceBrightness(self, value = 5):
        if (self.brightness - value) >= 0:
            self.brightness = self.brightness - value
        else:
            self.brightness = 0
            
    def getBrightness(self):
        return self.brightness