bl_info = {
    "name": "CameraideV2", 
    "author": "longiy",
    "version": (0, 1, 2),
    "blender": (4, 2, 0),
    "location": "Properties > Camera > CameraideV2, 3D View > Sidebar > CameraideV2",
    "description": "Adds custom settings for each camera with improved UI and features",
    "category": "Camera",
}

import bpy

# Import all modules
from . import properties
from .panels import main_panel, sidebar_panel
from .operators import resolution, frame_range, file_output, render
from .utils import callbacks

def register():
    properties.register()
    main_panel.register()
    sidebar_panel.register()
    resolution.register()
    frame_range.register()
    file_output.register()
    render.register()
    callbacks.register()

def unregister():
    callbacks.unregister()
    render.unregister()
    file_output.unregister()
    frame_range.unregister()
    resolution.unregister()
    sidebar_panel.unregister()
    main_panel.unregister()
    properties.unregister()

if __name__ == "__main__":
    register()