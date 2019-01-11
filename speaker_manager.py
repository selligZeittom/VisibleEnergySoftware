from espeak import espeak
import pyttsx3


# this class uses the espeak package : functional but bad results
class TextSpeaker:

    def __init__(self):
        espeak.set_voice("french+f5")
        espeak.set_parameter(espeak.Parameter.Wordgap, 1)
        espeak.set_parameter(espeak.Parameter.Rate, 50)
        espeak.set_parameter(espeak.Parameter.Pitch, 50)

    def say(self, sentence):
        espeak.synth(sentence)


# this one use the pyttsx3 package
class TTS3:

    def __init__(self):
        engine = pyttsx3.init()
        rate = engine.getProperty('rate')
        engine.setProperty('rate', rate + 50)

    def say(self, sentence):
        engine = pyttsx3.init()
        engine.say(sentence)
        engine.runAndWait()
