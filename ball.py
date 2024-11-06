import maya.cmds as cmds

BALL_RADIUS = 1
"""
Create a dictionary of the stairs information in the scene.
The dictionary will follow the structure below
keys: string names
values: list of tuples
        each tuple contains the step name at [0] and the center coordinate at [1]
e.g.
stair_info
{
    'First_Step' : [('First_Step', (x, y, z))],
    'Flight_of_Stairs_1' : [('pCube1', (x, y, z)), ('pCube2', (x, y, z), ...)]
    ...
}
"""
def get_stairs_info():
    stairs_info = {'First_Step' : [('First_Step', get_top_centre('First_Step'))]}

    for flight_idx in range(1,5): #TODO: abstract out number of flights of stairs
        flight_name = ('Flight_of_Stairs_' + str(flight_idx)) # TODO: abstract name out
        step_names_in_flight = cmds.ls(cmds.listRelatives(flight_name, children=True), shortNames=True)
        stairs_info[flight_name] = []
        for step_name in step_names_in_flight:
            stairs_info[flight_name].append((step_name, (get_top_centre(step_name))))

    return stairs_info

def get_top_centre(p_step_name):
    # Get the bounding box of the step
    bounding_box = cmds.xform(p_step_name, query=True, boundingBox=True, ws=True) # [xmin, ymin, zmin, xmax, ymax, zmax].

    top_center = [
            (bounding_box[0] + bounding_box[3]) / 2,  # X average
            bounding_box[4] + BALL_RADIUS, # Y max (top)
            (bounding_box[2] + bounding_box[5]) / 2   # Z average
        ]

    return top_center

def get_interpolated_vals(p_t, p_start_pt, p_end_pt):
    # Calculate interpolated values for x, y, z
    return [
        ((1 - p_t) * p_start_pt[idx] + (p_t * p_end_pt[idx]))
        for idx in range(3)
    ]

"""
Animate the specified ball object along a series of fixed points.

The ball moves between each point in the provided list `fixed_pts`, setting keyframes for each position over a specified duration and frame rate.
The function calculates the interval for keyframes based on the total number of points and animates the ball to give the appearance of bouncing down steps.

Parameters:
    p_ball (str): The name of the ball object to animate.
    p_step_top_coords (list): A list of tuples representing the (x, y, z) coordinates for the ball to traverse.
    fps (int): Frames per second for the animation (default is 25).
    duration (int): Total duration of the animation in seconds (default is 10).
    bounce_height (float): The maximum height the ball will reach during each bounce, relative to the base height of the steps. Higher values create
                           more pronounced bounces.
    bounce_factor (float): A scaling factor that affects the width and steepness of the parabolic bounce curve. Larger values result in a steeper bounce,
                           while smaller values create a flatter, more gradual bounce.
"""
def animate_ball(p_ball, p_step_top_coords, fps=25, duration=10, bounce_height=5, bounce_factor=4, squash_factor=0.2):
    total_frames = fps * duration
    num_points = len(p_step_top_coords)

    interval = ((total_frames / (num_points - 1)) if (num_points > 1) else 0)  # Time per section between two points

    # Set the exact position at the first step
    cmds.xform(p_ball, t=p_step_top_coords[0])
    cmds.setKeyframe(p_ball, t=0, attribute='translate')

    # Initial ball size keyframes
    cmds.setKeyframe(p_ball, t=0, attribute='scaleX', value=1)
    cmds.setKeyframe(p_ball, t=0, attribute='scaleY', value=1)
    cmds.setKeyframe(p_ball, t=0, attribute='scaleZ', value=1)

    # Interpolate between points for the bounces
    for i in range(num_points - 1):
        start_pt = p_step_top_coords[i]
        end_pt = p_step_top_coords[i + 1]

        # For every frame within the bounce between two steps
        for frame in range(int(i * interval), int((i + 1) * interval)):
            t = (frame - i * interval) / interval  # Normalized time between 0 and 1

            # Calculate the interpolated x and z values
            # Linear interpolation for the y base --> ensure the base y value from p_step_top_coords is maintained
            x, y_base, z = get_interpolated_vals(t, start_pt, end_pt)

            # Apply the parabolic bounce
            """
            Calculate the bounce height based on a parabolic equation.
            The equation models the vertical motion of the ball, peaking at the midpoint (t = 0.5) with a maximum height of `bounce_height`.
            The bounce_factor adjusts the width of the parabola, controlling how steep the bounce is. 
            As `t` approaches 0 or 1, the bounce value approaches zero, ensuring the ball is at the step height at the start and end of its motion.
            """
            bounce = (bounce_height * (1 - (bounce_factor * ((t - 0.5) ** 2))))

            """
            Ensure the bounce only adds height --> so the ball does not intesect the step
            Note that when (bounce < 0), it means we do not have a perfect parabola beyond the halfway point
            i.e. it follows the parabola until we hit the step, and then the curve flattens out instead of going negative
            """
            y = (y_base + max(0, bounce))

            # Squash and stretch based on position
            if bounce > 0:  # Ball is in mid-air, apply stretch
                scale_xz = 1 - (squash_factor * (bounce / bounce_height))
                scale_y = 1 + (squash_factor * (bounce / bounce_height))
            else:  # Ball is at or near ground, apply squash
                scale_xz = 1 + squash_factor
                scale_y = 1 - squash_factor

            # Apply the translation
            cmds.xform(p_ball, t=(x, y, z))
            cmds.setKeyframe(p_ball, t=frame, attribute='translate')

            # Set squash/stretch keyframes
            cmds.setKeyframe(p_ball, t=frame, attribute='scaleX', value=scale_xz)
            cmds.setKeyframe(p_ball, t=frame, attribute='scaleY', value=scale_y)
            cmds.setKeyframe(p_ball, t=frame, attribute='scaleZ', value=scale_xz)

    # Set the exact position at the last step
    cmds.xform(p_ball, t=p_step_top_coords[-1])
    cmds.setKeyframe(p_ball, t=total_frames, attribute='translate')

    # Final scale keyframes to reset to original size at end
    cmds.setKeyframe(p_ball, t=total_frames, attribute='scaleX', value=1)
    cmds.setKeyframe(p_ball, t=total_frames, attribute='scaleY', value=1)
    cmds.setKeyframe(p_ball, t=total_frames, attribute='scaleZ', value=1)



def create_and_animate_ball():
    step_top_coords = [coord for value in get_stairs_info().values() for _, coord in value]
    step_top_coords.append(step_top_coords[0]) # To ensure the loop is complete
    step_top_coords.reverse()  # So the ball is descending instead of ascending

    ball = cmds.polySphere(radius=BALL_RADIUS)[0]
    cmds.xform(ball, t = step_top_coords[0])

    animate_ball(ball, step_top_coords)