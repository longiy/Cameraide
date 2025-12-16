# In panels/__init__.py
from .sidebar_panel import register as register_sidebar_panel, unregister as unregister_sidebar_panel
from .camera_list import (
    CAMERAIDE_OT_select_camera,
    CAMERAIDE_OT_add_camera,
    CAMERAIDE_OT_remove_camera
)
import bpy

def register():
    # Register camera list operators first
    bpy.utils.register_class(CAMERAIDE_OT_remove_camera)
    bpy.utils.register_class(CAMERAIDE_OT_add_camera)
    bpy.utils.register_class(CAMERAIDE_OT_select_camera)
    
    register_sidebar_panel()

def unregister():
    unregister_sidebar_panel()
    
    # Unregister camera list operators
    bpy.utils.unregister_class(CAMERAIDE_OT_select_camera)
    bpy.utils.unregister_class(CAMERAIDE_OT_add_camera)
    bpy.utils.unregister_class(CAMERAIDE_OT_remove_camera)