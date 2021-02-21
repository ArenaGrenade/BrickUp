import numpy as np
from ..utils.vectors import Direction, get_direction

def collide_inner(self_aabb, other_aabb):
    is_collided = np.concatenate((self_aabb[:2] <= other_aabb[:2], self_aabb[2:] >= other_aabb[2:]))
    return np.array([is_collided[0] or is_collided[2], is_collided[1] or is_collided[3]])

def collide_outer(self_aabb, other_box, vel_dir):
    collision_change = np.array([False, False])
    
    # Find the maximal velocity direction
    velocity_direction = get_direction(vel_dir)

    # Left bar collision
    if self_aabb[0] == other_box[0] and (other_box[1] <= self_aabb[1] <= other_box[3]) and velocity_direction == Direction.Right:
        collision_change[0] = True
    
    # Top bar collision
    if self_aabb[1] == other_box[1] and (other_box[0] <= self_aabb[ 0] <= other_box[2]) and velocity_direction == Direction.Down:
        collision_change[1] = True

    # Right bar collision
    if self_aabb[0] == other_box[2] and (other_box[1] <= self_aabb[1] <= other_box[3]) and velocity_direction == Direction.Left:
        collision_change[0] = True
    
    # Bottom bar collision
    if self_aabb[1] == other_box[3] and (other_box[0] <= self_aabb[0] <= other_box[2]) and velocity_direction == Direction.Up:
        collision_change[1] = True
    
    # # If collision happens in both directions - we hit a corner. Hence, revert it.
    if collision_change[0] and collision_change[1]:
        collision_change = np.invert(collision_change)
    
    return collision_change
