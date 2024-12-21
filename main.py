import maya.cmds as cmds
import importlib.util
import os

# Manually specify the directory where your scripts are located
script_dir = r'C:\Users\anukr\Desktop\Code\maya-scripts'  # Use raw string for Windows path
# script_dir = r'/home/s5647918/Code/maya-scripts'
# TODO: get path dynamically; change path to match machine until then

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
    scripts_to_import = ['impossibleStairs.py', 'scene.py', 'camera.py' , 'ball.py', 'textures.py', 'lights.py']

    for script in scripts_to_import:
        script_path = os.path.join(script_dir, script)
        module_name = script[:-3]  # Remove the .py extension
        globals()[module_name] = import_module(module_name, script_path)

    # Populate scene
    marble_mat = textures.import_material('marble')
    stairs_grp = impossibleStairs.generate_stairs()
    if marble_mat:
        textures.assign_material_to_object(marble_mat, stairs_grp)

    camera.set_perspective_camera()

    materials = textures.create_textures()
    bricks = textures.create_brick_material()
    scene.create_walls(materials, bricks)

    black_tile_mat = textures.import_material('black_tile')
    floor = scene.create_floor()
    if black_tile_mat:
        textures.assign_material_to_object(black_tile_mat, floor)

    ball_obj = ball.create_ball()
    print(f"Ball object created: {ball_obj}")  # Debugging ball creation
    shader = lights.create_emissive_shader(ball_obj)
    print(f"Shader assigned to ball: {shader}")  # Debugging shader assignment
    ball.animate_ball_helper(ball_obj, shader)

    # leather_mat = textures.import_material('leather')
    # animated_ball = ball.create_and_animate_ball()
    # if leather_mat:
    #     textures.assign_material_to_object(leather_mat, animated_ball)

    lights.create_area_light()
    lights.create_pt_lights()
    # lights.make_object_emissive(animated_ball, (0.106, 0.384, 0.839))

main()
