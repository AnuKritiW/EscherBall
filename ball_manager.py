"""
Manages the ball animation and interactions.

This module contains functions to:
- Create the ball geometry.
- Animate the ball along the staircase.
- Calculate its position and ensure seamless looping.

Functions:
- generate_ball():        Generates the ball's geometry.
- setup_ball_animation(): Prepares the ball and applies the animation.
- get_stairs_info():      Retrieves information about all stairs in the scene.
- get_top_center():       Computes the top-center position of a staircase step.
- animate_ball():         Sets keyframes for the ball's motion.
- get_interpolated_vals(): Calculates interpolated values between two points.

Key Details:
- Ball animations rely on step positions derived from `get_stairs_info()`.
"""

import maya.cmds as cmds
import random

BALL_RADIUS = 1

def get_interpolated_vals(_t, _start_pt, _end_pt):
    # Calculate interpolated values for x, y, z
    return [
        ((1 - _t) * _start_pt[idx] + (_t * _end_pt[idx]))
        for idx in range(3)
    ]

def animate_ball(_ball, _ball_shader, _step_top_coords):
    """
    Animates the specified ball object along a series of fixed points, changing its emissive color each time it lands on a step.

    This function moves the ball between each point in the provided `step_top_coords` list, setting keyframes for its position to create a bouncing effect. 
    It calculates keyframe intervals based on the total number of points and ensures smooth movement. The ball's emissive color is updated via the shader 
    every time it lands on a step.

    Args:
        _ball (str): The name of the ball object to animate.
        _ball_shader (str): The name of the shader applied to the ball, used to change its emissive color.
        _step_top_coords (list): A list of tuples representing the (x, y, z) coordinates for the ball to traverse.

    Returns:
        None
    """
    fps = 25
    duration = 10 # Total duration of the animation in seconds
    total_frames = fps * duration
    num_points = len(_step_top_coords)

    interval = ((total_frames / (num_points - 1)) if (num_points > 1) else 0)  # Time per section between two points

    # Set the exact position and color at the first step
    cmds.xform(_ball, t=_step_top_coords[0])
    cmds.setKeyframe(_ball, t=0, attribute='translate')

    # Initial ball size keyframes
    cmds.setKeyframe(_ball, t=0, attribute='scaleX', value=1)
    cmds.setKeyframe(_ball, t=0, attribute='scaleY', value=1)
    cmds.setKeyframe(_ball, t=0, attribute='scaleZ', value=1)

    # Change emissive color at the first step
    cmds.setAttr(f"{_ball_shader}.emissionColor", 1, 0, 0, type="double3")  # Start with red
    cmds.setKeyframe(f"{_ball_shader}.emissionColor", t=0)

    bounce_height = 5   # The maximum height the ball will reach during each bounce, relative to the base height of the steps. Higher values create more pronounced bounces.
    bounce_factor = 4   # A scaling factor that affects the width and steepness of the parabolic bounce curve. Larger values result in a steeper bounce, while smaller values create a flatter, more gradual bounce.
    squash_factor = 0.3 # How much the ball should squash. The higher the value, the squishier the ball.

    # Interpolate between points for the bounces
    for i in range(num_points - 1):
        start_pt = _step_top_coords[i]
        end_pt = _step_top_coords[i + 1]

        # For every frame within the bounce between two steps
        for frame in range(int(i * interval), int((i + 1) * interval)):
            t = (frame - i * interval) / interval  # Normalized time between 0 and 1

            # Calculate the interpolated x and z values
            x, y_base, z = get_interpolated_vals(t, start_pt, end_pt)

            # Apply the parabolic bounce
            bounce = (bounce_height * (1 - (bounce_factor * ((t - 0.5) ** 2))))
            y = (y_base + max(0, bounce))

            # Squash and stretch based on position
            if bounce > 0:  # Ball is in mid-air, apply stretch
                scale_xz = 1 - (squash_factor * (bounce / bounce_height))
                scale_y = 1 + (squash_factor * (bounce / bounce_height))
            else:  # Ball is at or near ground, apply squash
                scale_xz = 1 + squash_factor
                scale_y = 1 - squash_factor

            # Apply the translation
            cmds.xform(_ball, t=(x, y, z))
            cmds.setKeyframe(_ball, t=frame, attribute='translate')

            # Set squash/stretch keyframes
            cmds.setKeyframe(_ball, t=frame, attribute='scaleX', value=scale_xz)
            cmds.setKeyframe(_ball, t=frame, attribute='scaleY', value=scale_y)
            cmds.setKeyframe(_ball, t=frame, attribute='scaleZ', value=scale_xz)

        # Change emissive color when the ball lands on a step
        color = [random.random(), random.random(), random.random()]  # Generate random color
        cmds.setAttr(f"{_ball_shader}.emissionColor", *color, type="double3")
        cmds.setKeyframe(f"{_ball_shader}.emissionColor", t=(i + 1) * interval)

    # Set the exact position at the last step
    cmds.xform(_ball, t=_step_top_coords[-1])
    cmds.setKeyframe(_ball, t=total_frames, attribute='translate')

    # Final scale keyframes to reset to original size at end
    cmds.setKeyframe(_ball, t=total_frames, attribute='scaleX', value=1)
    cmds.setKeyframe(_ball, t=total_frames, attribute='scaleY', value=1)
    cmds.setKeyframe(_ball, t=total_frames, attribute='scaleZ', value=1)

def get_top_centre(p_step_name):
    """
    Calculates the top center coordinate of a given step.

    Args:
        step_name (str): The name of the step object in the scene.

    Returns:
        list: A list of [x, y, z] coordinates representing the top center of the step.
    """

    # Get the bounding box of the step
    bounding_box = cmds.xform(p_step_name, query=True, boundingBox=True, ws=True) # [xmin, ymin, zmin, xmax, ymax, zmax].

    top_center = [
            (bounding_box[0] + bounding_box[3]) / 2,  # X average
            bounding_box[4] + BALL_RADIUS, # Y max (top)
            (bounding_box[2] + bounding_box[5]) / 2   # Z average
        ]

    return top_center

def get_stairs_info():
    """
    Retrieves detailed information about all stairs in the scene and organizes it into a structured dictionary.

    The resulting dictionary contains:
    - Keys: Names of stair groups (e.g., 'First_Step', 'Flight_of_Stairs_1').
    - Values: Lists of tuples, where each tuple contains:
        - [0]: The name of a step within the group.
        - [1]: The (x, y, z) coordinates of the top center of the step.

    Example:
        {
            'First_Step': [('First_Step', (x, y, z))],
            'Flight_of_Stairs_1': [('pCube1', (x, y, z)), ('pCube2', (x, y, z))],
            ...
        }

    Returns:
        dict: A dictionary containing the names of stairs as keys and their respective step information as values.
    """

    stairs_info = {'First_Step' : [('First_Step', get_top_centre('First_Step'))]}

    for flight_idx in range(1,5): #TODO: abstract out number of flights of stairs
        flight_name = ('Flight_of_Stairs_' + str(flight_idx)) # TODO: abstract name out
        step_names_in_flight = cmds.ls(cmds.listRelatives(flight_name, children=True), shortNames=True)
        stairs_info[flight_name] = []
        for step_name in step_names_in_flight:
            stairs_info[flight_name].append((step_name, (get_top_centre(step_name))))

    return stairs_info

def setup_ball_animation(_ball, _ball_shader):
    """
    Sets up the animation sequence for the ball.

    This function initializes the ball's position and animates it along
    the stairs' top coordinates.

    Args:
        ball (str): The name of the ball object to animate.
        shader (str): The shader applied to the ball.

    Returns:
        str: The name of the ball object after animation setup.
    """

    step_top_coords = [coord for value in get_stairs_info().values() for _, coord in value]
    step_top_coords.append(step_top_coords[0]) # To ensure the loop is complete
    step_top_coords.reverse()  # So the ball is descending instead of ascending

    cmds.xform(_ball, t = step_top_coords[0])

    animate_ball(_ball, _ball_shader, step_top_coords)

    return _ball

def generate_ball():
    """
    Creates a ball object in the Maya scene.

    Returns:
        str: The name of the created ball object.
    """
    return cmds.polySphere(radius=BALL_RADIUS)[0]