from colorama import Fore, Back, Style, Cursor
import numpy as np

cols = {
    -8: Fore.WHITE,
    -7: Fore.CYAN,
    -6: Fore.MAGENTA,
    -5: Fore.BLUE,
    -4: Fore.YELLOW,
    -3: Fore.GREEN,
    -2: Fore.RED,
    -1: Fore.BLACK,
    0: "",
    1: Back.BLACK,
    2: Back.RED,
    3: Back.GREEN,
    4: Back.YELLOW,
    5: Back.BLUE,
    6: Back.MAGENTA,
    7: Back.CYAN,
    8: Back.WHITE,
}

char_map = {
    0: " ",
    1: u'\u2b24',
    2: "",
    3: "\033[01m" + u'\u21da' + u'\u21db',
    4: "\033[01m" + u'\u21db' + u'\u21da',
    5: "\033[01m" + u'\u23E9',
    6: "\033[01m" + u'\u2702',
    7: "\033[01m" + u'\u27AB',
    8: "\033[01m" + u'\u00BD'
}

def color_map(x):
    color = np.sign([x])[0] * (abs(x) % 10)
    char = abs(x) / 10
    return cols[int(color)] + char_map[int(char)] + Style.RESET_ALL
color_map_vectorized = np.vectorize(color_map)

CLEAR_SCREEN = '\033[2J'

cursor_goto = lambda y, x: print(Cursor.POS(x + 1, y + 1), end='')
clear_screen = lambda: print('\033[2J', end='')
