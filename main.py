from MqttClient import MqttClient
from EnergyLogic import EnergyLogic
from speech_processing import SpeechProcessing
import time
import threading
from HardwareManager import ledsMeter, servoMotor, sevenSegmentDigit

houseClient = MqttClient("HouseClientConf.config")  # this starts the thread mqtt
consumption = ledsMeter(addressI2C=0x72, isInConsumption=True, valuePeak=8000)
production = ledsMeter(addressI2C=0x71, isInConsumption=False, valuePeak=8000)
display = sevenSegmentDigit()
servoMotor = servoMotor()
logic = EnergyLogic(houseClient, consumption, production, display, servoMotor)


class DisplayThread(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)

    def run(self):
        while True:
            logic.logic()
            time.sleep(10)
            # logic.otherLogic()


class ChangeModeThread(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)

    def run(self):
        while True:
            logic.changeMode(raw_input("type the mode you want to go to (solar, water, exportation, importation): "))
            time.sleep(10)


t = DisplayThread()
t.start()

u = ChangeModeThread()
u.start()

speechProcessing = SpeechProcessing(logic)  # this start the thread speech processing






