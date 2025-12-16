"""Sidebar panel for Cameraide addon"""
import bpy
from bpy.types import Panel


class CAMERAIDE_PT_sidebar_panel(Panel):
    """Main sidebar panel for Cameraide"""
    bl_label = "Cameraide 1.0.7"
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

        # Get active camera
        if context.active_object and context.active_object.type == 'CAMERA':
            cam_obj = context.active_object
            cam = cam_obj.data
            camera_name = cam_obj.name
        elif context.scene.camera:
            cam_obj = context.scene.camera
            cam = cam_obj.data
            camera_name = cam_obj.name
        else:
            layout.label(text="No active camera in the scene")
            return

        settings = cam.cameraide_settings

        # Befriend button
        self._draw_befriend_button(layout, settings, camera_name)
        
        layout.separator()

        # Camera list
        self._draw_camera_list(layout, context)
        
        layout.separator()

        # Settings sections
        if settings.use_custom_settings:
            self._draw_resolution_settings(layout, settings, context)
            self._draw_frame_range_settings(layout, settings, cam_obj, context)
            self._draw_file_output_settings(layout, settings)
            self._draw_format_settings(layout, settings)
            self._draw_extra_settings(layout, settings)
            
            layout.separator()
            
            # Render buttons
            self._draw_render_buttons(layout)

    def _draw_befriend_button(self, layout, settings, camera_name):
        """Draw the befriend/unfriend button"""
        row = layout.row()
        row.scale_y = 2.0
        if settings.use_custom_settings:
            row.operator("camera.toggle_custom_settings", text=f"{camera_name}", 
                        icon='FUND', depress=True)
        else:
            row.operator("camera.toggle_custom_settings", text=f"{camera_name}", 
                        icon='DECORATE')

    def _draw_camera_list(self, layout, context):
        """Draw the collapsible camera lists"""
        all_cameras = [obj for obj in context.scene.objects if obj.type == 'CAMERA']
        
        if not all_cameras:
            return
            
        cameraide_cameras = [c for c in all_cameras if c.data.cameraide_settings.use_custom_settings]
        other_cameras = [c for c in all_cameras if not c.data.cameraide_settings.use_custom_settings]
        
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
                for cam_item in cameraide_cameras:
                    row = box.row(align=True)
                    is_active = context.view_layer.objects.active == cam_item
                    op = row.operator(
                        "cameraide.select_camera",
                        text=cam_item.name,
                        icon='RADIOBUT_ON' if is_active else 'RADIOBUT_OFF',
                        depress=is_active
                    )
                    op.camera_name = cam_item.name
                    
                    op = row.operator("cameraide.remove_camera", text="", icon='X')
                    op.camera_name = cam_item.name
        
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
                for cam_item in other_cameras:
                    row = box.row(align=True)
                    is_active = context.view_layer.objects.active == cam_item
                    op = row.operator(
                        "cameraide.select_camera",
                        text=cam_item.name,
                        icon='RADIOBUT_ON' if is_active else 'RADIOBUT_OFF',
                        depress=is_active
                    )
                    op.camera_name = cam_item.name
                    
                    op = row.operator("cameraide.add_camera", text="", icon='ADD')
                    op.camera_name = cam_item.name

    def _draw_resolution_settings(self, layout, settings, context):
        """Draw resolution settings section"""
        box = layout.box()
        row = box.row(align=True)
        row.prop(settings, "show_resolution_settings", 
            text="Resolution", 
            icon='TRIA_DOWN' if settings.show_resolution_settings else 'TRIA_RIGHT',
            emboss=False
        )
        
        if settings.show_resolution_settings:
            col = box.column(align=True)
            
            row = col.row(align=True)
            split = row.split(factor=0.43, align=True)
            split.prop(settings, "resolution_x")
            
            subsplit = split.split(factor=0.16, align=True)
            subsplit.operator("camera.swap_resolution", text="", icon='ARROW_LEFTRIGHT')
            subsplit.prop(settings, "resolution_y")
            
            col.prop(settings, "resolution_percentage", slider=True)
            row = col.row(align=True)
            row.menu("CAMERA_MT_resolution_presets_menu", text="Presets")

    def _draw_frame_range_settings(self, layout, settings, cam_obj, context):
        """Draw frame range settings section"""
        box = layout.box()
        row = box.row(align=True)
        row.prop(settings, "show_frame_range", 
            text="Frame Range", 
            icon='TRIA_DOWN' if settings.show_frame_range else 'TRIA_RIGHT',
            emboss=False
        )
        
        if not settings.show_frame_range:
            return
            
        col = box.column(align=True)
        
        if not hasattr(settings, 'frame_range_mode'):
            settings.frame_range_mode = 'PER_CAMERA'
        
        from ..utils.marker_detection import get_marker_count, get_marker_frame_ranges
        
        has_markers = get_marker_count(cam_obj) > 0
        current_mode = settings.frame_range_mode
        
        col.prop(settings, "frame_range_mode", text="")
        
        # Mismatch warnings
        if current_mode == 'PER_CAMERA' and has_markers:
            self._draw_timeline_mode_warning(col, cam_obj)
        elif current_mode == 'TIMELINE_MARKERS' and not has_markers:
            self._draw_percamera_mode_warning(col, cam_obj)
        
        # Mode-specific UI
        if current_mode == 'TIMELINE_MARKERS':
            self._draw_timeline_mode_ui(col, settings, cam_obj)
        else:
            self._draw_percamera_mode_ui(col, settings)

    def _draw_timeline_mode_warning(self, col, cam_obj):
        """Draw warning when in per-camera mode but markers exist"""
        from ..utils.marker_detection import get_marker_count, get_marker_frame_ranges
        
        warn_box = col.box()
        warn_col = warn_box.column(align=True)
        warn_col.alert = True
        warn_col.scale_y = 0.9
        
        row = warn_col.row(align=True)
        row.label(text="Timeline markers detected", icon='INFO')
        
        marker_count = get_marker_count(cam_obj)
        ranges = get_marker_frame_ranges(cam_obj)
        if ranges:
            range_text = f"{len(ranges)} range{'s' if len(ranges) != 1 else ''}"
            warn_col.label(text=f"  {range_text} available")
        
        op = warn_col.operator("cameraide.switch_to_timeline_mode", 
                              text="Switch to Timeline Mode", icon='FORWARD')
        op.camera_name = cam_obj.name
        
        col.separator(factor=0.3)

    def _draw_percamera_mode_warning(self, col, cam_obj):
        """Draw warning when in timeline mode but no markers"""
        warn_box = col.box()
        warn_col = warn_box.column(align=True)
        warn_col.alert = True
        warn_col.scale_y = 0.9
        
        warn_col.label(text="No timeline markers found", icon='ERROR')
        warn_col.label(text="  Add markers or switch mode")
        
        op = warn_col.operator("cameraide.switch_to_percamera_mode", 
                              text="Switch to Per-Camera Mode", icon='FORWARD')
        op.camera_name = cam_obj.name
        
        col.separator(factor=0.3)

    def _draw_timeline_mode_ui(self, col, settings, cam_obj):
        """Draw UI for timeline markers mode"""
        from ..utils.marker_detection import get_marker_count, get_marker_frame_ranges
        
        marker_count = get_marker_count(cam_obj)
        if marker_count > 0:
            info_box = col.box()
            info_col = info_box.column(align=True)
            info_col.scale_y = 0.8
            info_col.label(text=f"Using {marker_count} timeline marker{'s' if marker_count != 1 else ''}", 
                          icon='BOOKMARKS')
            
            ranges = get_marker_frame_ranges(cam_obj)
            if ranges:
                for i, (start, end) in enumerate(ranges, 1):
                    info_col.label(text=f"  Range {i}: {start} - {end}")
            
            col.separator(factor=0.5)
            row = col.row(align=True)
            row.enabled = False
            row.prop(settings, "frame_start")
            row.prop(settings, "frame_end")
            row = col.row(align=True)
            row.enabled = False
            row.prop(settings, "frame_step")

    def _draw_percamera_mode_ui(self, col, settings):
        """Draw UI for per-camera mode"""
        row = col.row(align=True)
        row.prop(settings, "frame_start")
        row.prop(settings, "frame_end")
        col.prop(settings, "frame_step")
        col.operator("camera.toggle_frame_range_sync", 
            text="Sync " + ("ON" if settings.sync_frame_range else "OFF"), 
            icon='PREVIEW_RANGE',
            depress=settings.sync_frame_range)

    def _draw_file_output_settings(self, layout, settings):
        """Draw file output settings section"""
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

    def _draw_format_settings(self, layout, settings):
        """Draw format settings section"""
        box = layout.box()
        row = box.row(align=True)
        row.prop(settings, "show_format_settings", 
            text="File Format", 
            icon='TRIA_DOWN' if settings.show_format_settings else 'TRIA_RIGHT',
            emboss=False
        )
        
        if not settings.show_format_settings:
            return
            
        col = box.column(align=True)
        
        # Image formats
        row = col.row(align=True)
        row.prop_enum(settings, "output_format", 'PNG', text="PNG")
        row.prop_enum(settings, "output_format", 'JPEG', text="JPEG")
        row.prop_enum(settings, "output_format", 'OPEN_EXR', text="EXR")

        # Video formats
        row = col.row(align=True)
        row.prop_enum(settings, "output_format", 'H264_MP4', text="MP4")
        row.prop_enum(settings, "output_format", 'H264_MKV', text="MKV")
        
        row = col.row(align=True)
        row.prop_enum(settings, "output_format", 'PRORES_MOV', text="MOV")
        
        col.separator(factor=0.5)

        # Format-specific options
        if settings.output_format == 'PNG':
            self._draw_png_settings(col, settings)
        elif settings.output_format == 'JPEG':
            self._draw_jpeg_settings(col, settings)
        elif settings.output_format == 'OPEN_EXR':
            self._draw_exr_settings(col, settings)
        elif settings.output_format in {'H264_MP4', 'H264_MKV'}:
            self._draw_h264_settings(col, settings)
        elif settings.output_format == 'PRORES_MOV':
            self._draw_prores_settings(col, settings)

    def _draw_png_settings(self, col, settings):
        """Draw PNG format settings"""
        row = col.row(align=True)
        row.prop(settings, "png_color_depth", text="")
        row.prop(settings, "png_compression", slider=True)

    def _draw_jpeg_settings(self, col, settings):
        """Draw JPEG format settings"""
        col.prop(settings, "jpeg_quality", slider=True)

    def _draw_exr_settings(self, col, settings):
        """Draw EXR format settings"""
        row = col.row(align=True)
        row.prop(settings, "exr_color_depth", text="")
        row.prop(settings, "exr_codec", text="")

    def _draw_h264_settings(self, col, settings):
        """Draw H264 video format settings"""
        col.prop(settings, "video_quality", text="Quality")
        col.prop(settings, "video_bitrate")
        col.prop(settings, "video_gopsize")
        
        col.separator(factor=0.5)
        col.prop(settings, "use_audio")
        if settings.use_audio:
            row = col.row(align=True)
            row.prop(settings, "audio_codec", text="")
            row.prop(settings, "audio_bitrate")

    def _draw_prores_settings(self, col, settings):
        """Draw ProRes video format settings"""
        info_box = col.box()
        info_col = info_box.column(align=True)
        info_col.scale_y = 0.8
        info_col.label(text="ProRes 4444 Settings", icon='INFO')
        info_col.label(text="  • Perceptually lossless")
        info_col.label(text="  • Alpha channel support")
        info_col.label(text="  • Professional editing")
        
        col.separator(factor=0.5)
        col.prop(settings, "use_audio")
        if settings.use_audio:
            row = col.row(align=True)
            row.prop(settings, "audio_codec", text="")
            row.prop(settings, "audio_bitrate")

    def _draw_extra_settings(self, layout, settings):
        """Draw extra settings section"""
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
            if settings.output_format in {'PNG', 'OPEN_EXR', 'PRORES_MOV'}:
                col.prop(settings, "film_transparent")
            col.prop(settings, "include_camera_name")
            col.prop(settings, "burn_metadata")

    def _draw_render_buttons(self, layout):
        """Draw render buttons section"""
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
    
    del bpy.types.Scene.cameraide_show_cameraide_list
    del bpy.types.Scene.cameraide_show_other_list
