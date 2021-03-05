import gym
import time
from gym.envs.registration import register
import numpy as np
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
    act = ['forward']*3 #this holds either a list of actions or a single action
    wall_left = ['left', 'forward', 'left']
    counters = [0,0,0]

    while True:
        env.render(mode='human', highlight=True)
        time.sleep(0.1)

        #ac = [env.action_space.sample() for _ in range(nb_agents)]
        for i in range(3):
            if type(act[i])==list:
                if counters[i]==len(act[i])-1:
                    counters[i]=-1
                else:
                    counters[i]+=1
            

        ac = [3,3,3]
        # for ind,i in enumerate(at_wall):
        #     if i==1:
        #         ac[ind]=1,1
        obs, reward, done, info = env.step(map(act,lambda x:actions[x]))
        #print(np.array(obs).flatten().size)
        print("wall?",info)
        
        
        if done:
            break

if __name__ == "__main__":
    main()



"""
multigrid.Actions.available (NOTE: left right is turning)
available=['still', 'left', 'right', 'forward', 'pickup', 'drop', 'toggle', 'done']
# still = 0, left = 1, right = 2, forward = 3, etc


#directions are 0 1 2 3 right down left up
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