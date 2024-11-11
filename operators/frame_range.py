import bpy
from bpy.types import Operator
from ..utils.callbacks import update_viewport_resolution

class CAMERA_OT_toggle_frame_range_sync(Operator):
    bl_idname = "camera.toggle_frame_range_sync"
    bl_label = "Toggle Frame Range Sync"
    bl_description = "Toggle synchronization of viewport timeline with camera's frame range"

    def execute(self, context):
        if context.active_object and context.active_object.type == 'CAMERA':
            cam = context.active_object.data
        elif context.scene.camera:
            cam = context.scene.camera.data
        else:
            self.report({'ERROR'}, "No active camera found")
            return {'CANCELLED'}

        settings = cam.cameraide_settings
        settings.sync_frame_range = not settings.sync_frame_range
        
        if settings.sync_frame_range:
            context.scene.frame_start = settings.frame_start
            context.scene.frame_end = settings.frame_end
        
        update_viewport_resolution(context)
        return {'FINISHED'}

def register():
    bpy.utils.register_class(CAMERA_OT_toggle_frame_range_sync)

def unregister():
    bpy.utils.unregister_class(CAMERA_OT_toggle_frame_range_sync)