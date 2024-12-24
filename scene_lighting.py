import maya.cmds as cmds
import maya.api.OpenMaya as om
import math as math

def create_area_light():
    # Ensure the Arnold plugin is loaded
    if not cmds.pluginInfo('mtoa', query=True, loaded=True):
        cmds.loadPlugin('mtoa')

    light_name = "brown_area_light"

    # Create a transform node with a specific name
    light_transform = cmds.createNode('transform', name=light_name)

    # Create an Arnold area light shape as a child of the transform node
    light_shape = cmds.createNode('aiAreaLight', name= (light_name + 'Shape'), parent=light_transform)

    # Apply transformations using xform on the transform node
    cmds.xform(light_transform, translation=(0, 32.969, -0.788), worldSpace=True)
    cmds.xform(light_transform, rotation=(-90.085, 47.608, -0.063), worldSpace=True)
    cmds.xform(light_transform, scale=(41.011, 41.011, 41.011))

    # Set Arnold area light attributes on the shape node
    cmds.setAttr(f'{light_shape}.color', 0.301, 0.181, 0.114, type='double3')
    # cmds.setAttr(f'{light_shape}.color', 0.6, 0.2, 0.8, type='double3')
    cmds.setAttr(f'{light_shape}.intensity', 7.869)
    cmds.setAttr(f'{light_shape}.exposure', 0.249)
    cmds.setAttr(f'{light_shape}.normalize', 0)  # Disable normalization

    cmds.connectAttr(f'{light_transform}.instObjGroups', 'defaultLightSet.dagSetMembers', nextAvailable=True)

    # Check that 'illuminates by default' is already enabled (it should be by default)
    print(f"{light_transform} with {light_shape} created and configured.")

def get_face_normal_in_world_space(mesh, face_index=0):
    # Create a selection list and get the DAG path
    sel_list = om.MSelectionList()
    sel_list.add(mesh)
    dag_path = sel_list.getDagPath(0)

    # Create an MFnMesh function set for the mesh
    mesh_fn = om.MFnMesh(dag_path)

    # Get the normal for the specified face in world space
    normal_vector = mesh_fn.getPolygonNormal(face_index, om.MSpace.kWorld)
    normal_vector.normalize()  # Ensure the normal is a unit vector

    return [normal_vector.x, normal_vector.y, normal_vector.z]

def create_pt_light(frame):
    # Get the current position of the frame
    pos = cmds.xform(frame, query=True, worldSpace=True, translation=True)

    cmds.select(frame + '.f[0]')  # Select the front face
    normal = get_face_normal_in_world_space(frame)

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

    # max_intensity = 20.0
    # mid_intensity = 10.0
    # min_intensity = 5.0

    # Map the Y position to intensity
    intensity = mid_intensity + (y_position * 1.0)
    intensity = max(min_intensity, min(intensity, max_intensity))

    cmds.setAttr(light_shape + ".intensity", intensity)
    # cmds.setAttr(f'{light_shape}.color', 0.301, 0.181, 0.114, type='double3')
    cmds.setAttr(f'{light_shape}.color', 1, 1, 1, type='double3')


    return light_shape

def create_pt_lights():

    rectangular_frames = cmds.ls('Rectangular_Frame*', long=True)

    pt_lights = []

    for frame in rectangular_frames:
        if 'Rectangular_Frame' in frame and cmds.objectType(frame) == 'transform':
            light_shape = create_pt_light(frame)
            pt_lights.append(light_shape)

    lights_grp = cmds.group(pt_lights, name = "point_lights")
    return lights_grp

def make_object_emissive(object_name, emission_color=(1, 1, 1), intensity=40):
    # Create an Arnold Standard Surface shader
    shader = cmds.shadingNode('aiStandardSurface', asShader=True, name=f"{object_name}_emissiveShader")

    # Assign the shader to the object
    shading_group = cmds.sets(renderable=True, noSurfaceShader=True, empty=True, name=f"{shader}SG")
    cmds.connectAttr(f"{shader}.outColor", f"{shading_group}.surfaceShader", force=True)
    cmds.sets(object_name, edit=True, forceElement=shading_group)

    # Enable emission and set its properties
    cmds.setAttr(f"{shader}.emission", 1)  # Enable emission
    cmds.setAttr(f"{shader}.emissionColor", *emission_color, type="double3")  # Set color
    cmds.setAttr(f"{shader}.emissionStrength", intensity)  # Set intensity

    return shader

def create_emissive_shader(_shader_name, _emission_color=(1, 1, 1), _intensity=40, _obj=None):
    shader = cmds.shadingNode('aiStandardSurface', asShader=True, name=_shader_name)
    shading_group = cmds.sets(renderable=True, noSurfaceShader=True, empty=True, name=f"{shader}SG")
    cmds.connectAttr(f"{shader}.outColor", f"{shading_group}.surfaceShader", force=True)

    if _obj:
        cmds.sets(_obj, edit=True, forceElement=shading_group)

    cmds.setAttr(f"{shader}.emission", _intensity)  # Enable emission
    cmds.setAttr(f"{shader}.emissionColor", *_emission_color, type="double3") # Set emission color
    return shader