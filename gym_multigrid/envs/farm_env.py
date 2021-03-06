from gym_multigrid.multigrid import *
import gym_multigrid as gym_multigrid

farm_size = 45 #also must change in auto_farm_process.py!

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
        agents_loc = [],
        balls_index=[],
        balls_reward=[],
        balls_loc=[],
        zero_sum = False,
        view_size=7

    ):
        """ num_balls: indicates the number balls in each color set
            agents_index: list of agent indices; agents with same index will be same color
            agents_loc: list of (x,y) tuples indicating starting location of each agent
            balls_index: list of ball indices (distinguishes color)
            balls_reward: unused
            balls_loc: list of list of (x,y) tuples indicating starting location of each ball in each color set of balls
        """
        self.num_balls = num_balls
        self.balls_index = balls_index
        self.balls_reward = balls_reward
        self.balls_loc = balls_loc
        self.zero_sum = zero_sum

        self.world = World

        agents = []
        for i in agents_index: #if two agents have same i, they'll be same color
            agents.append(Agent(self.world, i, view_size=view_size))

        self.agents_loc = agents_loc

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

        if len(self.balls_loc)==0:
            #randomize ball placement
            for number, index in zip(self.num_balls, self.balls_index):
                # print("gen_grid balls", number,index)
                for i in range(number):
                    self.place_obj(Ball(self.world, index,inner_index=i))
        else:
            for number, index, location in zip(self.num_balls, self.balls_index, self.balls_loc):
                # print("gen_grid balls", number,index,location)
                for i in range(number):
                    self.place_obj(Ball(self.world, index,inner_index=i),top=location[i], size=(1,1))

        # Randomize the player start position and orientation
        # for a in self.agents:
        #     self.place_agent(a)

        #NOTE: on 20x20 the top left most placeable square is 1,1 and the btm right most is 18,18 (the walls count towards the 20x20) 
        # oh also size is if you want to randomly place it in a subgrid from top as top left corner of size size
        for agent,loc in zip(self.agents, self.agents_loc):
            # print("gen agents:",agent,loc)
            agent.dir = 1
            self.place_agent(agent,top=loc, size = (1,1), rand_dir = False)


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
        # print("picking it up!",fwd_cell,fwd_pos)
        if fwd_cell:
            if fwd_cell.can_pickup():
                #if fwd_cell.index in [0, self.agents[i].index]: 
                #oh i think index is the color! of ball or agent! lol so only red agent can pick up red ball? no thanks
                fwd_cell.cur_pos = np.array([-1, -1])
                self.grid.set(*fwd_pos, None)
                self._reward(i, rewards, fwd_cell.reward)

    def _handle_drop(self, i, rewards, fwd_pos, fwd_cell):
        pass

    def step(self, actions):
        obs, rewards, done, info = MultiGridEnv.step(self, actions)
        return obs, rewards, done, info

    def _handle_special_moves(self, i, rewards, fwd_pos, fwd_cell, action):
        #wait i actually don't need this callback. can just do this logic in multigrid! before line 1328
        """
        #NOTE: This is called on every move!
        i : agent you are stepping for's index
        rewards : array of awards given ()
        fwd_pos : [x,y] array of position
        fwd_cell: obj that it is at the cell infront of you
        """
       # print("HERE IN HANDLES SPCECIAL MOVES!")
       # print("fwd_cell",fwd_cell)
        if type(fwd_cell) == gym_multigrid.multigrid.Ball and (action == Actions().forward or action == Actions().still): #i think i had action =='forward' here to prevent them from triggering when they turn
            #print("Error at robot",i, fwd_cell)

            if fwd_cell.visible == False:
                fwd_cell.visible = True
            #    Grid.tile_cache = {}
            #code copied from grid.render_tile function
            # subdivs=3
            # tile_size=32
            # img = np.zeros(shape=(tile_size * subdivs, tile_size * subdivs, 3), dtype=np.uint8)
            # fwd_cell.render(img)

            return 2 + fwd_cell.index
        elif type(fwd_cell) == gym_multigrid.multigrid.Wall:
#            print(i, " hit a wall")
            return 1
        return 0
        


# class FarmEnv50x50(FarmEnv):
#     def __init__(self):
#         super().__init__(size=33, 
#         num_balls=[3,2,1], 
#         agents_index = [0,1,2],
#         agents_loc = [(1,1),(10,1),(20,1)],
#         balls_index=[0,1,2],
#         balls_reward=[1],
#         balls_loc = [[(25,2),(9,8),(5,6)],[(6,7),(18,16)],[(15,9)]],
#         zero_sum=True)

class TestFarm5x5(FarmEnv):
    def __init__(self):
        super().__init__(size=23, 
        num_balls=[1,1], 
        agents_index = [0,1],
        agents_loc = [(1,1),(6,1)],
        balls_index=[0,2],
        balls_reward=[1],
        balls_loc = [[(20,1)],[(1,20)]],
        zero_sum=True)

class FarmEnv50x50(FarmEnv):
    def __init__(self):
        super().__init__(size=53, #tianchen recommends 50
        num_balls=[3,2,1], 
        agents_index = [0,1,2],
        agents_loc = [(1,1),(10,1),(20,1),(30,1),(40,1)],
        balls_index=[0,1,2],
        balls_reward=[1],
        balls_loc = [[(25,2),(29,8),(5,6)],[(4,7),(18,16)],[(40,9)]],
        zero_sum=True)

#BELOW are the actual Farms used - we need 3!


class FarmLevel3(FarmEnv):
    def __init__(self):
        super().__init__(size=farm_size+2, 
        num_balls=[5,5,5], 
        agents_index = [0,1,2,3,4],
        agents_loc = [(farm_size//5*0+1,1),(farm_size//5+1,1),(farm_size//5*2+1,1),(farm_size//5*3+1,1),(farm_size//5*4+1,1)], #[(1,1),(5,1),(9,1),(13,1),(17,1)], #(farm_size//5+1,1),(farm_size//5*2+1,1),(farm_size//5*3+1,1),(farm_size//5*4+1,1)],
        balls_index=[0,1,2],
        balls_reward=[1],
        balls_loc = [], #[(1,20),(2,20)],[(3,20),(2,19)],[(3,19),(3,18)]
        zero_sum=True)

class FarmLevel2(FarmEnv):
    def __init__(self):
        super().__init__(size=farm_size+2, 
        num_balls=[2,2,2], 
        agents_index = [0,1,2],
        agents_loc = [(1,1),(7,1),(13,1)], #(farm_size//3+1,1),(farm_size//3*2,1)], #(9,1),(18,1)],
        balls_index=[0,1,2],
        balls_reward=[1],
        balls_loc = [],
        zero_sum=True)

class FarmLevel1(FarmEnv):
    def __init__(self):
        super().__init__(size=farm_size+2, 
        num_balls=[2,2,2], 
        agents_index = [0],
        agents_loc = [(1,1)],
        balls_index=[0,1,2],
        balls_reward=[1],
        balls_loc = [],
        zero_sum=True)

"""
helpful link how to setup custom environments:
https://stackoverflow.com/questions/52727233/how-can-i-register-a-custom-environment-in-openais-gym

0 Red
1 Green
2 Blue

"""
