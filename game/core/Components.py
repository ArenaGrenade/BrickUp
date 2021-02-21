import numpy as np
from abc import ABC, abstractmethod

class Component(ABC):
    def __init__(self, width, height, start, collideable):
        self.width = width
        self.height = height
        self.start = start
        self.is_collideable = collideable
    
    @abstractmethod
    def render(self):
        pass

class EmptyPage(Component):
    def __init__(self, width, height, start=(0, 0)):
        super(EmptyPage, self).__init__(width, height, start)
        self.page = np.zeros((width, height))
    
    def render(self):
        return self.page

class Border(Component):
    def __init__(self, width, height, color):
        super(Border, self).__init__(width, height, (0, 0), True)
        self.border = np.pad(np.ones((width - 4, height - 2)), pad_width=((2, 2), (1, 1)), mode='constant', constant_values=color)
    
    def render(self):
        return self.border
