# In operators/resolution_presets.py

import bpy
from bpy.types import Menu, Operator
from bpy.props import EnumProperty, StringProperty

# Resolution presets from square to widest aspect ratio
PRESETS = [
    ("SQUARE", "Square 1:1", "1080 x 1080", 1080, 1080),
    ("FILM_70MM", "70mm Film 6:5", "4096 x 3412", 4096, 3412),
    ("TRADITIONAL_4_3", "Traditional 4:3", "1600 x 1200", 1600, 1200),
    ("ACADEMY", "Academy Ratio 1.33:1", "2048 x 1536", 2048, 1536),
    ("IMAX", "IMAX 1.43:1", "4096 x 2860", 4096, 2860),
    ("PHOTO_3_2", "Photo 3:2", "2160 x 1440", 2160, 1440),
    ("EUROPEAN", "European Widescreen 1.66:1", "3840 x 2312", 3840, 2312),
    ("COMPUTER", "Computer 16:10", "1920 x 1200", 1920, 1200),
    ("CINEMA_FLAT", "Cinema Flat 1.85:1", "4096 x 2214", 4096, 2214),
    ("HD", "HD 16:9", "1920 x 1080", 1920, 1080),
    ("ULTRAWIDE", "Ultrawide 21:9", "3440 x 1440", 3440, 1440),
    ("SCOPE", "Anamorphic 2.39:1", "4096 x 1716", 4096, 1716),
    ("SUPER_ULTRAWIDE", "Super Ultrawide 32:9", "5120 x 1440", 5120, 1440),
    ("ULTRA_PANAVISION", "Ultra Panavision 2.76:1", "4096 x 1484", 4096, 1484),
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
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}

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