import gym
import time
from gym.envs.registration import register
import numpy as np
import threading
#import farm_speech
import pyttsx3 

threads = []

def SpeakText(command): 
	
	# Initialize the engine 
	engine = pyttsx3.init() 
	engine.say(command) 
	engine.runAndWait() 

class myThread (threading.Thread):
   def __init__(self, threadID, name):
      threading.Thread.__init__(self)
      self.threadID = threadID
      self.name = name
      self.terminated = 0
   def run(self):
        while(True): 
            print('IN THREAD',self.threadID)
            SpeakText("Error at "+self.name)
            a = input("Press enter")
            if a =='a':
                
                break
        print("Exiting THREAD",self.threadID)
        self.terminated = 1
        # threads[self.threadID] = myThread(self.threadID,"Robot-"+str(self.threadID),5)
        # threads[self.threadID].daemon = True
# import argparse

# parser = argparse.ArgumentParser(description=None)
#parser.add_argument('-e', '--env', default='soccer', type=str)

#args = parser.parse_args()

def main():

    register(
        id='multigrid-farm-v0',
        entry_point='gym_multigrid.envs:FarmEnv50x50',
    )
    env = gym.make('multigrid-farm-v0')
    
    _ = env.reset()

    nb_agents = len(env.agents)

    actions = {'left':1,'right':2,'forward':3}
    directions = {0:'right', 1:'down', 2:'left', 3:'up'}
    act = ['forward']*3 #this holds either a list of actions or a single action
    wall_left = ['left', 'forward', 'left']
    wall_right = ['right','forward','right']
    counters = [0,0,0]
    follow_actions = [0]*3 #indicates if a robot is following a list
    walls = [0,0,0]
    dir = [0,0,0]
    for i in range(3):
        threads.append(myThread(i,"Robot-"+str(i)))
        threads[i].daemon = True #kills the thread when main program exits
    while True:
        env.render(mode='human', highlight=True)
        time.sleep(.3)

 #       print("threads",list(threading.enumerate()))
        for i in range(3):
            if walls[i]==1:
                follow_actions[i] = wall_left if dir[i]=='down' else wall_right
            elif walls[i]==2 and not threads[i].is_alive(): #we're at an object
                if threads[i].terminated:
                    threads[i] = threads[i] = myThread(i,"Robot-"+str(i))
                    threads[i].daemon = True
                threads[i].start()
            if type(follow_actions[i])==list:
  #              print("follow_actions",follow_actions)
  #              print("following_actions bot ",i,"counter",counters[i])
                if counters[i]==len(follow_actions[i]):
                    counters[i]=0
                    follow_actions[i]=0
                    act[i] = 'forward' #default action
                else:
                    act[i] = follow_actions[i][counters[i]] 
                    counters[i]+=1
  #      print(act)
  #      print("action numbers:",list(map(lambda x:actions[x],act)))
            
        obs, reward, done, info = env.step(list(map(lambda x: actions[x],act)))
        #print(np.array(obs).flatten().size)
  #      print("info:",info)
        walls = info['walls']
        dir = list(map(lambda x: directions[x], info['dir']))
        
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