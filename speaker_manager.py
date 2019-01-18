import pyttsx3


# this one use the pyttsx3 package
class TTS3:

    def __init__(self):
        self.engine = pyttsx3.init()
        volume = self.engine.getProperty('volume')
        self.engine.setProperty('volume', volume + 0.75)
        rate = self.engine.getProperty('rate')
        self.engine.setProperty('rate', rate-25)
        voice = self.engine.getProperty('voices')[26]  # the french voice
        self.engine.setProperty('voice', voice.id)

    def say(self, sentence):
        self.engine.say(sentence)
        self.engine.runAndWait()
