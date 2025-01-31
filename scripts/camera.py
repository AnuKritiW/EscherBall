"""
Camera Setup: Handles the creation and configuration of a perspective camera in the Maya scene.

This module is responsible for:
- Creating a perspective camera.
- Positioning and orienting the camera for optimal scene framing.
- Configuring camera attributes such as focal length.

Functions:
- set_perspective_camera(): Creates and configures a perspective camera in the scene.
"""

import maya.cmds as cmds

def set_perspective_camera():
    """
    Creates and configures a perspective camera in the Maya scene.

    This function sets up a perspective camera with predefined settings, including:
    - Default position and orientation.
    - Preconfigured focal length for the lens.

    Returns:
        str: The name of the created camera node.
    """

    # Camera settings: retrieved by manually creating a camera and looking at the attribute values
    camera_name     = "Perspective_Stairs_Cam"
    translate       = (-1.556361341180433, 48.57076527730966, 27.76627236948046)
    rotate          = (320.9999999998558, 359.0000000000192, -359.99999999998454)
    film_aperture   = (1.4173200000000001, 0.94488)
    focal_length    = 35.0
    resolution      = [960, 540]
    aspect_ratio    = 1.7777776718139648

    new_camera = cmds.camera(name = camera_name)[0]

    # Set translation and rotation
    cmds.setAttr(new_camera + ".translate", *translate)
    cmds.setAttr(new_camera + ".rotate",    *rotate)

    # Set the film gate (aperture) and focal length
    cmds.setAttr(new_camera + ".horizontalFilmAperture", film_aperture[0])
    cmds.setAttr(new_camera + ".verticalFilmAperture",   film_aperture[1])
    cmds.setAttr(new_camera + ".focalLength",            focal_length)

    # Set render resolution and aspect ratio
    cmds.setAttr("defaultResolution.width",             resolution[0])
    cmds.setAttr("defaultResolution.height",            resolution[1])
    cmds.setAttr("defaultResolution.deviceAspectRatio", aspect_ratio)

    # Lock translation, rotation, and scale
    for attr in ["translate", "rotate", "scale"]:
        cmds.setAttr(f"{new_camera}.{attr}", lock=True)

    # Look through the new camera
    cmds.lookThru(new_camera)
