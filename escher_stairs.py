"""
Procedurally generates an Escher-inspired staircase.

This module provides functions to:
- Create individual steps with precise positioning.
- Assemble flights of stairs with customizable parameters.
- Group the staircase components into a single structure.

Functions:
- generate_step():             Creates a single step at a specified position.
- generate_flight_of_stairs(): Assembles a series of steps into a flight.
- generate_stairs():           Constructs the complete staircase with multiple flights.

Details:
- Step dimensions and placements are determined programmatically.
- Flights are grouped and rotated for a cohesive structure.
"""

import maya.cmds as cmds

SQ_STEP_SIZE = 2

def generate_step(_step_height, _coord_dict):
    """
    Generates a single step in the staircase.

    This function creates a step (a cube) with the specified height and positions it
    at the coordinates defined in `_coord_dict`.

    Args:
        _step_height (float): The height of the step.
        _coord_dict (dict): A dictionary containing the current coordinates
                            for placing the step (keys: 'x', 'z').

    Returns:
        tuple: A tuple containing the updated step height and the name of the created step object.
    """

    curr_step = cmds.polyCube(w = SQ_STEP_SIZE, h = _step_height, d = SQ_STEP_SIZE)[0]

    # Ensure that the newly created step is the active selection
    cmds.select(curr_step)

    # Move pivot to the bottom of the step (Y = -_step_height / 2)
    cmds.xform(curr_step, pivots=(0, (-_step_height / 2), 0), ws = True)

    # Move the step so its base aligns with Y = 0 and position it along the X-axis
    cmds.move(_coord_dict['x'], (_step_height / 2), _coord_dict['z'], curr_step, ws = True)  # y = (_step_height / 2) keeps the base at Y=0

    return ((_step_height + 0.25), curr_step)

def generate_flight_of_stairs(_coord_dict, _x_delta, _z_delta, _step_height, _num_steps_in_flight, _flight_num):
    """
    Generates a flight of stairs by creating multiple steps.

    This function creates a sequence of steps with consistent spacing in the X and Z directions
    based on the specified deltas. The steps are grouped together under a single node.

    Args:
        _coord_dict (dict): A dictionary containing the current coordinates (keys: 'x', 'z').
        _x_delta (float): The step increment in the X direction.
        _z_delta (float): The step increment in the Z direction.
        _step_height (float): The height of the first step in the flight.
        _num_steps_in_flight (int): The number of steps in the flight.
        _flight_num (int): The flight number for naming the group.

    Returns:
        tuple: A tuple containing the updated step height and the name of the flight group.
    """

    num_steps = 0
    steps = []
    while num_steps < _num_steps_in_flight:
        _coord_dict['x'] += _x_delta
        _coord_dict['z'] += _z_delta
        _step_height, step = generate_step(_step_height, _coord_dict)
        steps.append(step)
        num_steps += 1

    steps_grp = cmds.group(steps, name = ("Flight_of_Stairs_" + str(_flight_num)))
    return (_step_height, steps_grp)

def generate_stairs():
    """
    Generates the Escher-inspired staircase.

    This function creates an entire staircase consisting of multiple flights of stairs.
    It starts by generating the first step, followed by four flights of stairs, each with
    different directions and step counts. The entire staircase is grouped and rotated for
    optimal viewing.

    Returns:
        str: The name of the group containing the entire staircase.
    """

    num_steps = 0
    step_height = 20
    coord_dict = {'x': -6, 'z': 4} # Values arbitrarily decided after manual testing

    # Generate the first step and extrude its front face
    step_height, first_step = generate_step(step_height, coord_dict)

    first_step = cmds.rename(first_step, "First_Step")

    # Polyextrude the front face of the first step
    cmds.polyExtrudeFacet(first_step + ".f[0]", ltz=0.4)  # ltz determined after manual testing

    num_flights = 0
    step_height, first_flight  = generate_flight_of_stairs(coord_dict, 0,             -SQ_STEP_SIZE, step_height, 6, (num_flights + 1))
    step_height, second_flight = generate_flight_of_stairs(coord_dict, SQ_STEP_SIZE,  0,             step_height, 5, (num_flights + 1))
    step_height, third_flight  = generate_flight_of_stairs(coord_dict, 0,             SQ_STEP_SIZE,  step_height, 4, (num_flights + 1))
    step_height, fourth_flight = generate_flight_of_stairs(coord_dict, -SQ_STEP_SIZE, 0,             step_height, 2, (num_flights + 1))

    stairs_grp = cmds.group([first_step, first_flight, second_flight, third_flight, fourth_flight], name = "escher_stairs")

    # Rotate so we can view the illusion from the front
    cmds.rotate(0, 225, 0, stairs_grp, relative = True)

    return stairs_grp