from colorama import Fore, Back, Style, Cursor
import numpy as np

BACKS = {
    0: "",
    1: Back.BLACK,
    2: Back.RED,
    3: Back.GREEN,
    4: Back.YELLOW,
    5: Back.BLUE,
    6: Back.MAGENTA,
    7: Back.CYAN,
    8: Back.WHITE
}
color_map = lambda x: BACKS[int(x)] + " " + Style.RESET_ALL
color_map_vectorized = np.vectorize(color_map)

CLEAR_SCREEN = '\033[2J'

cursor_goto = lambda y, x: print(Cursor.POS(x + 1, y + 1), end='')
clear_screen = lambda: print('\033[2J', end='')
