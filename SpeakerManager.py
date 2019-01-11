from espeak import espeak


# #=====================================================================
# class textSpeaker
# ----------------------------------------------------------------------
# This class is  used for the text to speech modulation:
# This is a simplified structure to use the espeak API in our case.
# We won't change the settings for each sentences. That's why we
# redefine a class to use simplifier methods of the espeak API.
# ----------------------------------------------------------------------
# It contains 2 methods:
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# __init__(self)
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# say(self, phrase):
# it will transmit the "phrase" of type string in an audio format
# and play the result on the audio port
# #=====================================================================
class textSpeaker:

    def __init__(self):
        espeak.set_voice("french+f5")
        espeak.set_parameter(espeak.Parameter.Wordgap, 1)
        espeak.set_parameter(espeak.Parameter.Rate, 50)
        espeak.set_parameter(espeak.Parameter.Pitch, 50)

    def say(self, phrase):
        espeak.synth(phrase)
