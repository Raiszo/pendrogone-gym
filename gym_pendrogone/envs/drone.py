import numpy as np
import gym
from gym import error, spaces, utils
from gym.utils import seeding

LIMITS = np.array([1.5, 1.5])
T = 0.02

class Drone(gym.Env):
    metadata = {
        'render.modes': ['human'],
        'video.frames_per_second' : 50
    }

    def __init__(self):
        self.gravity = 9.81 #: [m/s2] acceleration
        self.mass = 0.5 #: [kg] mass
        self.Ixx = 0.00025
        self.arm_length = 0.086 # [m]
        self.arm_width = 0.02 # [m]
        self.height = 0.02 # [m]

        # max and min force for each motor
        self.maxF = 2 * self.mass * self.gravity
        self.minF = 0
        self.maxAngle = 90 * math.pi / 180
        self.dt = 0.02
        
        high = np.array([
            np.finfo(np.float32).max,
            np.finfo(np.float32).max,
            self.maxAngle * 2,
            np.finfo(np.float32).max,
            np.finfo(np.float32).max,
            np.finfo(np.float32).max
        ])
        
        self.action_space = spaces.Box(
            low = np.array([self.minF, self.minF]),
            high = np.array([self.maxF, self.maxF]),
            dtype = np.float32
        )
        self.observation_space = spaces.Box(-high, high, dtype=np.float32)

        self.seed()
        self.viewer = None
        self.state = None

    def seed(self, seed=None):
        self.np_random, seed = seeding.np_random(seed)
        return [seed]
        
    def render(self, mode='human', close=False):
        from gym.envs.classic_control import rendering
        screen_width = 500
        screen_height = 500

        x,z,phi = self.state[0:3].tolist()

        T = np.array([[np.cos(phi), -np.sin(phi), x],
                      [np.sin(phi), np.cos(phi), z],
                      [0, 0, 1]])

        bodyFrame = np.array([[self.arm_length, 0 , 1],
                              [-self.arm_length, 0 , 1]])

        worldFrame = T.dot(bodyFrame.T)[:-1,:]
        t1_xy = worldFrame[:,0].tolist()
        t2_xy = worldFrame[:,1].tolist()
        
        if self.viewer is None:
            self.viewer = rendering.Viewer(screen_width, screen_height)
            self.viewer.set_bounds(-1,1,-1,1)
            
            l,r,t,b = -self.arm_length, self.arm_length, self.arm_width, -self.arm_width
            self.frame_trans = rendering.Transform(rotation=phi, translation=(x,z))
            frame = rendering.FilledPolygon([(l,b), (l,t), (r,t), (r,b)])
            frame.set_color(0, .8, .8)
            frame.add_attr(self.frame_trans)
            self.viewer.add_geom(frame)

            self.t1_trans = rendering.Transform(translation=t1_xy)
            thruster1 = self.viewer.draw_circle(.04)
            thruster1.set_color(.8, .8, 0)
            thruster1.add_attr(self.t1_trans)
            self.viewer.add_geom(thruster1)

            self.t2_trans = rendering.Transform(translation=t2_xy)
            thruster2 = self.viewer.draw_circle(.04)
            thruster2.set_color(.8, .8, 0)
            thruster2.add_attr(self.t2_trans)
            self.viewer.add_geom(thruster2)

        self.frame_trans.set_translation(x,z)
        self.frame_trans.set_rotation(phi)
        
        self.t1_trans.set_translation(t1_xy[0], t1_xy[1])
        self.t2_trans.set_translation(t2_xy[0], t2_xy[1])
        
        return self.viewer.render(return_rgb_array = mode=='rgb_array')        

    def close(self):
        if self.viewer: self.viewer.close()