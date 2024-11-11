import bpy
from bpy.types import Panel

class Cameraide_settings(Panel):
    bl_label = "Cameraide Settings"
    bl_idname = "Cameraide_settings"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "data"

    @classmethod
    def poll(cls, context):
        return context.camera is not None

    def draw(self, context):
        layout = self.layout
        scene = bpy.context.scene

        # Determine which camera to use
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
            row.operator("camera.toggle_custom_settings", text=f"FRIEND: {camera_name}", icon='FUND', depress=True)
        else:
            row.operator("camera.toggle_custom_settings", text=f"BEFRIEND: {camera_name}", icon='DECORATE')

        if settings.use_custom_settings:
            # Resolution
            split = layout.split(factor=0.5)    
            col = split.column(heading="Resolution")
            col.prop(settings, "resolution_percentage", slider=True)
            row = col.row()
            row.prop(settings, "resolution_x")
            row.prop(settings, "resolution_y")
            row = col.row()
            row.operator("camera.swap_resolution", text="Swap Resolution", icon='ARROW_LEFTRIGHT')

            # Frame Range
            col = split.column(heading="Frame Range")
            col.prop(settings, "frame_step")
            row = col.row()
            row.prop(settings, "frame_start")
            row.prop(settings, "frame_end")
            row = col.row()
            row.operator("camera.toggle_frame_range_sync", 
                        text="Sync " + ("ON" if settings.sync_frame_range else "OFF"), 
                        icon='PREVIEW_RANGE',
                        depress=settings.sync_frame_range)

            # File Output
            split = layout.split(factor=0.7)    
            col = split.column(heading="File Output")
            col.prop(settings, "output_folder", text="")
            col.prop(settings, "file_name", text="")

            col = split.column()
            row = col.row()
            row.prop(settings, "file_format", text="", icon="IMAGE_DATA")

            # Format-specific options
            if settings.file_format == 'PNG':
                col.prop(settings, "png_color_mode", text="")
                row = col.row()   
                row.prop(settings, "png_color_depth", text="")
                row.prop(settings, "png_compression", slider=True)
            elif settings.file_format == 'JPEG':
                col.prop(settings, "jpeg_color_mode", text="")
                col.prop(settings, "jpeg_quality", slider=True)
            elif settings.file_format == 'OPEN_EXR':
                row = col.row() 
                row.prop(settings, "exr_color_mode", text="")
                row.prop(settings, "exr_color_depth", text="")
                row = col.row() 
                row.prop(settings, "exr_codec", text="")
                row.prop(settings, "exr_preview")

            layout.separator()

            row = layout.row()       
            row.prop(settings, "film_transparent")
            row.prop(settings, "overwrite_existing")
            row.prop(settings, "burn_metadata")
            row.prop(settings, "ignore_markers")
            row.prop(settings, "include_camera_name")

            layout.separator()
            layout.separator()
            
            row = layout.row(align=True)
            row.operator("camera.render_selected_viewport", text="Render Viewport", icon="RENDER_ANIMATION")
            row.operator("camera.render_selected_normal", text="Render Normal", icon="RENDER_ANIMATION")

def register():
    bpy.utils.register_class(Cameraide_settings)

def unregister():
    bpy.utils.unregister_class(Cameraide_settings)