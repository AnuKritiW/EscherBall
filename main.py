"""
Main script for the Maya project: Bouncing Ball on Escher's Impossible Staircase inspired by the Grand Staircase as seen in Harry Potter.

This script initializes the scene, creates the staircase, animates the bouncing ball and sets up the lighting for the scene

Dependencies:
- ball_manager:     Functions for handling ball animation.
- scene:            Functions for scene creation.
- scene_lighting:   Functions for lighting setup.
- escher_stairs:    Functions for generating the staircase.
- material_manager: Functions for material and shading management.
"""

import maya.cmds as cmds
import importlib.util
import os

SCRIPT_DIR = r'/Users/Exhale/Desktop/CAVE/maya-scripts'

# Function to dynamically import a module from a file
def import_module(module_name, file_path):
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

def clear_scene():
    cmds.select(all=True)
    cmds.delete()

def main():
    clear_scene()

    # List of scripts to load
    scripts_to_import = ['escher_stairs.py', 'scene.py', 'camera.py' , 'ball_manager.py', 'material_manager.py', 'scene_lighting.py']
    print(SCRIPT_DIR)

    # Import the scripts
    for script in scripts_to_import:
        script_path = os.path.join(SCRIPT_DIR, script)
        module_name = script[:-3]  # Removes the .py extension
        globals()[module_name] = import_module(module_name, script_path)

    # Generate stairs model
    stairs = escher_stairs.generate_stairs()

    # Assign Marble Mat to stairs
    marble_mat = material_manager.import_mat(SCRIPT_DIR, 'marble')
    if marble_mat:
        material_manager.assign_material_to_object(marble_mat, stairs)

    # Set up Camera
    camera.set_perspective_camera()

    # Get materials needed for walls
    brick_mat         = material_manager.prep_brick_mat(SCRIPT_DIR)
    portrait_mats     = material_manager.prep_portrait_mats(SCRIPT_DIR)
    frame_edge_shader = material_manager.prep_emissive_shader(_shader_name="frame_emissive_shader", _emission_color=(0.6, 0.8, 1.0), _intensity=5)

    # Generate walls
    scene.generate_walls(brick_mat, portrait_mats, frame_edge_shader)

    # Generate floor model
    floor = scene.generate_floor()

    # Assign Black Tile Mat to floor
    black_tile_mat = material_manager.import_mat(SCRIPT_DIR, 'black_tile')
    if black_tile_mat:
        material_manager.assign_material_to_object(black_tile_mat, floor)

    # Generate ball
    ball = ball_manager.generate_ball()

    # Get ball emissive shader
    ball_shader = material_manager.prep_emissive_shader(_shader_name="ball_emissive_shader", _intensity=10, _obj=ball)

    # Animate ball
    ball_manager.setup_ball_animation(ball, ball_shader)

    # Set up scene lights
    scene_lighting.setup_area_light()
    scene_lighting.setup_pt_lights()

main()
