# adopted from https://www.geeksforgeeks.org/python-convert-speech-to-text-and-text-to-speech/
# Python program to translate 
# speech to text and text to speech 

import speech_recognition as sr 
import pyttsx3 
import beepy as bp

def beep(sound):
    #Arguments 1 : 'coin', 2 : 'robot_error', 3 : 'error', 
    # 4 : 'ping', 5 : 'ready', 6 : 'success', 7 : 'wilhelm'
    bp.beep(sound)

def SpeakText(command): 
	"""Speaks a command"""
	# Initialize the engine 
	engine = pyttsx3.init() 
	engine.say(command) 
	engine.runAndWait() 

def hear_command(desired_cmd):
    """waits for user to say a certain command and returns that command"""
    r = sr.Recognizer() 
    # Loop infinitely for user to 
    # speak 

    while(1):	 
        
        # Exception handling to handle 
        # exceptions at the runtime 
        try: 
            
            # use the microphone as source for input. 
            with sr.Microphone() as source2: 
                
                # wait for a second to let the recognizer 
                # adjust the energy threshold based on 
                # the surrounding noise level 
                r.adjust_for_ambient_noise(source2, duration=0.2) 
                
                #listens for the user's input 
                audio2 = r.listen(source2) 
                
                # Using google to recognize audio 
                MyText = r.recognize_google(audio2) 
                MyText = MyText.lower() 

                print("Did you say: "+MyText)
                if type(desired_cmd)==list: #list of strings
                    if MyText in desired_cmd:
                        return MyText
                else: #just a string
                    if MyText==desired_cmd: 
                        return MyText
        except sr.RequestError as e: 
            print("Could not request results; {0}".format(e)) 
            
        except sr.UnknownValueError: 
            print("unknown error occured") 
        except:
            print("Other Audio Driver Error") #try reproducing with level 2 saying "reverse and retrying"