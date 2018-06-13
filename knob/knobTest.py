import time
import sys
sys.path.insert(0, '/home/pi/Desktop/Griffin')
from pypowermate import powermate

knob = powermate.Powermate('/dev/input/by-id/usb-Griffin_Technology__Inc._Griffin_PowerMate-event-if00')

counter = 0
while True:
    (timeStamp, eventName, value) = knob.read_event()
    if eventName == powermate.Powermate.EVENT_ROTATE:
        print('Rotation with: ', value)
        counter = counter + value
    elif eventName == powermate.Powermate.EVENT_BUTTON:
        print('Button pressed with: ', value)
        print('Counter: ', counter)
        counter = 0
    else:
        print('Kann dies überhaupt auftreten?')