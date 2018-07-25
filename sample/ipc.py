import threading

class IPCMemory:

    #MotionDetector
    START_LEARNING = 'startLearning'
    START_RECOGNIZING = 'startRecognizing'

    #MotionListener
    RESET_ROTATION_SUM = 'resetRotationSum'
    
    #General
    SHUTDOWN = 'shutdown'

    memory = []
    lock = threading.Lock()

    def __init__(self):
        pass

    def add(self, cmd):
        self.lock.acquire()
        self.memory.append(cmd)
        self.lock.release()

    def get(self, index):
        result = None
        self.lock.acquire()
        result = self.memory[index]
        self.lock.release()
        return result

    def getLast(self):
        return self.get(self.getSize()-1)

    def getSize(self):
        result = None
        self.lock.acquire()
        result = len(self.memory)
        self.lock.release()
        return result

    def clear(self):
        self.lock.acquire()
        self.memory = []
        self.lock.release()
