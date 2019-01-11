from speaker_manager import TextSpeaker
from speaker_manager import TTS3

speaker = TextSpeaker()
speaker2 = TTS3()

if __name__ == "__main__":
    print "enter test in main"
    speaker.say("hello")
    print "exit main test"
