from gym_multigrid.multigrid import *
import gym_multigrid as gym_multigrid

class FarmEnv(MultiGridEnv):
    """
    Environment in which the agents have to collect the balls
    """

    def __init__(
        self,
        size=10,
        width=None,
        height=None,
        num_balls=[],
        agents_index = [],
        balls_index=[],
        balls_reward=[],
        zero_sum = False,
        view_size=7

    ):
        self.num_balls = num_balls
        self.balls_index = balls_index
        self.balls_reward = balls_reward
        self.zero_sum = zero_sum

        self.world = World

        agents = []
        for i in agents_index:
            agents.append(Agent(self.world, i, view_size=view_size))

        super().__init__(
            grid_size=size,
            width=width,
            height=height,
            max_steps= 10000,
            # Set this to True for maximum speed
            see_through_walls=False,
            agents=agents,
            agent_view_size=view_size
        )



    def _gen_grid(self, width, height):
        self.grid = Grid(width, height)

        # Generate the surrounding walls
        self.grid.horz_wall(self.world, 0, 0)
        self.grid.horz_wall(self.world, 0, height-1)
        self.grid.vert_wall(self.world, 0, 0)
        self.grid.vert_wall(self.world, width-1, 0)

        for number, index, reward in zip(self.num_balls, self.balls_index, self.balls_reward):
            for i in range(number):
                self.place_obj(Ball(self.world, index, reward))

        # Randomize the player start position and orientation
        # for a in self.agents:
        #     self.place_agent(a)

        #NOTE: on 20x20 the top left most placeable square is 1,1 and the btm right most is 18,18 (the walls count towards the 20x20) 
        # oh also size is if you want to randomly place it in a subgrid from top as top left corner of size size
        self.agents[0].dir = 1
        self.agents[1].dir = 1
        self.agents[2].dir = 1
        self.place_agent(self.agents[0], top=(1,1), size = (1,1), rand_dir = False)
        self.place_agent(self.agents[1],top=(6,1), size = (1,1), rand_dir = False)
        self.place_agent(self.agents[2],top=(15,1), size = (1,1), rand_dir = False)


    def _reward(self, i, rewards, reward=1):
        """
        Compute the reward to be given upon success
        success => agent is at goal state
        """
        for j,a in enumerate(self.agents):
            if a.index==i or a.index==0:
                rewards[j]+=reward
            if self.zero_sum:
                if a.index!=i or a.index==0:
                    rewards[j] -= reward

    def _handle_pickup(self, i, rewards, fwd_pos, fwd_cell):
        if fwd_cell:
            if fwd_cell.can_pickup():
                if fwd_cell.index in [0, self.agents[i].index]:
                    fwd_cell.cur_pos = np.array([-1, -1])
                    self.grid.set(*fwd_pos, None)
                    self._reward(i, rewards, fwd_cell.reward)

    def _handle_drop(self, i, rewards, fwd_pos, fwd_cell):
        pass

    def step(self, actions):
        obs, rewards, done, info = MultiGridEnv.step(self, actions)
        return obs, rewards, done, info

    def _handle_special_moves(self, i, rewards, fwd_pos, fwd_cell):
        #wait i actually don't need this callback. can just do this logic in multigrid! before line 1328
        """
        #NOTE: This is called on every move!
        i : agent you are stepping for's index
        rewards : array of awards given ()
        fwd_pos : [x,y] array of position
        fwd_cell: obj that it is at the cell infront of you
        """
        
        if type(fwd_cell) == gym_multigrid.multigrid.Ball:
#            print("Error at robot",i) 
            return 2
        elif type(fwd_cell) == gym_multigrid.multigrid.Wall:
#            print(i, " hit a wall")
            return 1
        return 0
        


class FarmEnv50x50(FarmEnv):
    def __init__(self):
        super().__init__(size=20, #tianchen recommends 50
        num_balls=[5],
        agents_index = [1,2,3],
        balls_index=[0],
        balls_reward=[1],
        zero_sum=True)

"""
helpful link how to setup custom environments:
https://stackoverflow.com/questions/52727233/how-can-i-register-a-custom-environment-in-openais-gym
"""
