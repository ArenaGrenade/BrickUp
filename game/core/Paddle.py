from .Components import Component
import numpy as np

class Paddle(Component):
    def __init__(self, width, height, color, start):
        super(Paddle, self).__init__(width, height, start)
        self.color = color
        self.paddle = np.zeros((width, height))
        self.paddle.fill(color)
    
    def render(self):
        return self.paddle
    
    def powerup_expand_paddle(self):
        self.width *= 2
        self.paddle = np.zeros((self.width, self.height))
        self.paddle.fill(self.color)
    
    def move(self, x, y):
        self.start += np.array([x, y])
    
    def perform_action(self, action, bounds):
        if action == "d" and self.width + self.start[0] + 2 < bounds[3]:
            self.move(2, 0)
        elif action == "a" and self.start[0] > bounds[0]:
            self.move(-2, 0)
        elif action == "w":
            self.powerup_expand_paddle()
