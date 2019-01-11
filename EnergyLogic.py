from SpeakerManager import textSpeaker


class EnergyLogic:

    def __init__(self, mqttClient, led1, led2, display, servoMotor):
        self._client = mqttClient
        self._led1 = led1         #consumption led
        self._led2 = led2          #prodution led
        self._display = display
        self._servo = servoMotor
        self._TTS = textSpeaker()
        self._mode = "exportation"

    def logic(self):
        if self._mode.find("solar") != -1:
            self._led1.calcNbLedOn(self._client.getPM2())
            self._led2.calcNbLedOn(self._client.getPM3())
            self._display.displayString(str(int(self._client.getPM3())))
            dif = self._client.getPM2() - self._client.getPM3()
            newangle = (dif*20)/self._client.getMaxValue()
            self._servo.changeAngle(newangle)

        if self._mode.find("water") != -1:
            self._led1.calcNbLedOn(self._client.getPM2())
            self._led2.calcNbLedOn(self._client.getPM3())
            self._display.displayString(str(int(self._client.getPM2())))
            dif = self._client.getPM2() - self._client.getPM3()
            newangle = (dif * 20) / self._client.getMaxValue()
            self._servo.changeAngle(newangle)

        if self._mode.find("exportation") != -1:
            self._led1.calcNbLedOn(self._client.getExportPower())
            self._led2.calcNbLedOn(self._client.getImportPower())
            self._display.displayString(str(int(self._client.getExportPower())))
            dif = self._client.getImportPower() - self._client.getExportPower()
            newangle = (dif * 20) / self._client.getMaxValue()
            self._servo.changeAngle(newangle)

        if self._mode.find("importation") != -1:
            self._led1.calcNbLedOn(self._client.getExportPower())
            self._led2.calcNbLedOn(self._client.getImportPower())
            self._display.displayString(str(int(self._client.getImportPower())))
            dif = self._client.getImportPower() - self._client.getExportPower()
            newangle = (dif * 20) / self._client.getMaxValue()
            self._servo.changeAngle(newangle)

    def otherLogic(self):
        if self._client.getExportPower() > 2000:
            self._TTS.say("Penser a allumer une machine a laver")

        if self._client.getImportPower() > 1000:
            self._TTS.say("Penser a eteindre la lumiere")

    def changeMode(self, mode):
        self._TTS.say(str(mode))
        self._mode = mode

    def getMode(self):
        return self._mode
