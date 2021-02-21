from abc import ABC, abstractmethod
import numpy as np
from dotted_dict import DottedDict

class Block(ABC):
    def __init__(self):
        # Block States - 0 is the base and any other number denotes another state.
        # Hits on the block will reduce the state to 0, which is the base state
        self.block_states = {
            0: DottedDict({'color': 0}),
        }
        self.current_state = 0

        self.is_animated = False
    
    def get_render_mat(self):
        return np.ones((5, 1)) * self.block_states[self.current_state].color

    def make_hit(self):
        if self.current_state != 0:
            self.current_state -= 1
    
    def destruct(self):
        self.current_state = 0

class BlockOneHit(Block):
    def __init__(self):
        super(BlockOneHit, self).__init__()
        self.block_states.update({
            1: DottedDict({'color': 7})
        })
        self.current_state = 1

class BlockTwoHit(Block):
    def __init__(self):
        super(BlockTwoHit, self).__init__()
        self.block_states.update({
            1: DottedDict({'color': 7}),
            2: DottedDict({'color': 6})
        })
        self.current_state = 2

class BlockInvisible(Block):
    def __init__(self):
        super(BlockInvisible, self).__init__()
        self.block_states.update({
            1: DottedDict({'color': 7}),
            2: DottedDict({'color': 6}),
            3: DottedDict({'color': 1}),
        })
        self.current_state = 3

class BlockInfHit(Block):
    def __init__(self):
        super(BlockInfHit, self).__init__()
        self.block_states.update({
            1: DottedDict({'color': 8})
        })
        self.current_state = 1
    
    def make_hit(self):
        pass

class BlockExplosive(Block):
    def __init__(self):
        super(BlockExplosive, self).__init__()
        self.block_states.update({
            1: DottedDict({'color': 2}),
            2: DottedDict({'color': 4})
        })
        self.current_state = 1

        self.is_animated = True
        self.last_update = 0
        self.frame_duration = 8
    
    def flip_animation(self):
        if self.current_state == 1:
            self.current_state = 2
        elif self.current_state == 2:
            self.current_state = 1
    
    def get_render_mat(self):
        if self.last_update % self.frame_duration == 0:
            self.flip_animation()
        self.last_update += 1
        return np.ones((5, 1)) * self.block_states[self.current_state].color
    
    def make_hit(self):
        self.current_state = 0
    
    def destruct(self):
        super(BlockExplosive, self).destruct()
