import speech_recognition as sr

def audio_detect() :
    r = sr.Recognizer()
    mic = sr.Microphone()