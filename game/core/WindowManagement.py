import numpy as np
import colorama
from time import sleep
from .Components import EmptyPage
import signal
from ..utils.colors import color_map, color_map_vectorized, cursor_goto, clear_screen
from ..utils.genComponentID import calculate_least_value_nin_array
from ..utils.inputHandler import getchar

class AlarmException(Exception):    
    pass

class Window:
    def __init__(self, base_component, config):
        self.config = config

        self.components = {
            0: EmptyPage(config.WIDTH, config.HEIGHT)
        }
        self.active_components = [0]
        self.input_components = []

        self.input_queue = []
        self.allowed_inputs = ["w", "a", "s", "d"]

        colorama.init(autoreset=True)
    
    def activate_component(self, component_id):
        if component_id not in self.active_components:
            self.active_components.append(component_id)
    
    def deactivate_component(self, component_id):
        if component_id in self.active_components:
            self.active_components.remove(component_id)
    
    def add_component(self, component, make_active=False, takes_input=False):
        component_id = calculate_least_value_nin_array(self.active_components)
        self.components[component_id] = component
        if make_active:
            self.activate_component(component_id)
        if takes_input:
            self.input_components.append(component_id)
    
    def remove_component(self, component_id):
        del components[component_id]
        self.active_components.remove(component_id)
        self.input_components.remove(component_id)

    def render_components(self):
        num_active = len(self.active_components)
        frame_buffer = np.zeros((self.config.WIDTH, self.config.HEIGHT))
        for component_id in self.active_components:
            if num_active > 1 and component_id == 0:
                continue
            component = self.components[component_id]
            # print(component.start)
            bbox = [*component.start, component.width + component.start[0], component.height + component.start[1]]
            frame_buffer[bbox[1]:bbox[3], bbox[0]:bbox[2]] = component.render().T
        Window.blit(frame_buffer)
    
    def handle_inputs(self):
        def alarmSignalHandler(signalNum, frame):
            raise AlarmException
            
        signal.signal(signal.SIGALRM, alarmSignalHandler)
        signal.setitimer(signal.ITIMER_REAL, 0.1)
        input_char = ''
        try:
            input_char = getchar()
            signal.alarm(0)
        except AlarmException:
            pass
        signal.signal(signal.SIGALRM, signal.SIG_IGN)
        if input_char in self.allowed_inputs:
            self.input_queue.append(input_char)

    def render_loop(self):
        sub_frame_number = 0
        graphics_update = int(self.config.FRAME_DURATION / self.config.COUNT_GRAPHICS_UPDATES)
        physics_update = int(self.config.FRAME_DURATION / self.config.COUNT_PHYSICS_UPDATES)

        # clear_screen()
        while True:
            if self.config.ONE_FRAME_ONLY and sub_frame_number == self.config.FRAME_DURATION - 1:
                break
            if sub_frame_number % physics_update == 0:
                # Perform physics updates here - more than once per frame

                # Send all he inputs over to the components that require them
                while len(self.input_queue) > 0:
                    action = self.input_queue.pop(0)
                    for to_dispatch in self.input_components:
                        self.components[to_dispatch].perform_action(action, (2, 1, self.config.WIDTH - 2, self.config.HEIGHT - 1))
            if sub_frame_number % graphics_update == 0:
                # Update the graphics once per frame
                self.render_components()
            sub_frame_number += 1
            # sleep(0.1)

            # Handle inputs
            self.handle_inputs()

    @staticmethod
    def blit(buffer):
        buffer = color_map_vectorized(buffer)
        for row in range(buffer.shape[0]):
            cursor_goto(row + 1, 0)
            print("".join(buffer[row]))
