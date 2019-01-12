# -*- coding: latin-1 -*-
import snowboydecoder
import sys
import signal
import speech_recognition as sr
from speaker_manager import TTS3


class SpeechProcessing:

    def __init__(self, logic):
        self._logic = logic     # got the logic instance from main
        self.speaker = TTS3()
        self.stop_word_detected = False    # if the stop word is detected
        self.interrupted = False
        # check that there is a parameter for the recognition model
        if len(sys.argv) == 1:
            print("Error: need to specify model name")
            sys.exit(-1)
        self.startModel = sys.argv[1]    # start model, the one that launches the interaction
        # capture SIGINT signal, e.g., Ctrl+C
        signal.signal(signal.SIGINT, self.signal_handler)
        self.startDetector = snowboydecoder.HotwordDetector(self.startModel, sensitivity=0.5)
        # start the thread of the detector
        self.startDetector.start(detected_callback=self.start_word_detected,
                                 interrupt_check=self.interrupt_callback,
                                 sleep_time=0.03)
        print('Listening... Press Ctrl+C to exit')

    def signal_handler(self, signal, frame):
        self.interrupted = True

    def interrupt_callback(self):
        return self.interrupted

    def interact_with_device(self, recognizer, microphone):
        # check that recognizer and microphone arguments are appropriate type
        if not isinstance(recognizer, sr.Recognizer):
            raise TypeError("`recognizer` must be `Recognizer` instance")

        if not isinstance(microphone, sr.Microphone):
            raise TypeError("`microphone` must be `Microphone` instance")

        with microphone as source:
            # adjust to the ambient noise
            recognizer.adjust_for_ambient_noise(source, duration=0.1)
            print("let's talk to the device !")

            # set up the response object
            response = {
                "success": True,
                "error": None,
                "transcription": None
            }

            # if there is sth to listen...
            try:
                audio = recognizer.listen(source, timeout=5, phrase_time_limit=2)
            except sr.WaitTimeoutError:
                response["error"] = "Timeout"
                return response

        # fill the enum with the results
        try:
            response["success"] = True
            response["transcription"] = recognizer.recognize_google(audio, language="fr-CH")
        except sr.RequestError:
            # API was unreachable or unresponsive
            response["success"] = False
            response["error"] = "API unavailable"
            print(response["error"])
        except sr.UnknownValueError:
            # speech was unintelligible
            response["success"] = False
            response["error"] = "Unable to recognize speech"
            print(response["error"])
        return response


    def process_result(self, result):
        text = unicode(result)  # cast into unicode
        text.lower()

        # means that the user wants to stop the interaction with the device
        if text.__contains__("stop"):
            print("[cmd] : stop")
            self.speaker.say("au revoir")
            self.stop_word_detected = True
            return True

        # switch mode
        elif text.__contains__("mode") and (text.__contains__("panneau") or text.__contains__("solaire") or text.__contains__("production")):
            self._logic.changeMode("solar")
            self.speaker.say("mode panneau solaires")
            print("[cmd switch] : solar panel mode")
            return True
        elif text.__contains__("mode") and text.__contains__("import"):
            self._logic.changeMode("importation")
            self.speaker.say("mode importation")
            print("[cmd switch] : import mode")
            return True
        elif text.__contains__("mode") and text.__contains__("export"):
            self._logic.changeMode("exportation")
            self.speaker.say("mode exportation")
            print("[cmd switch] : export mode")
            return True
        elif text.__contains__("heure"):
            print("[cmd switch] : time mode")
            return True
        # wrong command
        else:
            self.speaker.say("je ne connais pas cette commande...")
            print("vocal command is not valid... try again ! ")
            return False

    def start_word_detected(self):
        self.speaker.say(u"oui j'écoute")
        print("got the start keyword !")
        # first terminate the start detector
        self.startDetector.terminate()

        # then start recognizing
        print("now time to start the talk ! ")
        # obtain audio from the microphone
        r = sr.Recognizer()
        m = sr.Microphone()

        while True:
            res = self.interact_with_device(r, m)
            # if no exception was launched
            if res["error"] is None:
                print(u"You said: {}".format(res["transcription"]))
                processed = self.process_result(res["transcription"])
                if processed is True or self.stop_word_detected is True:
                    break

        # if we come here : means that interaction is over
        self.stop_word_detected = False

        print("back to detecting hotword")
        # start the thread of the detector
        self.startDetector = snowboydecoder.HotwordDetector(self.startModel, sensitivity=0.5)
        self.startDetector.start(detected_callback=self.start_word_detected,
                                 interrupt_check=self.interrupt_callback,
                                 sleep_time=0.03)


