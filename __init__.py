bl_info = {
    "name": "Cameraide", 
    "author": "longiy",
    "version": (1, 0, 7),
    "blender": (4, 2, 0),
    "location": "Properties > Camera > Cameraide, 3D View > Sidebar > Cameraide",
    "description": "Adds custom settings for each camera with improved UI and features",
    "category": "Camera",
}

import bpy

# Import all modules
from . import properties
from . import operators
from . import panels
from . import utils

def register():
    properties.register()
    operators.register()
    panels.register()
    utils.register()

def unregister():
    utils.unregister()
    panels.unregister()
    operators.unregister()
    properties.unregister()

if __name__ == "__main__":
    register()