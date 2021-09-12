import farm_speech as speech
import time
earcons = {"red":3, "green":4, "blue":8, "purple":9, "yellow":10,"robot fail":1,"robot fixed":5}
failure_types = {'row collision':1,'untraversable object':2, 'unrecoverable failure':3}

speech.SpeakText("Here are the earcons:")
for color, sound in earcons.items():
    speech.SpeakText(color)
    time.sleep(1)
    speech.beep(sound)
    time.sleep(2)

speech.SpeakText("Here are the three failure types:")
for ftype, sound in failure_types.items():
    speech.SpeakText(ftype)
    time.sleep(1)
    for i in range(sound):
        speech.beep(1)
    time.sleep(2)