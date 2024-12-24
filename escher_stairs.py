import maya.cmds as cmds

SQ_STEP_SIZE = 2

def create_step(p_step_height, p_coord_dict):
    curr_step = cmds.polyCube(w = SQ_STEP_SIZE, h = p_step_height, d = SQ_STEP_SIZE)[0]

    # Ensure that the newly created step is the active selection
    cmds.select(curr_step)

    # Move pivot to the bottom of the step (Y = -p_step_height / 2)
    cmds.xform(curr_step, pivots=(0, (-p_step_height / 2), 0), ws = True)

    # Move the step so its base aligns with Y = 0 and position it along the X-axis
    cmds.move(p_coord_dict['x'], (p_step_height / 2), p_coord_dict['z'], curr_step, ws = True)  # y = (p_step_height / 2) keeps the base at Y=0

    return ((p_step_height + 0.25), curr_step)

def generate_flight_of_stairs(p_coord_dict, p_x_delta, p_z_delta, p_step_height, p_num_steps_in_flight, p_flight_num):
    num_steps = 0
    steps = []
    while num_steps < p_num_steps_in_flight:
        p_coord_dict['x'] += p_x_delta
        p_coord_dict['z'] += p_z_delta
        p_step_height, step = create_step(p_step_height, p_coord_dict)
        steps.append(step)
        num_steps += 1

    steps_grp = cmds.group(steps, name = ("Flight_of_Stairs_" + str(p_flight_num)))
    return (p_step_height, steps_grp)

def generate_stairs():
    num_steps = 0
    step_height = 20
    coord_dict = {'x': -6, 'z': 4} # Values arbitrarily decided after manual testing

    # Generate the first step and extrude its front face
    step_height, first_step = create_step(step_height, coord_dict)

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