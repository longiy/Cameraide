# In panels/main_panel.py
import bpy
from bpy.types import Panel

class CAMERAIDE_PT_main_panel(Panel):
    bl_label = "Cameraide Settings"
    bl_idname = "CAMERAIDE_PT_main_panel"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "data"

    @classmethod
    def poll(cls, context):
        return context.camera is not None

    def draw(self, context):
        layout = self.layout
        scene = bpy.context.scene

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
            split = layout.split(factor=0.6)    
            col = split.column(heading="File Output")
            col.prop(settings, "output_folder", text="")
            col.prop(settings, "file_name", text="")

            # Format selection box
            box = layout.box()
            col = box.column(align=True)
            col.label(text="File Format")
            col.separator(factor=0.1)

            # Format selection buttons
            row = col.row(align=True)
            row.prop_enum(settings, "output_format", 'PNG', text="PNG")
            row.prop_enum(settings, "output_format", 'JPEG', text="JPEG")
            row.prop_enum(settings, "output_format", 'OPEN_EXR', text="EXR")

            row = col.row(align=True)
            row.prop_enum(settings, "output_format", 'MP4', text="MP4")
            row.prop_enum(settings, "output_format", 'MKV', text="MKV")
            row.prop_enum(settings, "output_format", 'MOV', text="MOV")
            col.separator(factor=1)
            # Format-specific options
            if settings.output_format == 'PNG':
                row = col.row(align=True)
                row.prop(settings, "png_color_depth", text="")
                row.prop(settings, "png_compression", slider=True)
                col.prop(settings, "overwrite_existing")
            elif settings.output_format == 'JPEG':
                col.prop(settings, "jpeg_quality", slider=True)
                col.prop(settings, "overwrite_existing")
            elif settings.output_format == 'OPEN_EXR':
                row = col.row(align=True)
                row.prop(settings, "exr_color_depth", text="")
                row.prop(settings, "exr_codec", text="")
                col.prop(settings, "overwrite_existing")
                # col.prop(settings, "exr_preview")
                

            layout.separator()

            row = layout.row()
            row.prop(settings, "use_audio", text="Audio (mp3)")        
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
    try:
        bpy.utils.unregister_class(CAMERAIDE_PT_main_panel)
    except:
        pass
    bpy.utils.register_class(CAMERAIDE_PT_main_panel)

def unregister():
    try:
        bpy.utils.unregister_class(CAMERAIDE_PT_main_panel)
    except:
        pass