import bpy
from bpy.types import Operator
from ..utils.callbacks import update_viewport_resolution

class CAMERA_OT_swap_resolution(Operator):
    bl_idname = "camera.swap_resolution"
    bl_label = "Swap Resolution"
    bl_description = "Swap X and Y resolution values"

    def execute(self, context):
        if context.active_object and context.active_object.type == 'CAMERA':
            cam = context.active_object.data
        elif context.scene.camera:
            cam = context.scene.camera.data
        else:
            self.report({'ERROR'}, "No active camera found")
            return {'CANCELLED'}

        settings = cam.cameraide_settings
        settings.resolution_x, settings.resolution_y = settings.resolution_y, settings.resolution_x
        update_viewport_resolution(context)
        return {'FINISHED'}

def register():
    bpy.utils.register_class(CAMERA_OT_swap_resolution)

def unregister():
    bpy.utils.unregister_class(CAMERA_OT_swap_resolution)