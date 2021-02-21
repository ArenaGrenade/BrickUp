from .Components import Component
import numpy as np

class Paddle(Component):
    def __init__(self, width, height, color, start):
        super(Paddle, self).__init__(width, height, start, True)
        self.color = color
        self.generate_sized_paddle_image()

        self.default_width = width
        self.paddle_powerups = []
    
    def render(self):
        return self.paddle
    
    def generate_sized_paddle_image(self):
        self.paddle = np.zeros((self.width, self.height))
        self.paddle.fill(self.color)
    
    def revert_size(self):
        if len(self.paddle_powerups) > 0:
            to_change = self.paddle_powerups.pop(0)
            if to_change == "shrink":
                self.width += 2
            else:
                self.width -= 2
            self.generate_sized_paddle_image()
    
    def powerup_expand_paddle(self):
        if self.width <= 40:
            self.width += 2
            self.generate_sized_paddle_image()
            self.paddle_powerups.append("expand")
    
    def powerup_shrink_paddle(self):
        if self.width >= 10:
            self.width -= 2
            self.generate_sized_paddle_image()
            self.paddle_powerups.append("shrink")
    
    def move(self, x, y):
        self.start += np.array([x, y])
    
    def handle_event(self, event, bounds):
        if event == "d" and self.width + self.start[0] < bounds[2]:
            self.move(1, 0)
        elif event == "a" and self.start[0] > bounds[0]:
            self.move(-1, 0)
