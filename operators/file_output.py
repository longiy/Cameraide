import bpy
from bpy.types import Operator

class CAMERA_OT_toggle_custom_settings(Operator):
    bl_idname = "camera.toggle_custom_settings"
    bl_label = "FRIENDSHIP"
    bl_description = "Toggle custom camera settings"

    def execute(self, context):
        if context.active_object and context.active_object.type == 'CAMERA':
            cam = context.active_object.data
        elif context.scene.camera:
            cam = context.scene.camera.data
        else:
            self.report({'ERROR'}, "No active camera found")
            return {'CANCELLED'}

        settings = cam.cameraide_settings
        settings.use_custom_settings = not settings.use_custom_settings
        return {'FINISHED'}

def register():
    bpy.utils.register_class(CAMERA_OT_toggle_custom_settings)

def unregister():
    bpy.utils.unregister_class(CAMERA_OT_toggle_custom_settings)