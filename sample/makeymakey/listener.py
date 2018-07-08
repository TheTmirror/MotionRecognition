from getch import getch
import threading
import time

import sys
sys.path.insert(0, '/home/pi/Desktop/Updated Project/sample')

from events import TouchEvent, EVENT_TOUCH

class MakeyMakeyListener(threading.Thread):

    def __init__(self):
        threading.Thread.__init__(self)
        self.signals = []
        pass

    def run(self):
        while True:
            key = getch()
