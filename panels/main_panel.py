# In panels/main_panel.py
import bpy
from bpy.types import Panel

class CAMERAIDE_PT_main_panel(Panel):
    bl_label = "Cameraide 1.0.4"
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
        # Split layout for Resolution and Frame Range
            row = layout.row(align=True)
            split = row.split(factor=0.5)
            
            # Left side - Resolution
            col = split.column()  # Create column in left split
            box = col.box()  # Create box in left column
            col = box.column(align=True)
            col.label(text="Resolution")
            col.separator(factor=0.5)
            
            # Resolution controls with centered swap button
            row = col.row(align=True)
            res_split = row.split(factor=0.43, align=True)
            res_split.prop(settings, "resolution_x")
            
            subsplit = res_split.split(factor=0.16, align=True)
            subsplit.operator("camera.swap_resolution", text="", icon='ARROW_LEFTRIGHT')
            subsplit.prop(settings, "resolution_y")
            
            # Resolution scale slider
            col.prop(settings, "resolution_percentage", slider=True)
            
            # Resolution presets menu
            row = col.row(align=True)
            row.menu("CAMERA_MT_resolution_presets_menu", text="Presets")
            
            # Right side - Frame Range
            col = split.column()  # Create column in right split
            box = col.box()  # Create box in right column
            col = box.column(align=True)
            col.label(text="Frame Range")
            col.separator(factor=0.5)

            col.prop(settings, "frame_step")
            row = col.row(align=True)
            row.prop(settings, "frame_start")
            row.prop(settings, "frame_end")
            col.operator("camera.toggle_frame_range_sync", 
                        text="Sync " + ("ON" if settings.sync_frame_range else "OFF"), 
                        icon='PREVIEW_RANGE',
                        depress=settings.sync_frame_range)

            # File Output
            box = layout.box()
            col = box.column(align=True)
            col.label(text="File Output")
            col.separator(factor=1)

            # Output path with folder structure
            col.prop(settings, "output_path", text="")  # Main output path
            col.prop(settings, "output_subfolder", text="")  # Subfolder
            col.prop(settings, "output_filename", text="")   # Filename


            # Split layout for Format and Extra Settings
            split = layout.split(factor=0.7)

            # Left column - File Format
            col = split.column()
            box = col.box()
            col = box.column(align=True)
            col.label(text="File Format")
            col.separator(factor=0.5)

            # Format selection buttons
            row = col.row(align=True)
            row.scale_y = 1.9
            row.prop_enum(settings, "output_format", 'PNG', text="PNG")
            row.prop_enum(settings, "output_format", 'JPEG', text="JPEG")
            row.prop_enum(settings, "output_format", 'OPEN_EXR', text="EXR")

            row = col.row(align=True)
            row.scale_y = 1.9
            row.prop_enum(settings, "output_format", 'MP4', text="MP4")
            row.prop_enum(settings, "output_format", 'MKV', text="MKV")
            row.prop_enum(settings, "output_format", 'MOV', text="MOV")
            col.separator(factor=0.5)

            # Format-specific options
            if settings.output_format == 'PNG':
                row = col.row(align=True)
                row.prop(settings, "png_color_depth", text="")
                row.prop(settings, "png_compression", slider=True)

            elif settings.output_format == 'JPEG':
                row = col.row(align=True)
                row.prop(settings, "jpeg_quality", slider=True)
                row = col.row(align=True)
                
            elif settings.output_format == 'OPEN_EXR':
                row = col.row(align=True)
                row.prop(settings, "exr_color_depth", text="")
                row.prop(settings, "exr_codec", text="")
                row.prop(settings, "exr_preview")

            if settings.output_format in {'MP4', 'MKV', 'MOV'}:
                row = col.row(align=True)
                col.prop(settings, "use_audio", text="Audio (mp3)")

            # Right column - File Output Extra
            col = split.column()
            box = col.box()
            col = box.column(align=True)
            col.label(text="File Output Extra")
            col.separator(factor=0.5)
            col.prop(settings, "overwrite_existing")
            col.prop(settings, "film_transparent")
            col.prop(settings, "ignore_markers")
            col.prop(settings, "include_camera_name")
            col.prop(settings, "burn_metadata")

            # Render Buttons at the bottom
            row = layout.row(align=True)
            split = row.split(factor=0.85, align=True)
            split.scale_y = 1.5
            split.operator("camera.render_selected_viewport", text="Render Viewport", icon="RESTRICT_VIEW_OFF")
            split.alert = True
            split.operator("camera.render_all_viewport", text="All")
            
            row = layout.row(align=True)
            split = row.split(factor=0.85, align=True)
            split.scale_y = 1.5
            split.operator("camera.render_selected_normal", text="Render Normal", icon="RESTRICT_RENDER_OFF")
            split.alert = True
            split.operator("camera.render_all_normal", text="All")

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