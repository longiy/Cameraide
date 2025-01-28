# In panels/sidebar_panel.py
import bpy
from bpy.types import Panel

class CAMERAIDE_PT_sidebar_panel(Panel):
    bl_label = "Cameraide 1.0.2"
    bl_idname = "CAMERAIDE_PT_sidebar_panel"
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
            row.operator("camera.toggle_custom_settings", text=f"{camera_name}", icon='FUND', depress=True)
        else:
            row.operator("camera.toggle_custom_settings", text=f"{camera_name}", icon='DECORATE')

        if settings.use_custom_settings:
            # Resolution
            box = layout.box()
            col = box.column(align=True)  # Use column for compact spacing
            col.label(text="Resolution")
            col.separator(factor=1)
            row = col.row(align=True)
            row.prop(settings, "resolution_x")
            row.prop(settings, "resolution_y")
            col.prop(settings, "resolution_percentage", slider=True)
            col.operator("camera.swap_resolution", text="Swap Resolution", icon='ARROW_LEFTRIGHT')

            # Frame Range
            box = layout.box()
            col = box.column(align=True)  # Use column for compact spacing
            col.label(text="Frame Range")
            col.separator(factor=1)
            row = col.row(align=True)
            row.prop(settings, "frame_start")
            row.prop(settings, "frame_end")
            col.prop(settings, "frame_step")
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
                
            elif settings.output_format == 'JPEG':
                col.prop(settings, "jpeg_quality", slider=True)
                
            elif settings.output_format == 'OPEN_EXR':
                row = col.row(align=True)
                row.prop(settings, "exr_color_depth", text="")
                row.prop(settings, "exr_codec", text="")
                # col.prop(settings, "exr_preview")
            if settings.output_format in {'MP4', 'MKV', 'MOV'}:
                row = col.row(align=True)
                col.prop(settings, "use_audio", text="Audio (mp3)")
            
            # Extra Settings
            box = layout.box()
            col = box.column(align=True)  # Use column for compact spacing
            col.label(text="File Output Extra")
            col.separator(factor=1)

            # Audio option only for video formats
            if settings.output_format in {'PNG', 'JPEG', 'OPEN_EXR'}:
                col.prop(settings, "overwrite_existing")

            # Common options for all formats
            if settings.output_format in {'PNG', 'OPEN_EXR'}:
                col.prop(settings, "film_transparent")
            col.prop(settings, "ignore_markers")
            col.prop(settings, "include_camera_name")
            col.prop(settings, "burn_metadata")
            
            # In both panel files:



            row = layout.row(align=True)  # This align=True is what makes resolution gapless
            split = row.split(factor=0.85, align=True)
            split.scale_y = 1.5
            split.operator("camera.render_selected_viewport", text="Render Viewport", icon="RESTRICT_VIEW_OFF")
            split.alert = True
            split.operator("camera.render_all_viewport", text="All")
            
            row = layout.row(align=True)  # This align=True is what makes resolution gapless
            split = row.split(factor=0.85, align=True)
            split.scale_y = 1.5
            split.operator("camera.render_selected_normal", text="Render Normal", icon="RESTRICT_RENDER_OFF")
            split.alert = True
            split.operator("camera.render_all_normal", text="All")
                        
    
def register():
    try:
        bpy.utils.unregister_class(CAMERAIDE_PT_sidebar_panel)
    except:
        pass
    bpy.utils.register_class(CAMERAIDE_PT_sidebar_panel)

def unregister():
    try:
        bpy.utils.unregister_class(CAMERAIDE_PT_sidebar_panel)
    except:
        pass