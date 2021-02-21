from .Components import Component
from ..utils.DigitMatrices import digits, DIGIT_MATRIX_SIZE
import numpy as np
from abc import ABC, abstractmethod

class Digit(ABC):
    def __init__(self, value):
        self.digit = value

    @abstractmethod
    def get_image(self, color):
        pass

class NormalDigit(Digit):
    def ___init__(self, value):
        super(NormalDigit, self).__init__(value)
    
    def get_image(self, color):
        return (digits[self.digit] * color)

class BinaryDigit(Digit):
    def __init__(self, value, empty_color=5):
        super(BinaryDigit, self).__init__(list(format(value, 'b').rjust(4, '0')))
        self.empty_color = empty_color
    
    def get_image(self, color):
        colored = [color if x == '1' else self.empty_color for x in self.digit]
        return np.array([colored] * 2)

BinaryDigitManager = [BinaryDigit(i) for i in range(10)]
NormalDigitManager = [NormalDigit(i) for i in range(10)]

class Time(Component):
    def __init__(self, start, color):
        self.digits = [0] * 4
        dimension = np.array((2, 4)) * np.array([4, 1]) + [3, 0]
        super(Time, self).__init__(*dimension, start, False)
        self.color = color
    
    def generate_image(self):
        image = []
        for digit in self.digits:
            digit_image = list(BinaryDigitManager[digit].get_image(self.color))
            image += digit_image
            image.append(np.zeros(self.height))
        image.pop(-1)
        return np.array(image)

    def handle_event(self, event, payload):
        if event == "t":
            minutes = int(payload) / 60
            seconds = int(payload) % 60
            self.digits = [int(minutes / 10), int(minutes % 10), int(seconds / 10), int(seconds % 10)]
    
    def render(self):
        return self.generate_image()

class Score(Component):
    def __init__(self, start, color):
        self.digits = np.array([0] * 4)
        dimension = DIGIT_MATRIX_SIZE * np.array([4, 1]) + [3, 0]
        super(Score, self).__init__(*dimension, start, False)
        self.color = color

    def generate_image(self):
        image = []
        for digit in self.digits:
            digit_image = list(NormalDigitManager[digit].get_image(self.color))
            image += digit_image
            image.append(np.zeros(self.height))
        image.pop(-1)
        return np.array(image)
    
    def update_score(self, score):
        current_score = np.sum(self.digits * [1000, 100, 10, 1])
        incremented_score = current_score + score
        new_score = np.array([int(x) for x in str(incremented_score).rjust(4, '0')])
        if len(new_score) == 4:
            self.digits = new_score
    
    def render(self):
        return self.generate_image()

class Lives(Component):
    def __init__(self, width, top, color):
        self.max_lives = 5
        self.lives = self.max_lives + 1
        self.box_size = 10
        self.space_size = 2
        self.dimension = (self.box_size * self.max_lives + self.space_size * (self.max_lives - 1), 1)
        super(Lives, self).__init__(*self.dimension, [width // 2 - self.dimension[0] // 2, top], False)
        self.color = color
    
    def calculate_blit_image(self):
        allowed = np.matmul(np.diag([1] * self.lives + [0] * (self.max_lives - self.lives)), np.ones((self.max_lives, self.box_size)))
        self.blit_image = np.concatenate((allowed, np.zeros(self.space_size * self.max_lives).reshape(-1, self.space_size)), axis=1).reshape(-1)[:-self.space_size].reshape(-1, 1) * self.color
    
    def decrease_life(self):
        self.lives -= 1
        self.calculate_blit_image()
        return self.lives <= 0
    
    def render(self):
        return self.blit_image
