from .Components import Component
import numpy as np

class Powerup(Component):
    def __init__(self, width, start, render_mat):
        super(Powerup, self).__init__(width, 1, start, False)
        self.render_mat = render_mat
        self.pos = self.start
        self.speed = 0.04
        self.is_active = False
        self.start_time = -1

        # self.active_time = 10
        self.active_time = 5
    
    def render(self):
        return self.render_mat
    
    def update_positions(self):
        self.start = np.array([int(x) for x in self.pos])
    
    def move_vel(self):
        if not self.is_active:
            self.pos += self.speed * np.array([0, 1])
            self.update_positions()
    
    def handle_event(self, event, payload):
        if event == "t":
            self.move_vel()
            if self.is_active and payload - self.start_time >= self.active_time:
                self.kill_powerup()
    
    def execute_powerup(self, time):
        self.is_active = True
        self.start_time = time

    def kill_powerup(self):
        self.is_active = False

class ExpandPowerup(Powerup):
    def __init__(self, start):
        super(ExpandPowerup, self).__init__(2, start, np.array([[35], [20]]))
    
    def execute_powerup(self, time):
        super().execute_powerup(time)
        self.paddle.powerup_expand_paddle()
    
    def kill_powerup(self):
        super().kill_powerup()
        self.paddle.revert_size()

class ShrinkPowerup(Powerup):
    def __init__(self, start):
        super(ShrinkPowerup, self).__init__(2, start, np.array([[42], [20]]))
    
    def execute_powerup(self, time):
        super().execute_powerup(time)
        self.paddle.powerup_shrink_paddle()
    
    def kill_powerup(self):
        super().kill_powerup()
        self.paddle.revert_size()

class SpeedupPowerup(Powerup):
    def __init__(self, start):
        super(SpeedupPowerup, self).__init__(2, start, np.array([[52], [20]]))
        self.velocity_addition = 0.05
    
    def execute_powerup(self, time):
        super().execute_powerup(time)
        for ball in self.balls:
            ball.velocity_scalar = min(ball.velocity_scalar + self.velocity_addition, 0.5)
    
    def kill_powerup(self):
        super().kill_powerup()
        for ball in self.balls:
            ball.velocity_scalar = max(ball.velocity_scalar - self.velocity_addition, 0.1)

class DestructPowerup(Powerup):
    def __init__(self, start):
        super(DestructPowerup, self).__init__(1, start, np.array([[65]]))
    
    def execute_powerup(self, time):
        super().execute_powerup(time)
        for ball in self.balls:
            ball.destruct_ready = True
    
    def kill_powerup(self):
        super().kill_powerup()
        for ball in self.balls:
            ball.destruct_ready = False

class GrabPowerup(Powerup):
    def __init__(self, start):
        super(GrabPowerup, self).__init__(1, start, np.array([[75]]))
    
    def execute_powerup(self, time):
        super().execute_powerup(time)
        for ball in self.balls:
            ball.stick_powerup = True
    
    def kill_powerup(self):
        super().kill_powerup()
        for ball in self.balls:
            ball.stick_powerup = False

class SplitPowerup(Powerup):
    def __init__(self, start):
        super(SplitPowerup, self).__init__(1, start, np.array([[85]]))
    
    def execute_powerup(self, time):
        super().execute_powerup(time)
    
    def kill_powerup(self):
        super().kill_powerup()
