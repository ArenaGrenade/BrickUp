from .Components import Component
import numpy as np
from colorama import Fore
from random import randint
from .Components import Border
from .Level import Level
from .Paddle import Paddle
from ..utils.collision import collide_inner, collide_outer

class Ball(Component):
    def __init__(self, color, paddle, ball_pos=None, stuck_pos=None, vel_dir=[0.0, -1.0]):
        super(Ball, self).__init__(2, 1, (0, 0), False)
        self.color = color
        self.ball = np.array([color])
        self.paddle = paddle

        self.stuck_to_paddle = -1
        if stuck_pos is None:
            # Here we have the case that its neither stuck nor free - need new generation
            self.stuck_to_paddle = randint(0, 18)
            self.init_on_paddle()
        elif stuck_pos != -1:
            # Here is when the ball is stuck to the paddle and thatt value is being passed
            self.stuck_to_paddle = stuck_pos
            self.init_on_paddle()
        else:
            # Do something with the pos variable and all
            self.pos = ball_pos

        # self.velocity_scalar = 0.02
        self.velocity_scalar = 0.1
        # This will be the floating point version of start - so updates can be properly made
        self.vel_dir = vel_dir
        self.destruct_ready = False
        self.stick_powerup = False
    
    def init_on_paddle(self):
        self.move_to(self.paddle.start[0] + self.stuck_to_paddle, float(self.paddle.start[1] - 1))

    def render(self):
        return self.ball
    
    def update_positions(self):
        self.start = np.array([int(x) for x in self.pos])
    
    def move_vel(self):
        if self.stuck_to_paddle < 0:
            self.pos += (self.vel_dir * self.velocity_scalar)
            self.update_positions()
    
    def move_to(self, x, y):
        self.pos = np.array([x, y])
        self.update_positions()
    
    def handle_event(self, event, payload):
        # Handle input events
        if event in ["a", "d"] and self.stuck_to_paddle != -1:
            self.move_to(self.paddle.start[0] + self.stuck_to_paddle, self.paddle.start[1].astype(float) - 1)
        elif event == " " and self.stuck_to_paddle >= 0:
            self.stuck_to_paddle = -1
        
        # Handle time events
        if event == "t":
            self.move_vel()
    
    def collide_with(self, other):
        self_aabb = np.array([self.start[0], self.start[1], self.width + self.start[0], self.height + self.start[1]])
        collision_change = np.array([False, False])
        powerup = None
        score = 0
        if isinstance(other, Border):
            # Perform border / game edge collision
            other_aabb = np.array([2, 1, other.width - 2, other.height - 1])
            collision_change = collide_inner(self_aabb, other_aabb)
        elif isinstance(other, Level):
            # Collides with the level
            collision_change, powerup, score = other.collide_level(self)
        elif isinstance(other, Paddle):
            # Special collision handling for colliding with the Paddle
            is_collided = other.start[0] <= self_aabb[0] <= other.start[0] + other.width and self_aabb[1] >= other.start[1] - 1
            if is_collided and self.stuck_to_paddle < 0:
                paddle_hit_coordinates = self_aabb[0] - other.start[0]
                deflection = (paddle_hit_coordinates - other.width / 2) / other.width / 8
                self.vel_dir += [deflection, 0]
                self.vel_dir /= np.linalg.norm(self.vel_dir)
                collision_change[1] = True
                if self.stick_powerup:
                    self.stuck_to_paddle = paddle_hit_coordinates
        else:
            # This does not happen in the current version of the game, but if needed it can be expanded to use this feature
            # Collides with any other object - just reverse velocities based on hit axis on AABB
            other_box = np.array([other.start[0] - 1, other.start[1] - 1, other.width + other.start[0], other.height + other.start[1]])
            collision_change = collide_outer(self_aabb, other_box, self.vel_dir)
        self.vel_dir *= (np.invert(collision_change) * 2 - 1)

        return powerup, score
