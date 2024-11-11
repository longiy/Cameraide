import bpy
from bpy.types import Panel

class Cameraide_settings_3dview(Panel):
    bl_label = "Cameraide Settings"
    bl_idname = "Cameraide_settings_3dview"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Camera"
    bl_options = {'DEFAULT_CLOSED'}

    @classmethod
    def poll(cls, context):
        return True

    def draw(self, context):
        layout = self.layout

        if context.active_object and context.active_object.type == 'CAMERA':
            cam = context.active_object.data
            camera_name = context.active_object.name
        elif context.scene.camera:
            cam = context.scene.camera.data
            camera_name = context.scene.camera.name
        else:
            layout.label(text="No active camera in the scene")
            return

        settings = cam.cameraide_settings

        # Friend/Befriend button
        row = layout.row()
        row.scale_y = 2.0
        if settings.use_custom_settings:
            row.operator("camera.toggle_custom_settings", text=f"FRIEND: {camera_name}", icon='DECORATE', depress=True)
        else:
            row.operator("camera.toggle_custom_settings", text=f"BEFRIEND: {camera_name}", icon='DECORATE')

        if settings.use_custom_settings:
            # Resolution
            box = layout.box()
            box.label(text="Resolution", icon="KEYTYPE_EXTREME_VEC")
            row = layout.row(align=True)
            row.prop(settings, "resolution_x")
            row.prop(settings, "resolution_y")
            layout.prop(settings, "resolution_percentage", slider=True)
            layout.operator("camera.swap_resolution", text="Swap Resolution", icon='ARROW_LEFTRIGHT')

            # Frame Range
            box = layout.box()
            box.label(text="Frame Range", icon="KEYTYPE_EXTREME_VEC")
            row = layout.row(align=True)
            row.prop(settings, "frame_start")
            row.prop(settings, "frame_end")
            layout.prop(settings, "frame_step")
            layout.operator("camera.toggle_frame_range_sync", 
                         text="Sync " + ("ON" if settings.sync_frame_range else "OFF"), 
                         icon='PREVIEW_RANGE',
                         depress=settings.sync_frame_range)

            # File Output
            layout.separator()
            box = layout.box()
            box.label(text="File Output", icon="KEYTYPE_EXTREME_VEC")
            layout.prop(settings, "output_folder", text="")
            layout.prop(settings, "file_name", text="")
            row = layout.row(align=True)
            row.prop(settings, "file_format", text="")
            row.prop(settings, "png_color_mode", text="")

            # Format-specific options
            if settings.file_format == 'PNG':
                row = layout.row(align=True)
                row.prop(settings, "png_color_depth", text="")
                row.prop(settings, "png_compression", slider=True)
                layout.prop(settings, "overwrite_existing")
            elif settings.file_format == 'JPEG':
                row = layout.row(align=True)
                row.prop(settings, "jpeg_quality", slider=True)
                layout.prop(settings, "overwrite_existing")
            elif settings.file_format == 'OPEN_EXR':
                row = layout.row(align=True)
                row.prop(settings, "exr_color_depth", text="")
                row.prop(settings, "exr_codec", text="")
                row = layout.row(align=True)
                row.prop(settings, "overwrite_existing")
                row.prop(settings, "exr_preview")

            # Extra Settings
            box = layout.box()
            box.label(text="File Output Extra", icon="KEYTYPE_EXTREME_VEC")
            layout.prop(settings, "film_transparent")
            layout.prop(settings, "ignore_markers")
            layout.prop(settings, "include_camera_name")
            layout.prop(settings, "burn_metadata")

            # Render Buttons
            row = layout.row()
            row.scale_y = 2.0
            row.operator("camera.render_selected_viewport", text="Render Viewport", icon="RENDER_ANIMATION")
            row = layout.row()
            row.operator("camera.render_selected_normal", text="Render Normal", icon="RENDER_ANIMATION")

def register():
    bpy.utils.register_class(Cameraide_settings_3dview)

def unregister():
    bpy.utils.unregister_class(Cameraide_settings_3dview)