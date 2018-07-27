from flask import Blueprint, import request

device_handler_api = Blueprint('device_handler_api', __name__)

@device_handler_api.route("/assign/device")
def assignDeviceToMotion(self):
    motionName = request.args.get('motionName')
    deviceName = request.args.get('deviceName')

    motionManager = MotionManager()
    deviceManager = DeviceManager()

    motion = motionManager.getMotion(motionName)
    device = deviceManager.getDevice(deviceName)

    motion.associate(device)
    motionManager.updateMotion(motion)

    return 'True'

@device_handler_api.route("/assign/function")
def assignFunctionToMotion(self):
    motionName = request.args.get('motionName')
    functionName = request.args.get('functionName')

    motionManager = MotionManager()

    motion = motionManager.getMotion(motionName)
    function = getattr(motion.getAssociatedDevice(), functionName)

    motion.assignFunction(function)

    return True
    
