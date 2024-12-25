"""
Manages materials and shaders for the scene.

This module provides functions to:
- Create materials for portraits, bricks, and emissive shaders.
- Assign materials to scene objects.
- Import existing materials from external files.

Functions:
- prep_single_portrait_mat():  Creates a single portrait material with looping animation.
- prep_portrait_mats():        Prepares portrait materials from image sequences.
- prep_brick_mat():            Creates a brick material for walls.
- assign_material_to_object(): Assigns a material to a specific object.
- import_mat():                Imports materials from external Maya binary files.
- prep_emissive_shader():      Creates and configures an emissive shader.

Details:
- Portrait materials use dynamic frame extensions for animation.
- Brick textures are tiled for realistic appearance.
"""

import os
import maya.cmds as cmds

def prep_single_portrait_mat(_script_dir, _portrait, _offset_level):
    """
    Prepares a single portrait material with looping animation.

    This function creates a material for a specific portrait, links it to an image sequence,
    and configures it for looping playback with a specified offset.

    Args:
        _script_dir (str): The directory path where the portrait textures are stored.
        _portrait (str): The name of the portrait image to use.
        _offset_level (float): The offset level to apply to the animation loop.

    Returns:
        str: The name of the created material.
    """

    image_sequence_path = os.path.join(_script_dir, 'portraits', f'{_portrait}_seq', f'{_portrait}_1.png')

    # Create a new material (Lambert or Phong)
    portrait_mat = cmds.shadingNode('lambert', asShader=True, name=f'{_portrait}_material')
    cmds.setAttr(portrait_mat + '.color', 1, 1, 1, type='double3')  # Default white color

    # Create the File texture node for the image sequence
    file_node = cmds.shadingNode('file', asTexture=True, name='imageSequenceFile')
    cmds.setAttr(file_node + '.fileTextureName', image_sequence_path, type='string')

    # Enable the image sequence
    cmds.setAttr(file_node + '.useFrameExtension', 1)  # Enable frame extension (looping)

    if cmds.attributeQuery('imageCache', node=file_node, exists=True):
        cmds.setAttr(file_node + '.imageCache', 1)


    if cmds.attributeQuery('resolution', node=file_node, exists=True):
        cmds.setAttr(file_node + '.resolution', 256)  # Set to a lower value for preview

    # Connect the texture to the material
    cmds.connectAttr(file_node + '.outColor', portrait_mat + '.color', force=True)

    # Create a new shading group
    shading_group = cmds.sets(renderable=True, noSurfaceShader=True, empty=True, name='imageSequenceSG')
    cmds.connectAttr(portrait_mat + '.outColor', shading_group + '.surfaceShader', force=True)

    # Set the Timeline Range for Playback
    start_frame = 1
    parent_directory = os.path.dirname(image_sequence_path)
    png_files = [f for f in os.listdir(parent_directory) if f.endswith('.png')]
    end_frame = len(png_files) - 1

    frame_offset = 0
    if (_offset_level != 0):
        frame_offset = int(end_frame / _offset_level)

    cmds.playbackOptions(min=start_frame, max=end_frame)
    cmds.playbackOptions(loop="continuous")  # Enable looping for the timeline playback

    # Create an Expression to Loop the Frame Extension Attribute
    expression = f"{file_node}.frameExtension = ((frame + {frame_offset}) % {end_frame}) + 1;"
    cmds.expression(s=expression, o="", ae=True, uc="all")

    return portrait_mat

def prep_portrait_mats(_script_dir):
    """
    Prepares multiple portrait materials for the frames.

    This function generates variations of portrait materials with different offsets for looping animations.

    Args:
        _script_dir (str): The directory path where portrait textures are stored.

    Returns:
        list: A list of generated portrait material names.
    """

    portraits = ['slytherin', 'gryffindor', 'ravenclaw', 'hufflepuff', 'greylady', 'bloodybaron', 'nick', 'fatfriar', 'peeves', 'dumbledore']
    portrait_mats = []

    for portrait in portraits:
        portrait_mats.append(prep_single_portrait_mat(_script_dir, portrait, 0))
        portrait_mats.append(prep_single_portrait_mat(_script_dir, portrait, 1.5))
        portrait_mats.append(prep_single_portrait_mat(_script_dir, portrait, 3))

    return portrait_mats

def prep_brick_mat(_script_dir):
    """
    Prepares a brick material for the walls.

    This function creates a material, assigns a brick texture, and configures UV tiling.

    Args:
        _script_dir (str): The directory path where the brick texture is stored.

    Returns:
        str: The name of the created brick material.
    """

    texture_file_path = os.path.join(_script_dir, 'textures', 'brick-wall-texture.jpg')

    # Create a Lambert material
    material_name = "brickMaterial"
    material = cmds.shadingNode('lambert', asShader=True, name=material_name)

    # Create a file texture node and set its file path
    file_node = cmds.shadingNode('file', asTexture=True, name='brickFileTexture')
    cmds.setAttr(f'{file_node}.fileTextureName', texture_file_path, type='string')

    # Create a 2D texture placement node and connect it to the file node
    place2d_node = cmds.shadingNode('place2dTexture', asUtility=True, name='place2dBrick')
    cmds.connectAttr(f'{place2d_node}.outUV', f'{file_node}.uvCoord')
    cmds.connectAttr(f'{place2d_node}.outUvFilterSize', f'{file_node}.uvFilterSize')

    repeatU=16
    repeatV=24

    # Set repeat UV values to tile the texture
    cmds.setAttr(f'{place2d_node}.repeatU', repeatU)
    cmds.setAttr(f'{place2d_node}.repeatV', repeatV)

    # Connect the file texture's output to the color attribute of the material
    cmds.connectAttr(f'{file_node}.outColor', f'{material}.color')

    # Create a shading group and assign the material to it
    shading_group = cmds.sets(renderable=True, noSurfaceShader=True, empty=True, name=f'{material_name}SG')
    cmds.connectAttr(f'{material}.outColor', f'{shading_group}.surfaceShader', force=True)

    return material

def assign_material_to_object(_mat, _obj):
    """
    Assigns a material to a specific object in the scene.

    Args:
        _mat (str): The name of the material to assign.
        _obj (str): The name of the object to which the material is applied.

    Returns:
        None
    """

    cmds.select(_obj)
    cmds.hyperShade(assign=_mat)

def import_mat(_script_dir, _mat_name):
    """
    Imports a material from a Maya Binary (.mb) file.

    This function loads a material from an external file, identifies the imported materials,
    and returns the name of the first Arnold Standard Surface material found.

    Args:
        _script_dir (str): The directory path where the .mb file is located.
        _mat_name (str): The name of the material to import.

    Returns:
        str or None: The name of the imported Arnold Standard Surface material, or None if not found.
    """

    # List materials in the scene before import
    materials_before_import = set(cmds.ls(materials=True))

    # Specify the file path to the .mb file containing the material
    file_path = os.path.join(_script_dir, 'textures', f'{_mat_name}.mb')
    print(file_path)

    # Import the material with extra options to mimic Hypershade behavior
    cmds.file(file_path, i=True, type='mayaBinary', ignoreVersion=True, mergeNamespacesOnClash=True, namespace=":")

    # List materials in the scene after import
    materials_after_import = set(cmds.ls(materials=True))

    # Identify the new materials by finding the difference
    new_materials = materials_after_import - materials_before_import

    for material in new_materials:
        if cmds.nodeType(material) == 'aiStandardSurface':
            return material

    return None

def prep_emissive_shader(_shader_name, _emission_color=(1, 1, 1), _intensity=40, _obj=None):
    """
    Prepares an emissive shader and optionally assigns it to an object.

    This function creates an Arnold Standard Surface shader, enables emission, and sets the
    emission color and intensity. If an object is provided, the shader is assigned to it.

    Args:
        _shader_name (str): The name of the shader to create.
        _emission_color (tuple): A tuple (R, G, B) representing the emissive color. Defaults to (1, 1, 1).
        _intensity (float): The intensity of the emission. Defaults to 40.
        _obj (str, optional): The name of the object to which the shader will be applied. Defaults to None.

    Returns:
        str: The name of the created shader.
    """

    # Create an Arnold Standard Surface shader
    shader = cmds.shadingNode('aiStandardSurface', asShader=True, name=_shader_name)

    shading_group = cmds.sets(renderable=True, noSurfaceShader=True, empty=True, name=f"{shader}SG")
    cmds.connectAttr(f"{shader}.outColor", f"{shading_group}.surfaceShader", force=True)

    if _obj: # Assign the shader to the object
        cmds.sets(_obj, edit=True, forceElement=shading_group)

    # Enable emission and set its properties
    cmds.setAttr(f"{shader}.emission", _intensity)  # Enable emission
    cmds.setAttr(f"{shader}.emissionColor", *_emission_color, type="double3") # Set emission color
    return shader