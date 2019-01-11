# -*- coding: latin-1 -*-
import snowboydecoder
import sys
import signal
import speech_recognition as sr

interrupted = False

# if the stop word is detected
stop_word_detected = False


def signal_handler(signal, frame):
    global interrupted
    interrupted = True


def interrupt_callback():
    global interrupted
    return interrupted


def interact_with_device(recognizer, microphone):
    # check that recognizer and microphone arguments are appropriate type
    if not isinstance(recognizer, sr.Recognizer):
        raise TypeError("`recognizer` must be `Recognizer` instance")

    if not isinstance(microphone, sr.Microphone):
        raise TypeError("`microphone` must be `Microphone` instance")

    with microphone as source:
        # adjust to the ambient noise
        recognizer.adjust_for_ambient_noise(source, duration=0.5)
        print "let's talk to the device !"

        # set up the response object
        response = {
            "success": True,
            "error": None,
            "transcription": None
        }

        # if there is sth to listen...
        try:
            audio = recognizer.listen(source, timeout=3, phrase_time_limit=1)
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
        print response["error"]
    except sr.UnknownValueError:
        # speech was unintelligible
        response["success"] = False
        response["error"] = "Unable to recognize speech"
        print response["error"]
    return response


def process_result(result):
    text = unicode(result)  # cast into unicode
    text.lower()

    # means that the user wants to stop the interaction with the device
    if text.__contains__("stop"):
        print "[cmd] : stop"
        global stop_word_detected
        stop_word_detected = True
        return True

    # switch mode
    elif text.__contains__("mode") and (text.__contains__("panneau") or text.__contains__("solaire") or text.__contains__("production")):
        print "[cmd switch] : solar panel mode"
        return True
    elif text.__contains__("mode") and text.__contains__("import"):
        print "[cmd switch] : import mode"
        return True
    elif text.__contains__("mode") and text.__contains__("export"):
        print "[cmd switch] : export mode"
        return True
    elif text.__contains__("heure"):
        print "[cmd switch] : time mode"
        return True
    # set an alarm
    elif text.__contains__(u"réveil") or text.__contains__("alarm"):
        print "[cmd set] : set an alarm"
        return True
    # wrong command
    else:
        print "vocal command is not valid... try again ! "
        return False


def start_word_detected():
    print("got the start keyword !")
    # first terminate the start detector
    startDetector.terminate()

    # then start recognizing
    print("now time to start the talk ! ")
    # obtain audio from the microphone
    r = sr.Recognizer()
    m = sr.Microphone()

    while True:
        res = interact_with_device(r, m)
        # if no exception was launched
        if res["error"] is None:
            print(u"You said: {}".format(res["transcription"]))
            processed = process_result(res["transcription"])
            if processed is True or stop_word_detected is True:
                break

    # if we come here : means that interaction is over
    global stop_word_detected
    stop_word_detected = False

    print "back to detecting hotword"
    # start the thread of the detector
    global startDetector
    startDetector = snowboydecoder.HotwordDetector(startModel, sensitivity=0.5)
    startDetector.start(detected_callback=start_word_detected,
                        interrupt_check=interrupt_callback,
                        sleep_time=0.03)


if __name__ == "__main__":

    if len(sys.argv) == 1:
        print("Error: need to specify model name")
        print("Usage: python demo.py your.model")
        sys.exit(-1)

    startModel = sys.argv[1]    # start model, the one that launches the interaction

    # capture SIGINT signal, e.g., Ctrl+C
    signal.signal(signal.SIGINT, signal_handler)

    startDetector = snowboydecoder.HotwordDetector(startModel, sensitivity=0.5)

    # start the thread of the detector
    startDetector.start(detected_callback=start_word_detected,
                        interrupt_check=interrupt_callback,
                        sleep_time=0.03)
    print('Listening... Press Ctrl+C to exit')

