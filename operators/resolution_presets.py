# In operators/resolution_presets.py

import bpy
from bpy.types import Menu, Operator
from bpy.props import EnumProperty, StringProperty

# Resolution presets matching Blender's native ones
PRESETS = [
    ("4K_DCI", "4K DCI 2160p", "4096 x 2160", 4096, 2160),
    ("4K_UHDTV", "4K UHDTV 2160p", "3840 x 2160", 3840, 2160),
    ("4K_UW", "4K UW 1600p", "3840 x 1600", 3840, 1600),
    ("DVCPRO_HD_720", "DVCPRO HD 720p", "1280 x 720", 1280, 720),
    ("DVCPRO_HD_1080", "DVCPRO HD 1080p", "1920 x 1080", 1920, 1080),
    ("HDTV_720", "HDTV 720p", "1280 x 720", 1280, 720),
    ("HDTV_1080", "HDTV 1080p", "1920 x 1080", 1920, 1080),
    ("HDV_1080", "HDV 1080p", "1440 x 1080", 1440, 1080),
    ("HDV_NTSC", "HDV NTSC 1080p", "1440 x 1080", 1440, 1080),
    ("HDV_PAL", "HDV PAL 1080p", "1440 x 1080", 1440, 1080),
    ("TV_NTSC_4_3", "TV NTSC 4:3", "720 x 486", 720, 486),
    ("TV_NTSC_16_9", "TV NTSC 16:9", "720 x 486", 720, 486),
    ("TV_PAL_4_3", "TV PAL 4:3", "720 x 576", 720, 576),
    ("TV_PAL_16_9", "TV PAL 16:9", "720 x 576", 720, 576),
]

class CAMERA_MT_resolution_presets_menu(Menu):
    bl_label = "Resolution Presets"
    bl_idname = "CAMERA_MT_resolution_presets_menu"

    def draw(self, context):
        layout = self.layout
        layout.operator_context = 'EXEC_DEFAULT'

        for identifier, name, desc, _, _ in PRESETS:
            props = layout.operator(
                "camera.resolution_preset_apply",
                text=name
            )
            props.preset_id = identifier

class CAMERA_OT_resolution_preset_apply(Operator):
    bl_idname = "camera.resolution_preset_apply"
    bl_label = "Apply Resolution Preset"
    bl_description = "Apply preset resolution values"
    bl_options = {'REGISTER', 'UNDO'}

    preset_id: StringProperty(
        name="Preset",
        description="Identifier of the resolution preset",
        default=""
    )

    def execute(self, context):
        # Get the active camera
        if context.active_object and context.active_object.type == 'CAMERA':
            cam = context.active_object.data
        elif context.scene.camera:
            cam = context.scene.camera.data
        else:
            self.report({'ERROR'}, "No active camera found")
            return {'CANCELLED'}

        # Find the matching preset
        preset = next((p for p in PRESETS if p[0] == self.preset_id), None)
        if not preset:
            self.report({'ERROR'}, f"Preset {self.preset_id} not found")
            return {'CANCELLED'}

        # Apply the preset
        settings = cam.cameraide_settings
        settings.resolution_x = preset[3]  # Width
        settings.resolution_y = preset[4]  # Height

        # Update the viewport if needed
        from ..utils.callbacks import update_viewport_resolution
        update_viewport_resolution(context)

        return {'FINISHED'}

def register():
    bpy.utils.register_class(CAMERA_MT_resolution_presets_menu)
    bpy.utils.register_class(CAMERA_OT_resolution_preset_apply)

def unregister():
    bpy.utils.unregister_class(CAMERA_OT_resolution_preset_apply)
    bpy.utils.unregister_class(CAMERA_MT_resolution_presets_menu)