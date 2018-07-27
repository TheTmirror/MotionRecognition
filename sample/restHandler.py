from flask import Blueprint, request

from motionManager import MotionManager
from deviceManager import DeviceManager

device_handler_api = Blueprint('device_handler_api', __name__)

@device_handler_api.route("/assign/device")
def assignDeviceToMotion():
    motionName = request.args.get('motionName')
    deviceName = request.args.get('deviceName')

    motionManager = MotionManager()
    deviceManager = DeviceManager()

    motion = motionManager.getMotion(motionName)
    device = deviceManager.getDevice(deviceName)

    motion.assignDevice(device)
    motionManager.updateMotion(motion)

    return 'True'

@device_handler_api.route("/assign/function")
def assignFunctionToMotion():
    motionName = request.args.get('motionName')
    functionName = request.args.get('functionName')

    motionManager = MotionManager()

    motion = motionManager.getMotion(motionName)
    function = getattr(motion.getAssignedDevice(), functionName)

    motion.assignFunction(function)
    motionManager.updateMotion(motion)

    return 'True'
    
