# In operators/frame_range.py
import bpy
from bpy.types import Operator
from ..utils.callbacks import update_viewport_resolution, on_sync_toggle

class CAMERA_OT_toggle_frame_range_sync(Operator):
    bl_idname = "camera.toggle_frame_range_sync"
    bl_label = "Toggle Frame Range Sync"
    bl_description = "Toggle synchronization of viewport timeline with camera's frame range"

    def execute(self, context):
        if context.active_object and context.active_object.type == 'CAMERA':
            cam = context.active_object
        elif context.scene.camera:
            cam = context.scene.camera
        else:
            self.report({'ERROR'}, "No active camera found")
            return {'CANCELLED'}

        settings = cam.data.cameraide_settings
        settings.sync_frame_range = not settings.sync_frame_range
        
        on_sync_toggle(cam)
        update_viewport_resolution(context)
        
        return {'FINISHED'}

def register():
    try:
        bpy.utils.unregister_class(CAMERA_OT_toggle_frame_range_sync)
    except:
        pass
    bpy.utils.register_class(CAMERA_OT_toggle_frame_range_sync)

def unregister():
    try:
        bpy.utils.unregister_class(CAMERA_OT_toggle_frame_range_sync)
    except:
        pass