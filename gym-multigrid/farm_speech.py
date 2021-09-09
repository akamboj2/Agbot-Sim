# adopted from https://www.geeksforgeeks.org/python-convert-speech-to-text-and-text-to-speech/
# Python program to translate 
# speech to text and text to speech 

import speech_recognition as sr 
import pyttsx3 
import beepy as bp
import numpy as np
import chime as ch

def beep(sound):
    #Arguments 0==4: 'ding' 1 : 'coin', 2 : 'robot_error', 3 : 'error', 
    # 4 : 'ping', 5 : 'ready', 6 : 'success', 7 : 'wilhelm'
    if sound>7:
        if sound==10:
            ch.theme('material')
            ch.info()
        else:
            ch.theme('chime')
            if sound==9:
                ch.info()
            elif sound==8:
                ch.success()
        
    else:
        bp.beep(sound)

def SpeakText(command): 
	"""Speaks a command"""
	# Initialize the engine 
	engine = pyttsx3.init() 
	engine.say(command) 
	engine.runAndWait() 

def hear_command(robots, args_sound, single_error_sentences, errors_at = None):
    """waits for user to say a certain command and returns that command"""
    r = sr.Recognizer() 
    # Loop infinitely for user to 
    # speak 
    robot_colors = ["red", "green", "blue", "purple", "yellow"]
    #desire_cmd = list(map(lambda x: robot_colors[x], robots.keys()))
    earcons = {"red":3, "green":4, "blue":8, "purple":9, "yellow":10}

    desired_cmd = robots
    if errors_at is not None:
        desired_cmd = errors_at

    
    while(1):	 
        if type(robots) is not str:
            #update desired command to account for newly stopped robots
            new_desired_cmd = list(map(lambda x: robot_colors[x], robots.keys()))
            if desired_cmd!=new_desired_cmd:
                for bot in new_desired_cmd:
                    if bot not in desired_cmd:
                        #SpeakText("Error at "+str(bot))
                        # Play single robot failure (same as in hear_command fucntion)
                        if args_sound=='sound':
                            #beep('error')
                            beep(earcons[bot])
                        elif args_sound=='word':
                            SpeakText("Error at "+str(bot))
                        else: #use "full" here
                            SpeakText(single_error_sentences[np.random.randint(0,len(single_error_sentences)-1)] % str(bot))
            desired_cmd = new_desired_cmd

        print("Desired Command", desired_cmd)

        # #uncomment his to auto return:
        # if type(desired_cmd)==list: 
        #     print("Auto return ",desired_cmd[0])
        #     return desired_cmd[0]
        # else:
        #     print("Auto return ",desired_cmd)
        #     return desired_cmd


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
        except KeyboardInterrupt:
            print('keyboard interrupt while listening, leaving hear_command')
            break
        except:
            print("Other Audio Driver Error") #try reproducing with level 2 saying "reverse and retrying"