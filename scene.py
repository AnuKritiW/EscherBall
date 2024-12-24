import maya.cmds as cmds
import random

SQ_WALL_SIZE = 67

def apply_emissive_texture_to_faces(_frame, _frame_edges_shader):
    """
    Apply the same emissive texture to faces 1, 3, 4, and 5 of a cube.
    """
    if not cmds.objExists(_frame):
        return

    # List of specific faces to apply the texture
    target_faces = [f"{_frame}.f[1]", f"{_frame}.f[3]", f"{_frame}.f[4]", f"{_frame}.f[5]"]

    # Assign the shader to each face
    for face in target_faces:
        cmds.select(face, replace=True)
        cmds.hyperShade(assign=_frame_edges_shader)

def is_overlap(_x_pos, _y_pos, _fr_width, _fr_height, _frame_data_list):
    for frame_data in _frame_data_list:
        curr_fr_x, curr_fr_y, curr_fr_width, curr_fr_height = frame_data

        min_dist_between_fr = 0.2
        # Check for overlap by comparing bounding boxes
        if not ((_x_pos + (_fr_width / 2)  + min_dist_between_fr) < (curr_fr_x - (curr_fr_width  / 2)) or
                (_x_pos - (_fr_width / 2)  - min_dist_between_fr) > (curr_fr_x + (curr_fr_width  / 2)) or
                (_y_pos + (_fr_height / 2) + min_dist_between_fr) < (curr_fr_y - (curr_fr_height / 2)) or
                (_y_pos - (_fr_height / 2) - min_dist_between_fr) > (curr_fr_y + (curr_fr_height / 2))):
            return True

    return False

def is_frame_placed_on_wall(_fr_width, _fr_height, _frame_data_list, _wall_size):
    # Try upto 300 times to place the frame
    max_attempts = 300
    for _ in range(max_attempts):

        # Randomly choose a position for the frame
        x_pos = random.uniform(((-_wall_size / 2) + (_fr_width / 2)), ((_wall_size / 2) - (_fr_width / 2)))
        y_pos = random.uniform((_fr_height / 2), (_wall_size - (_fr_height / 2)))

        # Check if the frame overlaps with any existing frames
        if not is_overlap(x_pos, y_pos, _fr_width, _fr_height, _frame_data_list):
            cmds.move(x_pos, y_pos, 0.25)  # Slight offset to keep frame on the wall
            _frame_data_list.append((x_pos, y_pos, _fr_width, _fr_height))
            return True

    return False

def generate_frame(_width, _height):
    frame = cmds.polyCube(w = _width, h = _height, d = 0.2, name = "Rectangular_Frame")[0]
    return (frame, _width, _height)

def hang_frames(_portrait_mats, _frame_edges_shader):
    num_frames = 400
    frame_data_list = []
    frame_list = []
    for _ in range(num_frames):
        frame, fr_width, fr_height = generate_frame(p_width = random.uniform(8, 12), p_height = random.uniform(8, 12))

        # If placement fails, delete the frame
        sq_wall_size = (SQ_WALL_SIZE - 3) # padding around the boundaries of the wall

        if not is_frame_placed_on_wall(fr_width, fr_height, frame_data_list, sq_wall_size):
            cmds.delete(frame)
        else:
            cmds.select(frame + '.f[0]')  # Select the front face
            cmds.hyperShade(assign=random.choice(_portrait_mats))

            cmds.select(frame + '.f[0]')  # Select the front face

            cmds.polyAutoProjection(frame + '.f[0]', lm=0, ibd=True, sc=2)

            # If the portrait is landscape, polyAutoProjection would have rotated the texture for optimal fit
            # so we need to rotate the UVs back to the original orientation
            if fr_width > fr_height:
                cmds.polyEditUV(frame + '.f[0]', r=True, angle=90)  # Rotate the UVs by 90 degrees

            apply_emissive_texture_to_faces(frame, _frame_edges_shader)

            frame_list.append(frame)

    return frame_list

def generate_single_wall(_transform_dict, _wall_name, _brick_mat, _portrait_mats, _frame_edges_shader):
    wall = cmds.polyCube(w = _transform_dict['sx'], h = _transform_dict['sy'], d = _transform_dict['sz'], name = _wall_name)[0]
    cmds.move(0, _transform_dict['sy'] / 2, 0)

    cmds.select(wall)
    cmds.hyperShade(assign=_brick_mat)

    frames_list = hang_frames(_portrait_mats, _frame_edges_shader)
    frames_grp = cmds.group(frames_list, name = "Frames")

    wall_with_frames = cmds.group([wall, frames_grp], name = (_wall_name + "_with_Frames"))

    cmds.xform(wall_with_frames,
        t  = [_transform_dict['tx'], _transform_dict['ty'], _transform_dict['tz']],
        ro = [_transform_dict['rx'], _transform_dict['ry'], _transform_dict['rz']],
        ws = True)

    return wall_with_frames

def generate_walls(_brick_mat, _portrait_mats, _frame_edges_shader):
    # left wall
    transform_dict = {'tx': -10.571,
                      'ty': -33,
                      'tz': 42.109,
                      'rx': 0,
                      'ry': 180,
                      'rz': 0,
                      'sx': SQ_WALL_SIZE,
                      'sy': SQ_WALL_SIZE,
                      'sz': 0.2}
    left_wall = generate_single_wall(transform_dict, "Left_Wall",   _brick_mat, _portrait_mats, _frame_edges_shader)

    # right wall
    transform_dict['tx'] = -42.995
    transform_dict['tz'] = 8.603
    transform_dict['ry'] = 89.478 # Rotate to help with the illusion
    right_wall = generate_single_wall(transform_dict, "Right_Wall", _brick_mat, _portrait_mats, _frame_edges_shader)

    walls_grp = cmds.group([left_wall, right_wall], name = "Walls")
    cmds.xform(walls_grp,
               t = (11.637219585894766, 0, -32.82290721133882),
               ro = (0.0, -131.41189034927982, 0.0))

def generate_floor():
    floor = cmds.polyCube(d = 120, h = 0.2, w = 120)[0]
    cmds.xform(floor, t = [0, -33, 7], ro = [0, 48, 0])

    return floor
