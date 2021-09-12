import pyttsx3
engine = pyttsx3.init()

voices = engine.getProperty('voices')

print("Amount of voices:",len(voices))
print('Rate',engine.getProperty('rate'))
engine.setProperty('rate',150)
for v in voices[:5]:
    print("Voice ",v)
    engine.setProperty('voice', v.id)
    engine.say("Testing the voice",str(v.name))
    engine.runAndWait()