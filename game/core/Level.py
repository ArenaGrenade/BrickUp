from .Components import Component
import numpy as np
from math import ceil
from ..utils.collision import collide_outer
from .Powerup import ExpandPowerup, ShrinkPowerup, SpeedupPowerup, DestructPowerup, GrabPowerup, SplitPowerup
from random import random, choice
from .Block import BlockInfHit, BlockExplosive

brick_adjacency = [
    np.array([-1, 0]), # Transform left
    np.array([0, -1]), # Transform top
    np.array([1, 0]), # Transform right
    np.array([0, 1]) # Transform bottom
]

class Level(Component):
    def __init__(self, level_mat):
        self.is_complete = False
        super(Level, self).__init__(160, 26, (15, 8), True)
        self.level_mat = np.zeros((32, 26), dtype=np.object)
        self.level_mat[:level_mat.shape[0], :level_mat.shape[1]] = level_mat
        self.render_mat = np.zeros((self.width, self.height))
        self.animated_bricks = []
        self.cont = []
        for layer_num in range(26):
            for brick_num in range(32):
                brick = self.level_mat[brick_num, layer_num]
                if brick is not None and brick != 0:
                    brick_loc = Level.brick_to_screen_transform([brick_num, layer_num])
                    self.update_brick_render(brick_loc, brick)

                    if brick.is_animated:
                        self.animated_bricks.append((brick_loc, brick))
                    
                    coord = np.array([brick_num, layer_num])
                    if isinstance(brick, BlockExplosive) and not Level.coords_in_array(coord, self.cont):
                        self.cont = self.find_contiguous_bricks(coord)
                else:
                    self.level_mat[brick_num, layer_num] = None
    
    @staticmethod
    def coords_in_array(coord, array):
        return any((coord == x).all() for x in array)
    
    def find_contiguous_bricks(self, brick):
        def is_valid_coord(coord):
            return np.all(np.zeros(2) <= coord) and np.all(coord < self.level_mat.shape)
        contiguous_bricks = []
        bfs_queue = [brick]
        while len(bfs_queue) != 0:
            coord = bfs_queue.pop(0)
            x, y = coord
            # First check if the brick is a valid one and then check if it has not been visited and then check if it is a valid brick (should not be None)
            if is_valid_coord(coord) and not Level.coords_in_array(coord, contiguous_bricks) and self.level_mat[x, y] is not None and self.level_mat[x, y] != 0:
                contiguous_bricks.append(coord) # Mark it visited
                brick = self.level_mat[x, y]
                if isinstance(brick, BlockExplosive):
                    # Continue DFS in this direction and check the surrounding spaces
                    for transform in brick_adjacency:
                        scoord = coord + transform
                        if is_valid_coord(scoord):
                            sbrick = self.level_mat[scoord[0], scoord[1]]
                            bfs_queue.append(scoord)
        return contiguous_bricks
    
    @staticmethod
    def brick_to_screen_transform(mat_loc):
        return np.array([mat_loc[0] * 5, mat_loc[1], mat_loc[0] * 5 + 5, mat_loc[1] + 1])
    
    def update_brick_render(self, loc, brick):
        self.render_mat[loc[0]:loc[2], loc[1]:loc[3]] = brick.get_render_mat()
    
    def render(self):
        for (brick_loc, brick) in self.animated_bricks:
            self.update_brick_render(brick_loc, brick)
        return self.render_mat
    
    def get_brick_aabb(self, loc):
        if 1 <= loc[0] < 31 and 1 <= loc[1] <= 26:
            loc = loc.astype(int) - np.array([1, 1])
            brick = self.level_mat[loc[0], loc[1]]
            if brick is not None and brick.current_state != 0:
                brick_bounds = Level.brick_to_screen_transform(loc) + np.array([self.start[0], self.start[1], self.start[0], self.start[1]])
                return brick_bounds + np.array([-2, -1, 0, 0])
        return None
    
    def get_surrounding_bricks(self, brick_loc):
        return [self.get_brick_aabb(brick_loc + transform) for transform in brick_adjacency]
    
    @staticmethod
    def break_brick(brick, coords, destruct=True):
        score = brick.current_state * 5
        powerup = None
        if destruct:
            brick.destruct()
        else:
            brick.make_hit()
        # Ball has been destroyed in this hit if the next condition holds, so drop a powerup
        if brick.current_state == 0:
            powerup_class = choice([ExpandPowerup, ShrinkPowerup, SpeedupPowerup, DestructPowerup, GrabPowerup] * 2 +  [SplitPowerup])
            if random() < 0.1:
                powerup = powerup_class(coords)
        
        return score, powerup

    def handle_brick_hits(self, cur_brick_loc, collided_bricks, destruct=False):
        powerup = None
        score = 0
        for brick_transform_index in collided_bricks:
            brick_mat_loc = cur_brick_loc + brick_adjacency[brick_transform_index]
            brick_mat_loc = brick_mat_loc.astype(int) - np.array([1, 1])
            brick_screen_loc = Level.brick_to_screen_transform(brick_mat_loc)
            brick = self.level_mat[brick_mat_loc[0], brick_mat_loc[1]]

            if brick and brick.current_state != 0:
                # Check if it is an eplosive brick and break accordingly
                if isinstance(brick, BlockExplosive) and Level.coords_in_array(brick_mat_loc, self.cont):
                    for brick_new_mat_loc in self.cont:
                        brick_new_screen_loc = Level.brick_to_screen_transform(brick_new_mat_loc)
                        brick_new = self.level_mat[brick_new_mat_loc[0], brick_new_mat_loc[1]]
                        Level.break_brick(brick_new, (brick_new_screen_loc[0] + self.start[0], brick_new_screen_loc[1] + self.start[1]), destruct=True)
                        self.update_brick_render(brick_new_screen_loc, brick_new)
                else:
                    score_new, powerup_new = Level.break_brick(brick, (brick_screen_loc[0] + self.start[0], brick_screen_loc[1] + self.start[1]), destruct=destruct)
                    score += score_new
                    powerup = powerup_new if powerup_new is not None else powerup
                self.update_brick_render(brick_screen_loc, brick)
        
        return powerup, score
    
    def collide_level(self, ball):
        ball_bbox = np.array([ball.start[0], ball.start[1], ball.width + ball.start[0], ball.height + ball.start[1]])
        brick_loc = np.ceil((ball_bbox[:2] - np.array([14, 7])) / np.array([5, 1]))

        collision_change = np.array([False, False])

        surrounding_bricks = self.get_surrounding_bricks(brick_loc)
        collided_bricks = []
        powerup = None

        for (index, brick_aabb) in enumerate(surrounding_bricks):
            if brick_aabb is not None:
                is_collided = collide_outer(ball_bbox, brick_aabb, ball.vel_dir)
                collision_change = np.logical_or(collision_change, is_collided)

                if is_collided[0] ^ is_collided[1]:
                    collided_bricks.append(index)
        
        powerup, score = self.handle_brick_hits(brick_loc, collided_bricks, ball.destruct_ready)

        # If ball is destruction ready, then dont change collision at all
        if ball.destruct_ready:
            collision_change = np.array([False, False])
        
        completed = True
        for layer in self.level_mat:
            for brick in layer:
                if brick is not None and brick.current_state != 0 and not isinstance(brick, BlockInfHit):
                    completed = False
                    break
        self.is_complete = completed

        return collision_change, powerup, score
