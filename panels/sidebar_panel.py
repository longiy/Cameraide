# In panels/sidebar_panel.py
import bpy
from bpy.types import Panel

class CAMERAIDE_PT_sidebar_panel(Panel):
    bl_label = "Cameraide 1.0.6"
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

        # === BIG CAMERAIDE TOGGLE BUTTON ===
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
        
        layout.separator()

        # === CAMERA LIST ===
        all_cameras = [obj for obj in context.scene.objects if obj.type == 'CAMERA']
        
        if all_cameras:
            cameraide_cameras = [c for c in all_cameras if c.data.cameraide_settings.use_custom_settings]
            other_cameras = [c for c in all_cameras if not c.data.cameraide_settings.use_custom_settings]
            
            # Get or create scene property for collapsible state
            scene = context.scene
            if not hasattr(scene, 'cameraide_show_cameraide_list'):
                scene.cameraide_show_cameraide_list = True
            if not hasattr(scene, 'cameraide_show_other_list'):
                scene.cameraide_show_other_list = False
            
            # Cameraide cameras section
            if cameraide_cameras:
                box = layout.box()
                row = box.row(align=True)
                row.prop(scene, "cameraide_show_cameraide_list",
                    text="Cameraide Cameras",
                    icon='TRIA_DOWN' if scene.cameraide_show_cameraide_list else 'TRIA_RIGHT',
                    emboss=False
                )
                row.label(text="", icon='FUND')
                
                if scene.cameraide_show_cameraide_list:
                    for cam_obj in cameraide_cameras:
                        row = box.row(align=True)
                        is_active = context.view_layer.objects.active == cam_obj
                        op = row.operator(
                            "cameraide.select_camera",
                            text=cam_obj.name,
                            icon='RADIOBUT_ON' if is_active else 'RADIOBUT_OFF',
                            depress=is_active
                        )
                        op.camera_name = cam_obj.name
                        
                        op = row.operator("cameraide.remove_camera", text="", icon='X')
                        op.camera_name = cam_obj.name
            
            # Other cameras section
            if other_cameras:
                box = layout.box()
                row = box.row(align=True)
                row.prop(scene, "cameraide_show_other_list",
                    text="Other Cameras",
                    icon='TRIA_DOWN' if scene.cameraide_show_other_list else 'TRIA_RIGHT',
                    emboss=False
                )
                row.label(text="", icon='CAMERA_DATA')
                
                if scene.cameraide_show_other_list:
                    for cam_obj in other_cameras:
                        row = box.row(align=True)
                        is_active = context.view_layer.objects.active == cam_obj
                        op = row.operator(
                            "cameraide.select_camera",
                            text=cam_obj.name,
                            icon='RADIOBUT_ON' if is_active else 'RADIOBUT_OFF',
                            depress=is_active
                        )
                        op.camera_name = cam_obj.name
                        
                        op = row.operator("cameraide.add_camera", text="", icon='ADD')
                        op.camera_name = cam_obj.name
            
            layout.separator()

        # === REST OF SETTINGS (only show if camera has custom settings) ===
        if settings.use_custom_settings:
            # Resolution
            box = layout.box()
            row = box.row(align=True)
            row.prop(settings, "show_resolution_settings", 
                text="Resolution", 
                icon='TRIA_DOWN' if settings.show_resolution_settings else 'TRIA_RIGHT',
                emboss=False
            )
            
            if settings.show_resolution_settings:
                col = box.column(align=True)
                
                # Resolution controls with centered swap button
                row = col.row(align=True)
                split = row.split(factor=0.43, align=True)
                split.prop(settings, "resolution_x")
                
                subsplit = split.split(factor=0.16, align=True)
                subsplit.operator("camera.swap_resolution", text="", icon='ARROW_LEFTRIGHT')
                subsplit.prop(settings, "resolution_y")
                
                col.prop(settings, "resolution_percentage", slider=True)
                row = col.row(align=True)
                row.menu("CAMERA_MT_resolution_presets_menu", text="Presets")

            # Frame Range
            box = layout.box()
            row = box.row(align=True)
            row.prop(settings, "show_frame_range", 
                text="Frame Range", 
                icon='TRIA_DOWN' if settings.show_frame_range else 'TRIA_RIGHT',
                emboss=False
            )
            
            if settings.show_frame_range:
                col = box.column(align=True)
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
            row = box.row(align=True)
            row.prop(settings, "show_file_output", 
                text="File Output", 
                icon='TRIA_DOWN' if settings.show_file_output else 'TRIA_RIGHT',
                emboss=False
            )
            
            if settings.show_file_output:
                col = box.column(align=True)
                col.prop(settings, "output_path", text="")
                col.prop(settings, "output_subfolder", text="")
                col.prop(settings, "output_filename", text="")

            # Format Settings
            box = layout.box()
            row = box.row(align=True)
            row.prop(settings, "show_format_settings", 
                text="File Format", 
                icon='TRIA_DOWN' if settings.show_format_settings else 'TRIA_RIGHT',
                emboss=False
            )
            
            if settings.show_format_settings:
                col = box.column(align=True)
                
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

                if settings.output_format in {'MP4', 'MKV', 'MOV'}:
                    row = col.row(align=True)
                    col.prop(settings, "use_audio", text="Audio (mp3)")

            # Extra Settings
            box = layout.box()
            row = box.row(align=True)
            row.prop(settings, "show_extra_settings", 
                text="Extra Settings", 
                icon='TRIA_DOWN' if settings.show_extra_settings else 'TRIA_RIGHT',
                emboss=False
            )
            
            if settings.show_extra_settings:
                col = box.column(align=True)
                if settings.output_format in {'PNG', 'JPEG', 'OPEN_EXR'}:
                    col.prop(settings, "overwrite_existing")
                if settings.output_format in {'PNG', 'OPEN_EXR'}:
                    col.prop(settings, "film_transparent")
                col.prop(settings, "ignore_markers")
                col.prop(settings, "include_camera_name")
                col.prop(settings, "burn_metadata")

            # Render Buttons (always visible when custom settings are enabled)
            layout.separator()
            
            # Viewport Render Section
            box = layout.box()
            box.label(text="Viewport Render", icon='RESTRICT_VIEW_OFF')
            
            row = box.row(align=True)
            row.scale_y = 1.3
            row.operator("camera.render_snapshot_viewport", text="Snapshot", icon='RENDER_STILL')
            row.operator("camera.render_selected_viewport", text="Playblast", icon='RENDER_ANIMATION')
            row.operator("camera.render_all_viewport", text="All Cameras", icon='CAMERA_DATA')
            
            # Normal Render Section
            box = layout.box()
            box.label(text="Normal Render", icon='RESTRICT_RENDER_OFF')
            
            row = box.row(align=True)
            row.scale_y = 1.3
            row.operator("camera.render_snapshot_normal", text="Snapshot", icon='RENDER_STILL')
            row.operator("camera.render_selected_normal", text="Playblast", icon='RENDER_ANIMATION')
            row.operator("camera.render_all_normal", text="All Cameras", icon='CAMERA_DATA')
    
def register():
    # Register scene properties for collapsible lists
    bpy.types.Scene.cameraide_show_cameraide_list = bpy.props.BoolProperty(default=True)
    bpy.types.Scene.cameraide_show_other_list = bpy.props.BoolProperty(default=False)
    
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
    
    # Unregister scene properties
    del bpy.types.Scene.cameraide_show_cameraide_list
    del bpy.types.Scene.cameraide_show_other_list