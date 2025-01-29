# In operators/resolution_presets.py

import bpy
from bpy.types import Menu, Operator
import os

def get_presets():
    """Get all render presets including custom ones"""
    render_presets = []
    preset_paths = bpy.utils.preset_paths("render")
    
    for preset_path in preset_paths:
        if os.path.exists(preset_path):
            for preset_file in sorted(os.listdir(preset_path)):
                if preset_file.endswith(".py"):  # Blender actually stores presets as .py files
                    name = os.path.splitext(preset_file)[0]
                    filepath = os.path.join(preset_path, preset_file)
                    render_presets.append((name, filepath))
    
    return render_presets

class CAMERA_MT_resolution_presets_menu(Menu):
    bl_label = "Resolution Presets"
    bl_idname = "CAMERA_MT_resolution_presets_menu"

    def draw(self, context):
        layout = self.layout
        layout.operator_context = 'EXEC_DEFAULT'

        # Get and display all presets
        for name, filepath in get_presets():
            props = layout.operator(
                "camera.resolution_preset_apply",
                text=name
            )
            props.preset_filepath = filepath

class CAMERA_OT_resolution_preset_apply(Operator):
    bl_idname = "camera.resolution_preset_apply"
    bl_label = "Apply Resolution Preset"
    bl_description = "Apply Blender's resolution preset to the camera"
    bl_options = {'REGISTER', 'UNDO'}

    preset_filepath: bpy.props.StringProperty(
        name="Preset Path",
        description="Path to the preset file",
        default=""
    )

    def execute(self, context):
        if not self.preset_filepath or not os.path.exists(self.preset_filepath):
            self.report({'ERROR'}, "Invalid preset path")
            return {'CANCELLED'}

        # Get the active camera
        if context.active_object and context.active_object.type == 'CAMERA':
            cam = context.active_object.data
        elif context.scene.camera:
            cam = context.scene.camera.data
        else:
            self.report({'ERROR'}, "No active camera found")
            return {'CANCELLED'}

        # Store current render settings
        old_res_x = context.scene.render.resolution_x
        old_res_y = context.scene.render.resolution_y

        try:
            # Execute the preset file
            bpy.ops.script.execute_preset(filepath=self.preset_filepath, menu_idname="RENDER_MT_preset")
            
            # Get the new resolution from render settings
            new_res_x = context.scene.render.resolution_x
            new_res_y = context.scene.render.resolution_y

            # Apply to camera settings
            settings = cam.cameraide_settings
            settings.resolution_x = new_res_x
            settings.resolution_y = new_res_y

            # Restore original render settings
            context.scene.render.resolution_x = old_res_x
            context.scene.render.resolution_y = old_res_y

            # Update viewport if needed
            from ..utils.callbacks import update_viewport_resolution
            update_viewport_resolution(context)

            return {'FINISHED'}

        except Exception as e:
            self.report({'ERROR'}, f"Failed to apply preset: {str(e)}")
            return {'CANCELLED'}

def register():
    bpy.utils.register_class(CAMERA_MT_resolution_presets_menu)
    bpy.utils.register_class(CAMERA_OT_resolution_preset_apply)

def unregister():
    bpy.utils.unregister_class(CAMERA_OT_resolution_preset_apply)
    bpy.utils.unregister_class(CAMERA_MT_resolution_presets_menu)