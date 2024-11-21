# In operators/file_output.py
import bpy
from bpy.types import Operator
from ..utils.callbacks import on_befriend_toggle

class CAMERA_OT_toggle_custom_settings(Operator):
    bl_idname = "camera.toggle_custom_settings"
    bl_label = "FRIENDSHIP"
    bl_description = "Toggle custom camera settings"

    def execute(self, context):
        if context.active_object and context.active_object.type == 'CAMERA':
            cam = context.active_object
        elif context.scene.camera:
            cam = context.scene.camera
        else:
            self.report({'ERROR'}, "No active camera found")
            return {'CANCELLED'}

        settings = cam.data.cameraide_settings
        settings.use_custom_settings = not settings.use_custom_settings
        
        # Handle frame range sync when befriending/unfriending
        on_befriend_toggle(cam)
        
        return {'FINISHED'}

def register():
    try:
        bpy.utils.unregister_class(CAMERA_OT_toggle_custom_settings)
    except:
        pass
    bpy.utils.register_class(CAMERA_OT_toggle_custom_settings)

def unregister():
    try:
        bpy.utils.unregister_class(CAMERA_OT_toggle_custom_settings)
    except:
        pass