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
    scripts_to_import = ['impossibleStairs.py', 'scene.py', 'camera.py' , 'ball.py', 'material_manager.py', 'lights.py']
    print(SCRIPT_DIR)

    # Import the scripts
    for script in scripts_to_import:
        script_path = os.path.join(SCRIPT_DIR, script)
        module_name = script[:-3]  # Remove the .py extension
        globals()[module_name] = import_module(module_name, script_path)

    # Generate stairs model
    stairs_grp = impossibleStairs.generate_stairs()

    # Assign Marble Mat to stairs
    marble_mat = material_manager.import_mat(SCRIPT_DIR, 'marble')
    if marble_mat:
        material_manager.assign_material_to_object(marble_mat, stairs_grp)

    # Set up Camera
    camera.set_perspective_camera()

    # Get materials needed for walls
    portrait_mats     = material_manager.create_portrait_mats(SCRIPT_DIR)
    brick_mat         = material_manager.create_brick_mat(SCRIPT_DIR)
    frame_edge_shader = lights.create_emissive_shader_frame(emission_color=(0.6, 0.8, 1.0), intensity=5)

    # Generate walls
    scene.create_walls(portrait_mats, brick_mat, frame_edge_shader)

    # Generate floor model
    floor = scene.create_floor()

    # Assign Black Tile Mat to floor
    black_tile_mat = material_manager.import_mat(SCRIPT_DIR, 'black_tile')
    if black_tile_mat:
        material_manager.assign_material_to_object(black_tile_mat, floor)

    # Generate ball
    ball_obj = ball.create_ball()

    # Get ball emissive shader
    shader = lights.create_emissive_shader(ball_obj)

    # Animate ball
    ball.animate_ball_helper(ball_obj, shader)

    # Set up scene lights
    lights.create_area_light()
    lights.create_pt_lights()

main()
