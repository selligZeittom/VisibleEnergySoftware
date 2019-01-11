from MqttClient import MqttClient
from EnergyLogic import EnergyLogic
import signal
import time
import threading
from threading import Timer
from HardwareManager import ledsMeter, servoMotor, sevenSegmentDigit

houseClient = MqttClient("HouseClientConf.config")
consumption = ledsMeter(addressI2C=0x72, isInConsumption=True, valuePeak=8000)
production = ledsMeter(addressI2C=0x71, isInConsumption=False, valuePeak=8000)
display = sevenSegmentDigit()
servoMotor = servoMotor()
logic = EnergyLogic(houseClient, consumption, production, display, servoMotor)


class MonTestThread(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)

    def run(self):
        while True:
            time.sleep(10)
            logic.logic()
            # logic.otherLogic()


class MonThreadModeChangement(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)

    def run(self):
        while True:
            logic.changeMode(raw_input("type the mode you want to go to (solar, water, exportation, importation): "))


t = MonTestThread()
t.start()

u = MonThreadModeChangement()
u.start()




