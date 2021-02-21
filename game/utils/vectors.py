from enum import Enum
from dotted_dict import DottedDict
import numpy as np

class Direction(Enum):
    Null = -1
    Up = 0
    Down = 1
    Left = 2
    Right = 3

direction_dict = [np.array([0, -1]), np.array([0, 1]), np.array([-1, 0]),  np.array([1, 0])]

def get_direction(vector):
    max_dot = 0
    best_match = -1
    for (index, direction) in enumerate(direction_dict):
        dot_value = np.dot(vector, direction)
        if dot_value > max_dot:
            max_dot = dot_value
            best_match = index

    return Direction(best_match)
