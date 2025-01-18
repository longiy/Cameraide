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
            layout.separator()
            box = layout.box()
            col = box.column(align=True)
            col.label(text="File Output")
            col.separator(factor=1)

            # Output path with folder structure
            col.prop(settings, "output_path", text="")  # Main output path
            col.prop(settings, "output_subfolder", text="")  # Subfolder
            col.prop(settings, "output_filename", text="")   # Filename
            
            # Format-specific options, all inside the file output box
            box = layout.box()
            col = box.column(align=True)
            col.label(text="File Format")
            col.separator(factor=1)

            # Format selection buttons - now using a single property
            row = col.row(align=True)
            row.prop_enum(settings, "output_format", 'PNG', text="PNG")
            row.prop_enum(settings, "output_format", 'JPEG', text="JPEG")
            row.prop_enum(settings, "output_format", 'OPEN_EXR', text="EXR")

            row = col.row(align=True)
            row.prop_enum(settings, "output_format", 'MP4', text="MP4")
            row.prop_enum(settings, "output_format", 'MKV', text="MKV")
            row.prop_enum(settings, "output_format", 'MOV', text="MOV")
            col.separator(factor=0.5)

            # Format-specific options
            if settings.output_format == 'PNG':
                
                row = col.row(align=True)
                row.prop(settings, "png_color_depth", text="")
                row.prop(settings, "png_compression", slider=True)
                row = col.row(align=True)
                row.prop(settings, "overwrite_existing")
                row.prop(settings, "film_transparent")
                
            elif settings.output_format == 'JPEG':
                row = col.row(align=True)
                row.prop(settings, "overwrite_existing")
                row.prop(settings, "jpeg_quality", slider=True)
                
            elif settings.output_format == 'OPEN_EXR':
                row = col.row(align=True)
                row.prop(settings, "exr_color_depth", text="")
                row.prop(settings, "exr_codec", text="")
                row = col.row(align=True)
                row.prop(settings, "overwrite_existing")
                row.prop(settings, "film_transparent")
                row.prop(settings, "exr_preview")

            if settings.output_format in {'MP4', 'MKV', 'MOV'}:
                row = col.row(align=True)
                col.prop(settings, "use_audio", text="Audio (mp3)")
            


           # Extra Settings
            split = layout.split(factor=0.4)  # Split layout into two columns: 70% and 30%

            # Left column - File Output Extra
            col2 = split.column()
            col2.scale_y = 2.2  # Make buttons taller
            row = col2.row()
            row.operator("camera.render_selected_viewport", text="Render Viewport", icon="RENDER_ANIMATION")
            row = col2.row()
            row.operator("camera.render_selected_normal", text="Render Normal", icon="RENDER_ANIMATION")
            
            # Right column - Render Buttons
            col1 = split.column()
            box = col1.box()
            col = box.column(align=True)
            col.label(text="File Ouput Extra")
            col.prop(settings, "ignore_markers")
            col.prop(settings, "include_camera_name")
            col.prop(settings, "burn_metadata")

            

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