from game.core.WindowManagement import Window as WM
from game.core.Paddle import Paddle
from game.core.Ball import Ball
from game.core.Numbers import Time
from game.core.Level import Level
from game.core.Block import BlockOneHit, BlockTwoHit, BlockInfHit, BlockInvisible, BlockExplosive
from game.core.Powerup import Powerup
from game.utils.colors import clear_screen
from dotted_dict import DottedDict
from os import system, name
import signal
import sys
import random
import numpy as np

def main():
    resolution = (180, 50)
    config = DottedDict({
        "HEIGHT": resolution[1],
        "WIDTH": resolution[0],
        "FRAME_DURATION": 10,
        "COUNT_GRAPHICS_UPDATES": 2,
        "COUNT_PHYSICS_UPDATES": 10,
        "ONE_FRAME_ONLY": False,
        "BORDER": True,
    })
    win = WM(config)

    # Adds the paddle
    # Signature - width, height, color, (left, top)
    paddle_start = [int(resolution[0] / 2) - 10, resolution[1] - 2]
    paddle = Paddle(20, 1, 2, paddle_start)
    win.add_component(paddle, True, True)

    # Add a simple level in
    layer_res = [26, 30]
    layer_mat = []
    for row_num in range(layer_res[0]):
        row = []
        for col_num in range(layer_res[1]):
            # Conditions for blocks to be as they need to be
            explosive_conditions = [row_num in [layer_res[0] - 1], col_num in []]
            other_all_conditions = [row_num % 3 == 0, col_num % 3 == 0]

            if any(explosive_conditions):
                row.append(BlockExplosive())
            elif all(other_all_conditions):
                row.append(random.choice([BlockOneHit, BlockTwoHit, BlockInvisible, BlockOneHit, BlockTwoHit, BlockInvisible, BlockInfHit])())
            else:
                row.append(None)
        layer_mat.append(row)
    level = Level(np.array(layer_mat).T)
    win.add_component(level, True)

    # Adds display for time
    time_bar = Time((resolution[0] - 19, 2), 7)
    win.add_component(time_bar, True, True)

    if name == 'posix':
        _ = system('tput civis')
    win.game_loop()

if __name__ == '__main__':
    main()
