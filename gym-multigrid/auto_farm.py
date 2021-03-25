import gym
import time
from gym.envs.registration import register
import numpy as np
import threading
import farm_speech as speech

robots = {} #holds key:val robot_id:[failure_num, is_fixed]


class myThread (threading.Thread):
   def __init__(self, threadID, name):
      threading.Thread.__init__(self)
      self.threadID = threadID
      self.name = name
      self.terminated = 0
    
   def run(self):
        #print('Error - IN THREAD',self.threadID)
        global robots
        while True:
            if robots: #empty dictionary evals to false
                speech.SpeakText("Error at robots"+str(list(robots.keys())))
                #while True: 
                num = int(input("Press robot number to diagnose\n"))
               # print(list(robots),num,"bool", bool(num in robots), bool(robots[num]))
                if num in robots:
                    if robots[num][0]==0: #fixes robot with error code zero
                        speech.hear_command("fix robot")
                        print("Robot",num,"fixed!")
                        robots[num][1]=True
                    #break
                else:
                    print("That robot number is not broken")
                        
        self.terminated = 1
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
       # self.threads = []

        #initialize threads
        # for i in range(num_agents):
        self.thread = myThread(0,"Robot-Thread")
        self.thread.daemon = True #kills the thread when main program exitss
        print("creating thread")
        self.thread.start()

    def next_action(self):
        global robots
        for i in range(self.num_agents):
            if self.objs[i]==1:
                #if you hit a wall, perform sequence of actions to turn around
                self.follow_actions[i] = self.wall_left if self.dir[i]=='down' else self.wall_right
            elif self.objs[i]==2:
                print("Robots dict in ctrl thread",list(robots.items()))
                if i in robots:
                    if robots[i][1]: #if it's fixed
                        self.follow_actions[i] = self.solve_error1
                        del robots[i] #delete item from robot
                else:
                    print("Adding robot {} to failure list".format(i))
                    robots[i] = [0,False] #need some sort of struct for error type
            
            if type(self.follow_actions[i])==list:
                #if we are following a list of actions increment through list, otherwise just hold the current action
                print("follow_actions",self.follow_actions[i])
                print("following_actions bot ",i,"counter",self.counters[i])
                if  self.counters[i]==len(self.follow_actions[i]):
                    #we're on the last action, get rid of counter and list of actions, time to go forward only
                     self.counters[i]=0
                     self.follow_actions[i]=0
                     self.act[i] = 'forward' #default action
                else:
                    #still on list of aciton, keep incrementing through it
                     self.act[i] =  self.follow_actions[i][self.counters[i]] 
                     self.counters[i]+=1

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

    #ctrl = Controller(3)
    ctrl = Controller(1)

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