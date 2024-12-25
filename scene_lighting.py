"""
Configures lighting for the 3D scene.

This module provides functions to:
- Add and configure area and point lights.
- Calculate light positions based on object normals.
- Create realistic lighting setups for rendering.

Functions:
- setup_area_light():               Creates an Arnold area light with custom attributes.
- get_face_normal_in_world_space(): Computes the normal vector of a polygon face.
- setup_single_pt_light():          Adds a point light near a specific frame.
- setup_pt_lights():                Generates multiple point lights for the scene.

Details:
- Uses Maya's Arnold renderer for area lights.
- Lights are placed dynamically based on frame positions.
"""

import maya.cmds as cmds
import maya.api.OpenMaya as om

def setup_area_light():
    """
    Creates and configures an Arnold area light in the Maya scene.

    This function ensures the Arnold plugin is loaded, creates an area light with a specific
    name, and sets its properties such as color, intensity, and exposure. It also places the
    light in the default light set.

    Returns:
        None
    """

    # Ensure the Arnold plugin is loaded
    if not cmds.pluginInfo('mtoa', query=True, loaded=True):
        cmds.loadPlugin('mtoa')

    light_name = "brown_area_light"

    # Create a transform node with a specific name
    light_transform = cmds.createNode('transform', name=light_name)

    # Create an Arnold area light shape as a child of the transform node
    light_shape = cmds.createNode('aiAreaLight', name= (light_name + 'Shape'), parent=light_transform)

    # Apply transformations using xform on the transform node
    cmds.xform(light_transform, translation=(0, 32.969, -0.788),    worldSpace=True)
    cmds.xform(light_transform, rotation=(-90.085, 47.608, -0.063), worldSpace=True)
    cmds.xform(light_transform, scale=(41.011, 41.011, 41.011))

    # Set Arnold area light attributes on the shape node
    cmds.setAttr(f'{light_shape}.color',     0.301, 0.181, 0.114, type='double3')
    cmds.setAttr(f'{light_shape}.intensity', 7.869)
    cmds.setAttr(f'{light_shape}.exposure',  0.249)
    cmds.setAttr(f'{light_shape}.normalize', 0    ) # Disable normalization

    cmds.connectAttr(f'{light_transform}.instObjGroups', 'defaultLightSet.dagSetMembers', nextAvailable=True)

def get_face_normal_in_world_space(_mesh, _face_index=0):
    """
    Calculates the world-space normal vector for a specified face of a mesh.

    Args:
        _mesh (str): The name of the mesh object.
        _face_index (int): The index of the face to calculate the normal for. Defaults to 0.

    Returns:
        list: A normalized vector [x, y, z] representing the face's normal in world space.
    """

    # Create a selection list and get the DAG path
    sel_list = om.MSelectionList()
    sel_list.add(_mesh)
    dag_path = sel_list.getDagPath(0)

    # Create an MFnMesh function set for the mesh
    mesh_fn = om.MFnMesh(dag_path)

    # Get the normal for the specified face in world space
    normal_vector = mesh_fn.getPolygonNormal(_face_index, om.MSpace.kWorld)
    normal_vector.normalize()  # Ensure the normal is a unit vector

    return [normal_vector.x, normal_vector.y, normal_vector.z]

def setup_single_pt_light(_frame):
    """
    Creates a point light positioned relative to a frame's front face normal.

    This function calculates the position of the light based on the normal vector
    of the front face of the given frame. The light's intensity is dynamically adjusted
    based on its height in the scene.

    Args:
        _frame (str): The name of the frame object to position the light near.

    Returns:
        str: The name of the created point light shape.
    """

    # Get the current position of the frame
    pos = cmds.xform(_frame, query=True, worldSpace=True, translation=True)

    cmds.select(_frame + '.f[0]')  # Select the front face
    normal = get_face_normal_in_world_space(_frame)

    distance = 1.5

    # Calculate the new position for the light along the normal vector
    light_position = [pos[0] + normal[0] * distance,
                      pos[1] + normal[1] * distance,
                      pos[2] + normal[2] * distance]

    # Create the point light and position it
    light_shape = cmds.pointLight()
    light_transform = cmds.listRelatives(light_shape, parent=True)[0]  # Get the transform node

    cmds.xform(light_transform, worldSpace=True, translation=light_position)

    y_position = light_position[1]
    max_intensity = 30.0
    mid_intensity = 20.0
    min_intensity = 10.0

    # Map the Y position to intensity
    intensity = mid_intensity + (y_position * 1.0)
    intensity = max(min_intensity, min(intensity, max_intensity))

    cmds.setAttr(light_shape + ".intensity", intensity)
    cmds.setAttr(f'{light_shape}.color', 1, 1, 1, type='double3')

    return light_shape

def setup_pt_lights():
    """
    Creates and groups point lights for all rectangular frames in the scene.

    This function iterates over all rectangular frame objects, creates a point light for
    each frame using `setup_single_pt_light()`, and groups the resulting lights under a
    single parent node.

    Returns:
        str: The name of the group containing all created point lights.
    """

    rectangular_frames = cmds.ls('Rectangular_Frame*', long=True) # Name decided in scene.create_frame
    pt_lights = []

    for frame in rectangular_frames:
        if 'Rectangular_Frame' in frame and cmds.objectType(frame) == 'transform':
            light_shape = setup_single_pt_light(frame)
            pt_lights.append(light_shape)

    lights_grp = cmds.group(pt_lights, name = "point_lights")
    return lights_grp
