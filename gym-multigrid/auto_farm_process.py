import gym
import time
from gym.envs.registration import register
import numpy as np
import farm_speech as speech
from functools import reduce

#from multiprocessing import Process
import multiprocessing as mp

from tkinter import * 
import sys

import easygui
 

#robots = {} #holds key:val robot_id:[failure_num, is_fixed]
#any_fixed = 0
    
def run(robots, any_fixed):
    num = 0
    def callback1():
        if num not in robots:
            print("That robot number is not broken")
            return
        print("fixing error 0:")
        speech.hear_command("fix robot")
        print("Robot",0,"fixed!")
        robots[0][1]=True
        any_fixed.value=1
    def callback2():
        if num not in robots:
            print("That robot number is not broken")
            return
        print("fixing error 1:")
        speech.hear_command("move around")
        print("Robot",num,"fixed!")
        robots[num][1]=True
        any_fixed.value=1
    def callback3():
        if num not in robots:
            print("That robot number is not broken")
            return
        print("fixing error 2:")
        speech.hear_command("sending human")
        print("Robot",num,"fixed!")
        robots[num][1]=True
        any_fixed.value=1

    # root=Tk() 
    # var = StringVar()
    # p1=Label(root, textvariable=var) 
    # p1.pack()
    
    print("In process!")
    while True:
        print("in speech robots:_run",robots,any_fixed)
        #if something in dictionary and all robots are not fixed (is_fixed==0), then
        if robots and not any_fixed.value:#not reduce((lambda x,y: x or y),np.append(np.array(list(robots.values()))[:,1],0)): 
            print("reported error")
            #sys.stdout.flush()
            speech.SpeakText("Error at robots"+str(list(robots.keys())))
            #while True: 
            #var.set("Error at robots"+str(list(robots.keys())))

            print("right before forloop",robots)
            # R = []
            # for i in range(5):
            #     R.append(Radiobutton(root,text="Robot "+str(i), variable = num, value = i))
            #     R[i].pack()
            callbacks = [callback1,callback2,callback3]
            
            num = int(easygui.buttonbox("Error at robots"+str(list(robots.keys())), 'Fix Robot', list(map(lambda x: str(x), robots.keys())))) #('0','1', '2')))
            callbacks[robots[num][0]]()
            # B = Button(root, text ="Fix Robot", command = callbacks[robots[num][0]])
            # B.pack()
            # print("new mainloop")
            # root.mainloop()
    """
    print("In process!")
    def check_robots():
        #while True:
        print("in speech robots:_run",robots,any_fixed)
        #if something in dictionary and all robots are not fixed (is_fixed==0), then
        if robots and not any_fixed.value:#not reduce((lambda x,y: x or y),np.append(np.array(list(robots.values()))[:,1],0)): 
            print("reported error")
            #sys.stdout.flush()
            speech.SpeakText("Error at robots"+str(list(robots.keys())))
            #while True: 
            var.set("Error at robots"+str(list(robots.keys())))
            #print("right before forloop",robots)
    def cb_wrapper():
        print("Num = ",num)
        callbacks[robots[num][0]]()
    #R = []
    # for i in range(5):
    #     R.append(Radiobutton(root,text="Robot "+str(i), variable = num, value = i))
    #     R[i].pack()
    R = Radiobutton(root,text="Robot "+str(i), variable = num, value = i)
    callbacks = [callback1,callback2,callback3]
    B = Button(root, text ="Fix Robot", command = cb_wrapper)
    B.pack()
    B2 = Button(root, text="Refresh", command=check_robots)
    B2.pack()
    print("new mainloop")
    root.mainloop()

    #the problem with this method is that i couldn't get past root.mainloop() to continously check and update robots. 
    #apparentlyt he root.quit() would have done that tho. if I called root.quit() in one of the callbacks
    """        
        
    #self.terminated = 1
    # threads[self.threadID] = myThread(self.threadID,"Robot-"+str(self.threadID),5)
    # threads[self.threadID].daemon = True
# import argparse

# parser = argparse.ArgumentParser(description=None)
#parser.add_argument('-e', '--env', default='soccer', type=str)

#args = parser.parse_args()
 
class Controller():
    def __init__(self, num_agents):

        #these are set internal helper variables
        self.actions = {'left':1,'right':2,'forward':3, 'pickup':4}
        self.directions = {0:'right', 1:'down', 2:'left', 3:'up'}
        self.wall_left = ['left', 'forward', 'left']
        self.wall_right = ['right','forward','right']
        self.solve_error1 = ['pickup', 'forward','forward']

        #user inputs
        self.num_agents = num_agents

        #internal state arrays dependent on num_agents
        self.act = ['forward']*num_agents #this holds either a list of actions or a single action
        self.counters = [0]*num_agents
        self.follow_actions = [0]*num_agents #boolean array, indicates if a robot is following a list
        self.objs = [0]*num_agents #0=nothing, 1=wall, 2=obstacle
        self.dir = [0]*num_agents
        #mp.set_start_method('fork')

        #variables shared across process
        self.manager = mp.Manager()
        self.robots = self.manager.dict()
        self.any_fixed = mp.Value('i',0)
        self.proc = mp.Process(target=run,args=(self.robots, self.any_fixed))
        self.proc.start()

    def next_action(self):
       # global robots, any_fixed
        for i in range(self.num_agents):
            #print('objs and robots:',self.objs, self.robots)
            if self.objs[i]==1:
                #if you hit a wall, perform sequence of actions to turn around
                self.follow_actions[i] = self.wall_left if self.dir[i]=='down' else self.wall_right
            elif self.objs[i]>=2: #so self.objs after 2 is the ball index
                #print("Robots dict in ctrl thread",list(self.robots.items()))
 
                if i in self.robots:
                    if self.robots[i][1]: #if it's fixed
                        self.follow_actions[i] = self.solve_error1
                        del self.robots[i] #delete item from robot
                        print("Just deleted robot",i)
                        self.any_fixed.value = 0
                else:
                    print("Adding robot {} to failure list".format(i))
                    self.robots[i] = self.manager.list([self.objs[i]-2,False]) #need some sort of struct for error type
            if type(self.follow_actions[i])==list:
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
        #    else:
        #        print("moved default forward")

        return list(map(lambda x: self.actions[x],self.act))

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
    #env = gym.make('multigrid-farm-v0')
    env = gym.make('multigrid-farmtest-v0')
    _ = env.reset()

    nb_agents = len(env.agents)

    try:
        #ctrl = Controller(3)
        ctrl = Controller(2)

        while True:
            env.render(mode='human', highlight=True)
            time.sleep(.3)

            obs, reward, done, info = env.step(ctrl.next_action())
            
            #print(np.array(obs).flatten().size)
    #      print("info:",info)
            ctrl.objs = info['objs']
            ctrl.dir = list(map(lambda x: ctrl.directions[x], info['dir']))
            
            if done:
                break
    except:
        print("Recieved ctrl-c")
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
- add multiple agents and test!
- fix slowness bugs!
- replace speech recognition with sounds and full speech rec (harder than will be)
- add tkinter itf
- design 3-6 environments
- make portable
- read papers and develop survey questions
- begin testing

_________________________]
with multiprocessing:
* i don't think the multigrid process is reading the dictionary correctly. 
try printing just that! (bc after it fixes the robot in speech thread, the ball doesn't get picked up!)
"""