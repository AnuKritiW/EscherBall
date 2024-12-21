import os
import maya.cmds as cmds

def create_textures():

    portraits = ['slytherin', 'gryffindor', 'ravenclaw', 'hufflepuff', 'greylady', 'bloodybaron', 'nick', 'fatfriar', 'peeves', 'dumbledore']
    # portraits = ['peeves'] # for testing that textures have different offsets
    materials = []

    # TODO: clean up logic here
    for portrait in portraits:
        materials.append(create_material(portrait, 0))
        materials.append(create_material(portrait, 3))
        materials.append(create_material(portrait, 1.5))

    return materials

def create_material(p_portrait, p_offset_level):
    # image_sequence_path = f'/home/s5647918/Code/maya-scripts/portraits/{p_portrait}_seq/{p_portrait}_1.png'
    image_sequence_path= f'C:/Users/anukr/Desktop/Code/maya-scripts/portraits/{p_portrait}_seq/{p_portrait}_1.png'

    # Create a new material (Lambert or Phong)
    material = cmds.shadingNode('lambert', asShader=True, name=f'{p_portrait}_material')
    cmds.setAttr(material + '.color', 1, 1, 1, type='double3')  # Default white color

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
    cmds.connectAttr(file_node + '.outColor', material + '.color', force=True)

    # Create a new shading group
    shading_group = cmds.sets(renderable=True, noSurfaceShader=True, empty=True, name='imageSequenceSG')
    cmds.connectAttr(material + '.outColor', shading_group + '.surfaceShader', force=True)

    # Set the Timeline Range for Playback
    start_frame = 1
    parent_directory = os.path.dirname(image_sequence_path)
    png_files = [f for f in os.listdir(parent_directory) if f.endswith('.png')]
    end_frame = len(png_files) - 1

    frame_offset = 0
    if (p_offset_level != 0):
        frame_offset = int(end_frame / p_offset_level)

    cmds.playbackOptions(min=start_frame, max=end_frame)
    cmds.playbackOptions(loop="continuous")  # Enable looping for the timeline playback

    # Create an Expression to Loop the Frame Extension Attribute
    # expression = f"{file_node}.frameExtension = (frame % {end_frame}) + 1;"
    expression = f"{file_node}.frameExtension = ((frame + {frame_offset}) % {end_frame}) + 1;"
    cmds.expression(s=expression, o="", ae=True, uc="all")

    return material

def create_brick_material(repeatU=16, repeatV=24):
    material_name="brickMaterial"
    # texture_file_path = f'./textures/brick-wall-texture.jpg'
    texture_file_path = f'C:/Users/anukr/Desktop/Code/maya-scripts/textures/brick-wall-texture.jpg'

    # Create a Lambert material
    material = cmds.shadingNode('lambert', asShader=True, name=material_name)

    # Create a file texture node and set its file path
    file_node = cmds.shadingNode('file', asTexture=True, name='brickFileTexture')
    cmds.setAttr(f'{file_node}.fileTextureName', texture_file_path, type='string')

    # Create a 2D texture placement node and connect it to the file node
    place2d_node = cmds.shadingNode('place2dTexture', asUtility=True, name='place2dBrick')
    cmds.connectAttr(f'{place2d_node}.outUV', f'{file_node}.uvCoord')
    cmds.connectAttr(f'{place2d_node}.outUvFilterSize', f'{file_node}.uvFilterSize')

    # Set repeat UV values to tile the texture
    cmds.setAttr(f'{place2d_node}.repeatU', repeatU)
    cmds.setAttr(f'{place2d_node}.repeatV', repeatV)

    # Connect the file texture's output to the color attribute of the material
    cmds.connectAttr(f'{file_node}.outColor', f'{material}.color')

    # Create a shading group and assign the material to it
    shading_group = cmds.sets(renderable=True, noSurfaceShader=True, empty=True, name=f'{material_name}SG')
    cmds.connectAttr(f'{material}.outColor', f'{shading_group}.surfaceShader', force=True)

    print(f"Material '{material_name}' with tiled brick texture has been created.")
    return material

def assign_material_to_object(material, object):
    print(material)
    cmds.select(object)
    cmds.hyperShade(assign=material)


def import_material(material_name):
    # List materials in the scene before import
    materials_before_import = set(cmds.ls(materials=True))

    # Specify the file path to the .mb file containing the material
    # file_path = '/home/s5647918/Code/maya-scripts/textures/' + material_name + '.mb'
    file_path = f'C:/Users/anukr/Desktop/Code/maya-scripts/textures/' + material_name + '.mb'

    # Import the material with extra options to mimic Hypershade behavior
    cmds.file(file_path, i=True, type='mayaBinary', ignoreVersion=True, mergeNamespacesOnClash=True, namespace=":")

    # List materials in the scene after import
    materials_after_import = set(cmds.ls(materials=True))

    # Identify the new materials by finding the difference
    new_materials = materials_after_import - materials_before_import

    for material in new_materials:
        if cmds.nodeType(material) == 'aiStandardSurface':
            print(f"Found aiStandardSurface material: {material}")
            return material

    return None
