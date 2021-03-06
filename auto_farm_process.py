"""
Reminder to self on how to run:
open anaconda
activate speech
cd to directory
python auto_farm_process.py -l 1 -s word
"""

import gym
import time
from gym.envs.registration import register
import numpy as np
import farm_speech as speech
from functools import reduce
import argparse

#from multiprocessing import Process
import multiprocessing as mp

from tkinter import * 
import sys

import easygui
 
farm_size = 45 #also must change in farm_env.py!
DEBUG = False

#robots = {} #holds key:val robot_id:[failure_num, is_fixed]
#any_fixed = 0
    
def run(robots, any_fixed, listen_text):
    # app = Tk() 
    # app.geometry('300x200')
    # app.title("Basic Status Bar")

    # statusbar = Label(app, text="on the way…", bd=1, relief=tk.SUNKEN, anchor=tk.W)
    #print("In process!")
    error_names = ["Row Collision","Untraversable Object", "Unrecoverable Failure"]
    error_fixes = ["reverse and retry", "navigate around", "sending human"]
    robot_colors = ["red", "green", "blue", "purple", "yellow"]
    single_error_sentences = ["The %s robot is facing an error", "An error just occurred at the %s robot",
                        "The %s robot has failed", "The %s robot is stuck", "Assistance is needed with the %s robot",
                        "A failure occurred at the %s robot","The %s robot needs help", "There is a problem with the %s robot",
                        " The %s robot needs assistance", "The % rrobot has encountered an obstacle", "An issue has arisen at the %s robot"]
    multi_error_sentences = ["There are errors at the following robots: ", "An error has occurred at these robots: ", 
                        "These are the robots that have failed: ", "The robots that are stuck are: ", "Assistance is needed with each of these robots:",
                        "Failures have occurred at each of these robots:","These robots still need to be addressed:", "There are problems with these robots:",
                        "Here is a list of the failed robots:", "These robots are still facing an obstacle", "The remaining robots with issues to be resolved are: "]
    robot_fixed_sentences = ["The %s robot has been fixed", "The %s robot is now functioning again", "The %s robot's error has been solved!","The %s robot's error has been resolved", "The %s robot is fully functioning now"]
    failure_type_sentences = ["There is a %s at the %s robot!", "The error is %s at the %s robot!"] #TODO
    #earcons = {"red":3, "green":4, "blue":8, "purple":9, "yellow":10,"robot_fail":1,"robot_fixed":5}
    earcons = {"red":"red_siren.wav","green":"green_leaves.wav","blue":"blue_water.wav","yellow":"yellow_taxi.wav", "purple":"purple_violin.wav","robot_fail":1,"robot_fixed":5}

    while True:
    #    print("in speech robots:_run",robots,any_fixed)
        #if something in dictionary and all robots are not fixed (is_fixed==0), then
        if robots and not any_fixed.value:#not reduce((lambda x,y: x or y),np.append(np.array(list(robots.values()))[:,1],0)): 
            #sys.stdout.flush()
            
            errors_at = list(map(lambda x: robot_colors[x], robots.keys()))

            #print("Error at robots"+str(errors_at))
            #Play Robot Failure Sound (single or multi)
            if len(errors_at)==1: # Play single robot failure (same as in hear_command fucntion)
                if args.sound=='sound':
                    speech.beep(earcons[errors_at[0]])
                elif args.sound=='word':
                    speech.SpeakText("Error at "+str(errors_at))
                elif args.sound=='full': #use "full" here
                    speech.SpeakText(single_error_sentences[np.random.randint(0,len(single_error_sentences)-1)] % str(errors_at))
            else: # Play multi robot failure 
                if args.sound=='sound':
                    for err_robot in errors_at:
                        speech.beep(earcons[err_robot])
                elif args.sound=='word':
                    speech.SpeakText("Errors at "+str(errors_at))
                elif args.sound=='full': #use "full" here
                    speech.SpeakText(multi_error_sentences[np.random.randint(0,len(multi_error_sentences)-1)]+str(errors_at))
                    speech.SpeakText("Which robot would you like to fix?")

            #print("right before forloop",robots)
           # callbacks = [callback1,callback2,callback3]
            
            if args.interface=='gui':
                robot_col = easygui.buttonbox("Error at robots: "+str(errors_at)+"\n what robot would you like to fix? ", 'Fix Robot', errors_at)
            else:
               # speech.SpeakText("Error at robots: "+str(errors_at)+"\n what robot would you like to fix?")
                #robot_col = speech.hear_command(errors_at)
                robot_col = speech.hear_command(robots, args.sound, single_error_sentences, errors_at,listen_text)

            if robot_col is not None:
                robot_num = robot_colors.index(robot_col)
                # print("robot stuff:", robot_num, robot_col, errors_at)
                error = robots[robot_num][0]
                #Play Failure Type sound
                if args.sound=='sound':
                    for i in range(error+1):
                        speech.beep(earcons['robot_fail'])
                elif args.sound=='word':
                    speech.SpeakText(str(error_names[error])) #+" at robot "+str(robot_num))
                elif args.sound=='full':
                    speech.SpeakText(failure_type_sentences[np.random.randint(0,len(failure_type_sentences)-1)] % (str(error_names[error]),str(robot_colors[robot_num])))#"There is a " + str(error_names[error])+" at the "+str(robot_colors[robot_num])+" robot!")
                
                if DEBUG: print("Fixing error {}:".format(error_names[error]))
                _ = speech.hear_command(error_fixes[error], args.sound, single_error_sentences,listen_text=listen_text)

                #Play Robot Fixed sound
                if args.sound=='sound':
                    speech.beep(earcons['robot_fixed'])
                elif args.sound=='word':
                    speech.SpeakText("Robot fixed")
                elif args.sound=='full':
                    speech.SpeakText(robot_fixed_sentences[np.random.randint(0,len(robot_fixed_sentences)-1)] % str(robot_colors[robot_num]))
                    time.sleep(.1)
                robots[robot_num][1]=True
                any_fixed.value = 1 #do i still need this? forgot what it was for.


 
class Controller():
    def __init__(self, num_agents):

        #these are set internal helper variables
        self.actions = {'still':0,'left':1,'right':2,'forward':3, 'pickup':4}
        self.directions = {0:'right', 1:'down', 2:'left', 3:'up'}
        self.wall_left = ['left', 'forward', 'left']
        self.wall_right = ['right','forward','right']
        self.solve_error1 = ['pickup']#, 'forward']

        #user inputs
        self.num_agents = num_agents

        #internal state arrays dependent on num_agents
        self.act = ['forward']*num_agents #this holds either a list of actions or a single action
        self.counters = [0]*num_agents #this counts what action the robot is on when following a list 
        self.follow_actions = [0]*num_agents #list of actions robot will follow.
        self.objs = [0]*num_agents #0=nothing, 1=wall, 2=obstacle
        self.dir = [0]*num_agents
        self.pos = [[0,0]]*num_agents
        #mp.set_start_method('fork')

        #variables shared across process
        self.manager = mp.Manager()
        self.robots = self.manager.dict() #error robot
        self.any_fixed = mp.Value('i',0)
        self.listen_text = mp.Array('c', b'                                               '*3)
        self.proc = mp.Process(target=run,args=(self.robots, self.any_fixed,self.listen_text))
        self.proc.start()

    def next_action(self):
        for i in range(self.num_agents):
            #print('objs and robots:',self.objs, self.robots)

            #buglog, i'm not sure why it's pausing after first error
            #trying to print robots dict in ctrl thread and find out. it's not even saying just deleted after robot is fixed.
            if self.objs[i]>=2: #and (self.dir[i]=='up' or self.dir[i]=='down'): #so self.objs after 2 is the ball index
                # print("Robots dict in ctrl thread",list(self.robots.items()))
                if i in self.robots:
                    # print("is fixed?",self.robots[i][1])
                    if self.robots[i][1]: #if it's fixed
                        #self.follow_actions[i] = self.solve_error1 #this was a list, in case we want robots o move around robot
                        # can't follow list of actions to solve, if we want to handle edge cases, cuz then robot would be following Nested lists!
                        #self.act[i]='pickup'
                        if type(self.follow_actions[i])==list:
                            self.follow_actions[i]=self.follow_actions[i][:self.counters[i]]+['pickup']+self.follow_actions[self.counters[i]:]
                        else:
                            self.follow_actions[i]=['pickup'] #need to do list here, so afterwards (when list is done) default self.act is set to forward again
                        del self.robots[i] #delete item from robot
                    #    print("Just deleted robot",i,"from error dictionary")
                        self.any_fixed.value = 0
                        #self.act[i]='forward'
                    else: #robots not fixed, it should stand still and not do wall checking/rest of loop
                        self.act[i]='still'
                        continue
                else:
                    if DEBUG: print("Adding robot {} to failure list".format(i))
                    self.robots[i] = self.manager.list([self.objs[i]-2,False]) #need some sort of struct for error type
            elif self.objs[i]==1:
                #if you hit a wall, perform sequence of actions to turn around
                self.follow_actions[i] = self.wall_left if self.dir[i]=='down' else self.wall_right
            
            if type(self.follow_actions[i])==list:# and self.objs[i]<2: #if we are following a list AND we are not stopped behind failure
                #if we are following a list of actions increment through list, otherwise just hold the current action
    #            print("follow_actions",self.follow_actions[i])
    #            print("following_actions bot ",i,"counter",self.counters[i])
                if  self.counters[i]==len(self.follow_actions[i]):
                    #we're on the last action, get rid of counter and list of actions, time to go forward only
                     self.counters[i]=0
                     self.follow_actions[i]=0
                     self.act[i] = 'forward' #default action
                else:
                    #still on list of aciton, keep incrementing through it
                     self.act[i] =  self.follow_actions[i][self.counters[i]] 
                     self.counters[i]+=1
            #print("hello")
            # if (i==0):
            #     print("calc",args.level,self.pos[i][0], 20/5*(i+1))

            # if int(args.level)==3:
            #     print("level 3!!")
            global farm_size
            #print(self.pos)
            if ((int(args.level)==2 and self.pos[i][0]>farm_size/3*(i+1)+1) \
                    or (int(args.level)==3 and (self.pos[i][0]>farm_size/5*(i+1) and self.pos[i][1]>=farm_size))): #also had: self.counters[i]==0 and , but counters shouldn't matter
                    # print("in here",i,self.pos[i][0],20/5*(i+1))
                    # print(self.pos)
                    self.act[i]='still'
            
        #    else:
        #        print("moved default forward")

        return list(map(lambda x: self.actions[x],self.act))

    def get_status_text(self):
        robot_colors = ["Red", "Green", "Blue", "Purple", "Yellow"]
       # errors_at = list(map(lambda x: robot_colors[x], robots.keys()))
        text = ""
        for i,robo in enumerate(robot_colors):
            text+=robo+":"
            if i in self.robots.keys():
                text+="ERROR"
            else:
                text+="     "
            text+='\n'
        return text


parser = argparse.ArgumentParser(description=None)
parser.add_argument('-l', '--level', default="1", type=str)
parser.add_argument('-s', '--sound', default='word',type=str)
parser.add_argument('-i','--interface',default='not-gui',type=str)
# #sound vs. word vs. speech.

args = parser.parse_args()

def main():
    """Note: When adding to registry also need to import in __init__.py"""
    register(
        id='multigrid-farm-v0',
        entry_point='gym_multigrid.envs:FarmEnv50x50',
    )
    register(
        id='multigrid-farmtest-v0',
        entry_point = 'gym_multigrid.envs:TestFarm5x5',
    )
    register(
        id='multigrid-farmlevel-v3',
        entry_point = 'gym_multigrid.envs:FarmLevel3',
    )
    register(
        id='multigrid-farmlevel-v2',
        entry_point = 'gym_multigrid.envs:FarmLevel2',
    )
    register(
        id='multigrid-farmlevel-v1',
        entry_point = 'gym_multigrid.envs:FarmLevel1',
    )


 
    #print(args.level)
    #env = gym.make('multigrid-farm-v0')
    #env = gym.make('multigrid-farmtest-v0')
    #env = gym.make('multigrid-farmlevel-v1')
    env = gym.make('multigrid-farmlevel-v'+args.level)

    _ = env.reset()

    nb_agents = len(env.agents)

    try:
        ctrl = Controller(list([1,3,5])[int(args.level)-1])
        #ctrl = Controller(5)

        status_text = ""
        while True:
            env.render(mode='human', text_info=status_text, listen_text=ctrl.listen_text.value.decode())
            time.sleep(.5) #use for experiments!
            

            obs, reward, done, info = env.step(ctrl.next_action())
            
            #print(np.array(obs).flatten().size)
            #print("info:",info)
            ctrl.objs = info['objs']
            ctrl.dir = list(map(lambda x: ctrl.directions[x], info['dir']))
            ctrl.pos = info['pos']
            status_text = ctrl.get_status_text()

            if done:
                break
    except:
        print("Recieved ctrl-c")
        print("Unexpected error:", sys.exc_info())
        raise #uncommenting this will raise the true error, but u need to have task manager open to kill the other thread then cuz ctrl c won't work!
        ctrl.proc.terminate()

if __name__ == "__main__":
    main()



"""
multigrid.Actions.available (NOTE: left right is turning)
available=['still', 'left', 'right', 'forward', 'pickup', 'drop', 'toggle', 'done']
# still = 0, left = 1, right = 2, forward = 3, etc


#directions are 0 1 2 3 right down left up
    down
left    right
    up
# Map of agent direction indices to vectors
DIR_TO_VEC = [
    # Pointing right (positive X)
    np.array((1, 0)),
    # Down (positive Y)
    np.array((0, 1)),
    # Pointing left (negative X)
    np.array((-1, 0)),
    # Up (negative Y)
    np.array((0, -1)),
]
"""



"""
NEXT STEPS:
- fix at edge false positive
- fix robot 0 facing robots 1,2 bug! (need to count cols and make sure robots placed even apart? i think)

- add multiple agents and test!
- replace speech recognition with sounds and full speech rec (harder than will be)
- design 3-6 environments
- make portable
- read papers and develop survey questions
- begin testing
"""