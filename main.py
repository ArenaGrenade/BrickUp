from game.core.WindowManagement import Window as WM
from game.core.Components import Border
from game.core.Paddle import Paddle
from game.utils.colors import clear_screen
from dotted_dict import DottedDict
from os import system, name
import signal
import sys

def main():
    resolution = (180, 50)
    config = DottedDict({
        "HEIGHT": resolution[0],
        "WIDTH": resolution[1],
        "FRAME_DURATION": 10,
        "COUNT_GRAPHICS_UPDATES": 5,
        "COUNT_PHYSICS_UPDATES": 10,
        "ONE_FRAME_ONLY": False,
    })

    def handleSignal(signalNumber, frame):
        if name == 'posix':
            _ = system('tput cnorm; clear')
        else:
            _ = system('cls')
        sys.exit()
    signal.signal(signal.SIGINT, handleSignal)

    border = Border(*resolution, 8)
    # Signature - width, height, color, (left, top)
    box = Paddle(20, 1, 2, [int(resolution[0] / 2) - 10, resolution[1] - 3])
    win = WM(border, config)
    win.add_component(border, True)
    win.add_component(box, True, True)

    if name == 'posix':
        _ = system('tput civis')
    win.render_loop()

if __name__ == '__main__':
    main()
