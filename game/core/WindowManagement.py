import numpy as np
import colorama
from time import sleep
from .Components import EmptyPage
import signal
from ..utils.colors import color_map, color_map_vectorized, cursor_goto, clear_screen
from ..utils.genComponentID import calculate_least_value_nin_array
from ..utils.inputHandler import getchar
from time import time
from queue import Queue
from threading import Thread
from .Components import Border
from os import system, name
from .Ball import Ball
from .Paddle import Paddle
from .Powerup import Powerup, SplitPowerup
from .Numbers import Score
from random import choice
from ..utils.collision import collide_inner
from copy import deepcopy
from .Numbers import Lives
from .Level import Level

# An exception to raise whenever an alarm hits when taking inputs
class CustomAlarmException(Exception):    
    pass

class Window:
    def __init__(self, config):
        self.config = config

        self.components = {
            0: Border(config.WIDTH, config.HEIGHT, 8) if config.BORDER else EmptyPage(config.WIDTH, config.HEIGHT),
            1: Score((4, 2), 4)
        }
        self.active_components = [0, 1]
        self.input_components = []
        self.ball_components = []
        self.paddle_component = None
        self.active_powerup = None

        self.input_queue = Queue()
        self.allowed_inputs = ["a", "d", " ", "r", "w", "s"]

        colorama.init(autoreset=True)
        self.exit = False

        self.lives_manager = Lives(self.config.WIDTH, 2, 5)
        self.add_component(self.lives_manager, True)
    
    def activate_component(self, component_id):
        if component_id not in self.active_components:
            self.active_components.append(component_id)
    
    def deactivate_component(self, component_id):
        if component_id in self.active_components:
            self.active_components = [el for el in self.active_components if el != component_id]
    
    def add_component(self, component, make_active=False, takes_input=False):
        component_id = calculate_least_value_nin_array(self.active_components)
        self.components[component_id] = component
        if make_active:
            self.activate_component(component_id)
        if takes_input:
            self.input_components.append(component_id)
        if isinstance(component, Ball):
            self.ball_components.append(component_id)
        elif isinstance(component, Paddle):
            self.paddle_component = component
    
    def remove_component(self, component_id):
        if component_id in self.components:
            del self.components[component_id]
        if component_id in self.active_components:
            self.active_components = [el for el in self.active_components if el != component_id]
        if component_id in self.input_components:
            self.input_components = [el for el in self.input_components if el != component_id]
        if component_id in self.ball_components:
            self.ball_components = [el for el in self.ball_components if el != component_id]

    def render_components(self):
        num_active = len(self.active_components)
        frame_buffer = np.zeros((self.config.WIDTH, self.config.HEIGHT))
        for component_id in self.active_components:
            if not self.config.BORDER and num_active > 1 and component_id == 0:
                continue
            component = self.components[component_id]
            bbox = [*component.start, component.width + component.start[0], component.height + component.start[1]]
            frame_buffer[bbox[0]:bbox[2], bbox[1]:bbox[3]] = component.render()
        Window.blit(frame_buffer.T)
    
    def game_loop(self):
        renderer = Thread(target=self.render_thread)
        renderer.start()
        self.input_thread()
        renderer.join()
        # Do all cleanup here
        if name == 'posix':
            _ = system('tput cnorm; clear')
        else:
            _ = system('cls')
        exit()

    def render_thread(self):
        sub_frame_number = 0
        graphics_update = int(self.config.FRAME_DURATION / self.config.COUNT_GRAPHICS_UPDATES)
        physics_update = int(self.config.FRAME_DURATION / self.config.COUNT_PHYSICS_UPDATES)

        start_time = time()

        # clear_screen()
        while not self.exit:
            if self.config.ONE_FRAME_ONLY and sub_frame_number == self.config.FRAME_DURATION - 1:
                break
            # Perform physics updates and other event updates here - more than once per frame
            if sub_frame_number % physics_update == 0:
                # Check if there are no balls left, if so reduce the lives and add a new ball
                if len(self.ball_components) == 0:
                    gameover = self.lives_manager.decrease_life()

                    # Check if game is over or not, if over exit
                    if gameover:
                        self.exit = True
                    else:
                        ball = Ball(-18, self.paddle_component)
                        self.add_component(ball, True, True)

                # Cleanup all dead powerup components as well as catch the completion of a level
                tobe_removed = []
                for (component_id, component) in self.components.items():
                    if isinstance(component, Level) and component.is_complete:
                        self.exit = True
                    # If powerup components is not active and has already started, then only state it can be in is dead state
                    if issubclass(type(component), Powerup) and ((component.start_time != -1 and not component.is_active) or ()):
                        # Check if the powerup component is a ball split to revert it
                        if isinstance(component, SplitPowerup):
                            for ball_id in self.ball_components[len(self.ball_components)//2:]:
                                tobe_removed.append(ball_id)
                        tobe_removed.append(component_id)
                for component_id in tobe_removed:
                    self.remove_component(component_id)

                update_time = time() - start_time
                # Send all the inputs over to the components that require them
                while not self.input_queue.empty():
                    event = self.input_queue.get(block=False)
                    for to_dispatch in self.input_components:
                        self.components[to_dispatch].handle_event(event, (2, 2, self.config.WIDTH - 2, self.config.HEIGHT - 1))

                # Perform time updates
                for to_dispatch in self.input_components:
                    self.components[to_dispatch].handle_event("t", update_time)
                
                # Perform the ball's collision updates
                powerup_to_be_added = None
                for component_id in self.active_components:
                    for ball_id in self.ball_components:
                        component = self.components[component_id]
                        if component.is_collideable:
                            powerup, score = self.components[ball_id].collide_with(component)
                            if powerup is not None and powerup_to_be_added is None:
                                powerup_to_be_added = powerup
                            if score != 0:
                                self.components[1].update_score(score)
                
                # Add the powerup component to be rendered
                if powerup_to_be_added is not None:
                    self.add_component(powerup_to_be_added, True, True)
                
                # Perform the paddle's collision updates
                changed_id = -1
                to_add_balls = []
                for component_id in self.active_components:
                    component = self.components[component_id]
                    if issubclass(type(component), Powerup) and self.paddle_component.start[0] <= component.start[0] <= self.paddle_component.start[0] + self.paddle_component.width and component.start[1] == self.paddle_component.start[1] - 1:
                        changed_id = component_id
                        self.components[changed_id].paddle = self.paddle_component
                        self.components[changed_id].balls = [self.components[ball_id] for ball_id in self.ball_components]
                        self.components[changed_id].speed = 0
                        self.components[changed_id].start = (60, 4) + np.random.randint(-3, 3, 2)
                        self.components[changed_id].execute_powerup(update_time)

                        # Check if the captured powerup is a multiplier - if it is then multiply the balls
                        if isinstance(component, SplitPowerup):
                            for ball_id in self.ball_components:
                                ball = self.components[ball_id]
                                to_add_balls.append(Ball(
                                    ball.color,
                                    ball.paddle,
                                    ball_pos=ball.pos + choice([-1, 1]) * np.random.randint(1, 3, 2),
                                    stuck_pos=ball.stuck_to_paddle,
                                    vel_dir=(ball.vel_dir * np.array([-1, 1])),
                                ))
                for ball in to_add_balls:
                    self.add_component(ball, True, True)
                
                # Remove the caught powerup from getting rendered
                if changed_id > 0:
                    self.deactivate_component(changed_id)
                
                # Perform all the collision of powerups with the walls and kill it accordingly
                tobe_removed = []
                for (component_id, component) in self.components.items():
                    if (issubclass(type(component), Powerup) or isinstance(component, Ball)) and component.start[1] >= self.config.HEIGHT - 2:
                        tobe_removed.append(component_id)
                for comp_id in tobe_removed:
                    self.remove_component(comp_id)
            # Update the graphics once per frame
            if sub_frame_number % graphics_update == 0:
                self.render_components()
            sub_frame_number += 1
    
    def input_thread(self):
        # Set Alarm Signal handlers to catch and raise an exception
        def alarmSignalHandler(signalNum, frame):
            raise CustomAlarmException
        signal.signal(signal.SIGALRM, alarmSignalHandler)

        while not self.exit:
            signal.setitimer(signal.ITIMER_REAL, 0.1) # Set a timer with 0.1 seconds interval
            input_char = ''
            try:
                input_char = getchar()
                signal.alarm(0) # Cancelled the alarm signal if we get a character
            except CustomAlarmException:
                # The raised exception stops from taking the input
                pass

            # Check for quit character and return
            if input_char == 'q':
                self.exit = True

            # Push the input to the inputs queue after checking if it valid
            if input_char in self.allowed_inputs:
                self.input_queue.put(input_char)

    @staticmethod
    def blit(buffer):
        buffer = color_map_vectorized(buffer)
        for row in range(buffer.shape[0]):
            cursor_goto(row + 1, 0)
            print("".join(buffer[row]))
