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

# Import order matters - properties first, then utils, then operators/panels
from . import properties
from . import utils
from . import operators
from . import panels

def register():
    # Register in dependency order
    properties.register()
    utils.register()
    operators.register()
    panels.register()

def unregister():
    # Unregister in reverse order
    panels.unregister()
    operators.unregister()
    utils.unregister()
    properties.unregister()

if __name__ == "__main__":
    register()
