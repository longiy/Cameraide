import bpy
import os
from bpy.types import Operator
import time
from ..utils.marker_detection import get_all_marker_ranges

class RenderCleanupManager:
    """Manages render settings and cleanup for Cameraide"""
    
    _original_settings = None
    _current_camera = None
    
    @classmethod
    def store_settings(cls, context):
        """Store original render settings"""
        cls._original_settings = {
            'frame_start': context.scene.frame_start,
            'frame_end': context.scene.frame_end,
            'filepath': context.scene.render.filepath,
            'resolution_x': context.scene.render.resolution_x,
            'resolution_y': context.scene.render.resolution_y,
            'resolution_percentage': context.scene.render.resolution_percentage,
            'film_transparent': context.scene.render.film_transparent,
            'use_stamp': context.scene.render.use_stamp,
            'frame_step': context.scene.frame_step,
            'file_format': context.scene.render.image_settings.file_format,
            'color_mode': context.scene.render.image_settings.color_mode,
            'view_transform': context.scene.view_settings.view_transform,
            'look': context.scene.view_settings.look,
            'exposure': context.scene.view_settings.exposure,
            'gamma': context.scene.view_settings.gamma,
            'use_curve_mapping': context.scene.view_settings.use_curve_mapping
        }
        
        current_format = context.scene.render.image_settings.file_format
        if current_format in {'PNG', 'JPEG', 'OPEN_EXR'}:
            cls._store_image_settings(context)
        elif current_format in {'FFMPEG', 'MPEG4', 'MKV', 'QUICKTIME'}:
            cls._store_video_settings(context)

    @classmethod
    def _store_image_settings(cls, context):
        """Store image format specific settings"""
        image_settings = context.scene.render.image_settings
        format_settings = {}
        
        if hasattr(image_settings, 'color_depth'):
            format_settings['color_depth'] = image_settings.color_depth
        if hasattr(image_settings, 'compression'):
            format_settings['compression'] = image_settings.compression
        if hasattr(image_settings, 'quality'):
            format_settings['quality'] = image_settings.quality
        if hasattr(image_settings, 'exr_codec'):
            format_settings['exr_codec'] = image_settings.exr_codec
        if hasattr(image_settings, 'use_preview'):
            format_settings['use_preview'] = image_settings.use_preview
        
        cls._original_settings.update(format_settings)

    @classmethod
    def _store_video_settings(cls, context):
        """Store video format specific settings"""
        ffmpeg = context.scene.render.ffmpeg
        cls._original_settings.update({
            'ffmpeg_codec': ffmpeg.codec,
            'ffmpeg_video_bitrate': ffmpeg.video_bitrate,
            'ffmpeg_minrate': ffmpeg.minrate,
            'ffmpeg_maxrate': ffmpeg.maxrate,
            'ffmpeg_gopsize': ffmpeg.gopsize,
            'ffmpeg_audio_codec': ffmpeg.audio_codec,
            'ffmpeg_audio_bitrate': ffmpeg.audio_bitrate
        })
        
    @classmethod
    def restore_settings(cls, context):
        """Restore original render settings"""
        if cls._original_settings:
            # Get available formats once
            available_formats = [item.identifier for item in context.scene.render.image_settings.bl_rna.properties['file_format'].enum_items]
            
            for key, value in cls._original_settings.items():
                if value is None:
                    continue
                
                # Skip invalid file formats
                if key == 'file_format' and value not in available_formats:
                    print(f"Skipping restore of unsupported format: {value}")
                    continue
                    
                if key.startswith('ffmpeg_'):
                    clean_key = key.replace('ffmpeg_', '')
                    if hasattr(context.scene.render.ffmpeg, clean_key):
                        setattr(context.scene.render.ffmpeg, clean_key, value)
                elif key in ['view_transform', 'look', 'exposure', 'gamma', 'use_curve_mapping']:
                    setattr(context.scene.view_settings, key, value)
                elif hasattr(context.scene.render, key):
                    setattr(context.scene.render, key, value)
                elif hasattr(context.scene.render.image_settings, key):
                    setattr(context.scene.render.image_settings, key, value)
                elif hasattr(context.scene, key):
                    setattr(context.scene, key, value)
            cls._original_settings = None
    
    @classmethod
    def apply_camera_settings(cls, context, cam_obj, frame_range=None):
        """
        Apply camera settings to render.
        frame_range: Optional (start, end) tuple to override frame range
        """
        from ..utils.callbacks import get_clean_camera_name
        
        settings = cam_obj.data.cameraide_settings
        cls._current_camera = cam_obj
        
        # Calculate resolution
        res_x = settings.resolution_x
        res_y = settings.resolution_y
        percentage = settings.resolution_percentage
        
        if settings.output_format in {'MP4', 'MKV', 'MOV'}:
            scaled_x = int((res_x * percentage) / 100)
            scaled_y = int((res_y * percentage) / 100)
            res_x = scaled_x + (scaled_x % 2)
            res_y = scaled_y + (scaled_y % 2)
            context.scene.render.resolution_percentage = 100
        else:
            context.scene.render.resolution_percentage = percentage
            
        # Apply frame range (use override if provided, otherwise detect from mode)
        if frame_range:
            context.scene.frame_start = frame_range[0]
            context.scene.frame_end = frame_range[1]
        else:
            from ..utils.marker_detection import get_effective_frame_range
            start, end = get_effective_frame_range(cam_obj)
            context.scene.frame_start = start
            context.scene.frame_end = end
        
        context.scene.frame_step = settings.frame_step
        context.scene.render.resolution_x = res_x
        context.scene.render.resolution_y = res_y
        context.scene.render.film_transparent = settings.film_transparent
        context.scene.render.use_stamp = settings.burn_metadata

        # Construct output path
        base_path = bpy.path.abspath(settings.output_path)
        subfolder = settings.output_subfolder
        if settings.include_camera_name:
            clean_name = get_clean_camera_name(cam_obj)
            filename = f"{clean_name}_{settings.output_filename}"
        else:
            filename = settings.output_filename
            
        filepath = os.path.join(base_path, subfolder, filename)
        context.scene.render.filepath = filepath
        
        # Format settings
        if settings.output_format in {'PNG', 'JPEG', 'OPEN_EXR'}:
            context.scene.render.image_settings.file_format = settings.output_format
            cls._apply_format_settings(context, settings)
        else:
            cls._apply_video_settings(context, settings)

    @classmethod
    def _apply_format_settings(cls, context, settings):
        """Apply format-specific settings"""
        image_settings = context.scene.render.image_settings
        
        if settings.output_format == 'PNG':
            image_settings.color_mode = 'RGBA'
            image_settings.color_depth = settings.png_color_depth
            image_settings.compression = settings.png_compression
            
        elif settings.output_format == 'JPEG':
            image_settings.color_mode = 'RGB'
            image_settings.quality = settings.jpeg_quality
            
        elif settings.output_format == 'OPEN_EXR':
            image_settings.color_mode = 'RGBA'
            image_settings.color_depth = settings.exr_color_depth
            image_settings.exr_codec = settings.exr_codec
            if hasattr(image_settings, 'use_preview'):
                image_settings.use_preview = settings.exr_preview

    @classmethod
    def _apply_video_settings(cls, context, settings):
        """Apply video-specific settings"""
        # CRITICAL: image_settings.file_format must be 'FFMPEG' for video
        # This should already be set in apply_camera_settings, but ensure it here
        context.scene.render.image_settings.file_format = 'FFMPEG'
        
        # Now configure the FFMPEG container format
        context.scene.render.ffmpeg.format = {
            'MP4': 'MPEG4',
            'MKV': 'MKV',
            'MOV': 'QUICKTIME'
        }[settings.output_format]
        
        if settings.output_format == 'MOV':
            context.scene.render.ffmpeg.codec = 'QTRLE'
            if hasattr(context.scene.render.ffmpeg, 'constant_rate_factor'):
                context.scene.render.ffmpeg.constant_rate_factor = 'LOSSLESS'
            context.scene.render.ffmpeg.gopsize = 1
        else:
            context.scene.render.ffmpeg.codec = 'H264'
            if hasattr(context.scene.render.ffmpeg, 'constant_rate_factor'):
                context.scene.render.ffmpeg.constant_rate_factor = 'HIGH'
            context.scene.render.ffmpeg.video_bitrate = 6000
            context.scene.render.ffmpeg.minrate = 0
            context.scene.render.ffmpeg.maxrate = 9000
            context.scene.render.ffmpeg.gopsize = 12
        
        if settings.use_audio:
            context.scene.render.ffmpeg.audio_codec = 'MP3'
            context.scene.render.ffmpeg.audio_bitrate = 192
        else:
            context.scene.render.ffmpeg.audio_codec = 'NONE'


def render_complete_handler(scene, depsgraph):
    """Handler for render completion"""
    RenderCleanupManager.restore_settings(bpy.context)
    remove_handlers()

def render_cancel_handler(scene, depsgraph):
    """Handler for render cancellation"""
    RenderCleanupManager.restore_settings(bpy.context)
    remove_handlers()

def remove_handlers():
    """Remove render handlers"""
    if render_complete_handler in bpy.app.handlers.render_complete:
        bpy.app.handlers.render_complete.remove(render_complete_handler)
    if render_cancel_handler in bpy.app.handlers.render_cancel:
        bpy.app.handlers.render_cancel.remove(render_cancel_handler)


# === SNAPSHOT OPERATORS ===
class CAMERA_OT_render_snapshot_viewport(Operator):
    bl_idname = "camera.render_snapshot_viewport"
    bl_label = "Render Snapshot (Viewport)"
    bl_description = "Render current frame using viewport renderer"
    
    @classmethod
    def poll(cls, context):
        return context.active_object and context.active_object.type == 'CAMERA'
    
    def execute(self, context):
        cam_obj = context.active_object
        settings = cam_obj.data.cameraide_settings
        
        if not settings.use_custom_settings:
            self.report({'ERROR'}, "Custom settings are not enabled for this camera")
            return {'CANCELLED'}
            
        try:
            RenderCleanupManager.store_settings(context)
            remove_handlers()
            bpy.app.handlers.render_complete.append(render_complete_handler)
            bpy.app.handlers.render_cancel.append(render_cancel_handler)
            
            context.scene.camera = cam_obj
            RenderCleanupManager.apply_camera_settings(context, cam_obj)
            
            for area in context.screen.areas:
                if area.type == 'VIEW_3D':
                    override = context.copy()
                    override['area'] = area
                    bpy.ops.render.opengl('INVOKE_DEFAULT', animation=False, sequencer=False, write_still=True, view_context=True)
                    break
            
            return {'FINISHED'}
            
        except Exception as e:
            self.report({'ERROR'}, f"Render failed: {str(e)}")
            RenderCleanupManager.restore_settings(context)
            remove_handlers()
            return {'CANCELLED'}


class CAMERA_OT_render_snapshot_normal(Operator):
    bl_idname = "camera.render_snapshot_normal"
    bl_label = "Render Snapshot (Normal)"
    bl_description = "Render current frame using normal renderer"
    
    @classmethod
    def poll(cls, context):
        return context.active_object and context.active_object.type == 'CAMERA'
    
    def execute(self, context):
        cam_obj = context.active_object
        settings = cam_obj.data.cameraide_settings
        
        if not settings.use_custom_settings:
            self.report({'ERROR'}, "Custom settings are not enabled for this camera")
            return {'CANCELLED'}
            
        try:
            RenderCleanupManager.store_settings(context)
            
            context.scene.camera = cam_obj
            RenderCleanupManager.apply_camera_settings(context, cam_obj)
            
            if settings.output_format in {'MP4', 'MKV', 'MOV'}:
                res_x = context.scene.render.resolution_x
                res_y = context.scene.render.resolution_y
                if res_x % 2 or res_y % 2:
                    context.scene.render.resolution_x += (res_x % 2)
                    context.scene.render.resolution_y += (res_y % 2)
            
            bpy.ops.render.render('INVOKE_DEFAULT', animation=False, write_still=True)
            
            return {'FINISHED'}
            
        except Exception as e:
            self.report({'ERROR'}, f"Render failed: {str(e)}")
            RenderCleanupManager.restore_settings(context)
            return {'CANCELLED'}


# === PLAYBLAST OPERATORS ===
class CAMERA_OT_render_selected_viewport(Operator):
    bl_idname = "camera.render_selected_viewport"
    bl_label = "Render Viewport"
    bl_description = "Render animation using viewport renderer"
    
    @classmethod
    def poll(cls, context):
        return context.active_object and context.active_object.type == 'CAMERA'
    
    def execute(self, context):
        cam_obj = context.active_object
        settings = cam_obj.data.cameraide_settings
        
        if not settings.use_custom_settings:
            self.report({'ERROR'}, "Custom settings are not enabled for this camera")
            return {'CANCELLED'}
            
        try:
            RenderCleanupManager.store_settings(context)
            remove_handlers()
            bpy.app.handlers.render_complete.append(render_complete_handler)
            bpy.app.handlers.render_cancel.append(render_cancel_handler)
            
            context.scene.camera = cam_obj
            RenderCleanupManager.apply_camera_settings(context, cam_obj)
            
            for area in context.screen.areas:
                if area.type == 'VIEW_3D':
                    override = context.copy()
                    override['area'] = area
                    bpy.ops.render.opengl('INVOKE_DEFAULT', animation=True, sequencer=False, write_still=False, view_context=True)
                    break
            
            return {'FINISHED'}
            
        except Exception as e:
            self.report({'ERROR'}, f"Render failed: {str(e)}")
            RenderCleanupManager.restore_settings(context)
            remove_handlers()
            return {'CANCELLED'}


class CAMERA_OT_render_selected_normal(Operator):
    bl_idname = "camera.render_selected_normal"
    bl_label = "Render Normal"
    bl_description = "Render selected camera with normal render"
    
    @classmethod
    def poll(cls, context):
        return context.active_object and context.active_object.type == 'CAMERA'
    
    def execute(self, context):
        cam_obj = context.active_object
        settings = cam_obj.data.cameraide_settings
        
        if not settings.use_custom_settings:
            self.report({'ERROR'}, "Custom settings are not enabled for this camera")
            return {'CANCELLED'}
            
        try:
            RenderCleanupManager.store_settings(context)
            context.scene.camera = cam_obj
            RenderCleanupManager.apply_camera_settings(context, cam_obj)
            
            bpy.ops.render.render('INVOKE_DEFAULT', animation=True)
            return {'FINISHED'}
            
        except Exception as e:
            self.report({'ERROR'}, f"Render failed: {str(e)}")
            RenderCleanupManager.restore_settings(context)
            return {'CANCELLED'}


# === BATCH RENDER OPERATORS ===
class CAMERA_OT_render_all_viewport(Operator):
    bl_idname = "camera.render_all_viewport"
    bl_label = "Render All Cameras"
    bl_description = "Render all cameras with viewport render (timeline-ordered for marker mode)"
    
    _current_camera = None
    _current_index = -1
    _has_rendered = False
    _last_frame = -1
    _timer = None
    _frame_zero_time = None
    _render_queue = []

    @classmethod
    def reset_flags(cls):
        """Reset all operator flags"""
        print("=== Resetting viewport render flags ===")
        cls._current_camera = None
        cls._current_index = -1
        cls._has_rendered = False
        cls._last_frame = -1
        cls._frame_zero_time = None
        cls._render_queue = []
        
        handlers_to_remove = []
        for handler in bpy.app.handlers.frame_change_post:
            if hasattr(handler, 'has_rendered'):
                handlers_to_remove.append(handler)
        
        for handler in handlers_to_remove:
            bpy.app.handlers.frame_change_post.remove(handler)
    
    @classmethod
    def frame_change(cls, scene, depsgraph):
        """Frame change handler"""
        current_frame = scene.frame_current
        if not cls._current_camera:
            return
        
        if cls._current_index >= 0 and cls._current_index < len(cls._render_queue):
            _, _, end_frame = cls._render_queue[cls._current_index]
            
            if current_frame >= end_frame:
                cls._has_rendered = True
        
        if current_frame == 0:
            if cls._frame_zero_time is None:
                cls._frame_zero_time = time.time()
        else:
            cls._frame_zero_time = None
            
        cls._last_frame = current_frame
    
    def check_render_complete(self, context):
        """Check if current render job is complete"""
        if not self._current_camera:
            return False
            
        current_frame = context.scene.frame_current
        
        if self._has_rendered and current_frame == 0 and self._frame_zero_time:
            time_at_zero = time.time() - self._frame_zero_time
            if time_at_zero >= 1:
                return True
        return False
        
    def start_next_render(self, context):
        """Setup and start next render job"""
        print("\n=== Starting Next Render Job ===")
        self.__class__._current_index += 1
        cam_obj, start, end = self._render_queue[self._current_index]
        self.__class__._current_camera = cam_obj
        
        print(f"Job {self._current_index + 1}/{len(self._render_queue)}: {cam_obj.name} [{start}-{end}]")
        
        self.__class__._has_rendered = False
        self.__class__._last_frame = -1
        
        context.scene.camera = cam_obj
        RenderCleanupManager.store_settings(context)
        RenderCleanupManager.apply_camera_settings(context, cam_obj, frame_range=(start, end))
        
        bpy.ops.render.opengl('INVOKE_DEFAULT', animation=True, 
                            sequencer=False, write_still=False, view_context=True)
    
    def execute(self, context):
        print("\n=== Starting Batch Viewport Render ===")
        
        cameras = [obj for obj in context.scene.objects 
                  if obj.type == 'CAMERA' 
                  and obj.data.cameraide_settings.use_custom_settings]
        
        if not cameras:
            self.report({'WARNING'}, "No cameras with settings enabled")
            return {'CANCELLED'}
        
        # Build render queue based on frame range mode
        self._render_queue = []
        for cam_obj in cameras:
            ranges = get_all_marker_ranges(cam_obj)
            for start, end in ranges:
                self._render_queue.append((cam_obj, start, end))
        
        print(f"Built render queue: {len(self._render_queue)} jobs")
        
        self.__class__.reset_flags()
        
        if self.__class__.frame_change not in bpy.app.handlers.frame_change_post:
            bpy.app.handlers.frame_change_post.append(self.__class__.frame_change)
        
        wm = context.window_manager
        self._timer = wm.event_timer_add(0.5, window=context.window)
        wm.modal_handler_add(self)
        
        return {'RUNNING_MODAL'}
    
    def cleanup(self, context):
        """Clean up timer and restore settings"""
        print("\n=== Cleaning Up ===")
        if self._timer:
            context.window_manager.event_timer_remove(self._timer)
        
        if self.__class__.frame_change in bpy.app.handlers.frame_change_post:
            bpy.app.handlers.frame_change_post.remove(self.__class__.frame_change)
            
        RenderCleanupManager.restore_settings(context)
        self.__class__.reset_flags()
    
    def modal(self, context, event):
        if event.type == 'TIMER':
            if self._current_index == -1:
                self.start_next_render(context)
            elif self.check_render_complete(context):
                if self._current_index >= len(self._render_queue) - 1:
                    self.cleanup(context)
                    return {'FINISHED'}
                self.start_next_render(context)
        
        return {'PASS_THROUGH'}

    def cancel(self, context):
        self.cleanup(context)
        return {'CANCELLED'}


class CAMERA_OT_render_all_normal(Operator):
    bl_idname = "camera.render_all_normal"
    bl_label = "Render All Cameras (Normal)"
    bl_description = "Render all cameras with normal render (timeline-ordered for marker mode)"
    
    _render_queue = []
    _current_index = -1
    _render_complete = False
    
    @classmethod
    def poll(cls, context):
        return any(
            obj.type == 'CAMERA' and obj.data.cameraide_settings.use_custom_settings 
            for obj in context.scene.objects
        )
    
    def execute(self, context):
        cameras = [
            obj for obj in context.scene.objects 
            if obj.type == 'CAMERA' and obj.data.cameraide_settings.use_custom_settings
        ]
        
        if not cameras:
            self.report({'WARNING'}, "No cameras with settings found")
            return {'CANCELLED'}
        
        # Build render queue based on frame range mode
        self._render_queue = []
        for cam_obj in cameras:
            ranges = get_all_marker_ranges(cam_obj)
            for start, end in ranges:
                self._render_queue.append((cam_obj, start, end))
        
        print(f"Normal render queue: {len(self._render_queue)} jobs")
        
        self._current_index = -1
        self._render_complete = False
        
        bpy.app.handlers.render_complete.append(self.render_complete_handler)
        bpy.app.handlers.render_cancel.append(self.render_cancel_handler)
        
        self.render_next_job(context)
        
        return {'RUNNING_MODAL'}
    
    def render_next_job(self, context):
        """Prepare and start next render job"""
        self._current_index += 1
        
        if self._current_index >= len(self._render_queue):
            self.finish_rendering(context)
            return
        
        cam_obj, start, end = self._render_queue[self._current_index]
        context.scene.camera = cam_obj
        
        RenderCleanupManager.store_settings(context)
        RenderCleanupManager.apply_camera_settings(context, cam_obj, frame_range=(start, end))
        
        print(f"Rendering job {self._current_index + 1}/{len(self._render_queue)}: {cam_obj.name} [{start}-{end}]")
        
        bpy.ops.render.render('INVOKE_DEFAULT', animation=True)
    
    def render_complete_handler(self, scene, depsgraph):
        """Handler called when a render is complete"""
        if self._current_index < len(self._render_queue) - 1:
            self.render_next_job(bpy.context)
        else:
            self._render_complete = True
    
    def render_cancel_handler(self, scene, depsgraph):
        """Handler called if render is cancelled"""
        self.finish_rendering(bpy.context)
    
    def finish_rendering(self, context):
        """Cleanup after rendering"""
        if self.render_complete_handler in bpy.app.handlers.render_complete:
            bpy.app.handlers.render_complete.remove(self.render_complete_handler)
        if self.render_cancel_handler in bpy.app.handlers.render_cancel:
            bpy.app.handlers.render_cancel.remove(self.render_cancel_handler)
        
        RenderCleanupManager.restore_settings(context)
        
        self._render_queue = []
        self._current_index = -1
        
        print("Batch rendering complete")
    
    def modal(self, context, event):
        if self._render_complete:
            return {'FINISHED'}
        return {'PASS_THROUGH'}
    
    def cancel(self, context):
        self.finish_rendering(context)
        return {'CANCELLED'}


class CameraRenderOperatorBase:
    """Base class for render operators (for backwards compatibility)"""
    pass


def register():
    bpy.utils.register_class(CAMERA_OT_render_snapshot_viewport)
    bpy.utils.register_class(CAMERA_OT_render_snapshot_normal)
    bpy.utils.register_class(CAMERA_OT_render_selected_viewport)
    bpy.utils.register_class(CAMERA_OT_render_selected_normal)
    bpy.utils.register_class(CAMERA_OT_render_all_viewport)
    bpy.utils.register_class(CAMERA_OT_render_all_normal)

def unregister():
    bpy.utils.unregister_class(CAMERA_OT_render_all_normal)
    bpy.utils.unregister_class(CAMERA_OT_render_all_viewport)
    bpy.utils.unregister_class(CAMERA_OT_render_selected_normal)
    bpy.utils.unregister_class(CAMERA_OT_render_selected_viewport)
    bpy.utils.unregister_class(CAMERA_OT_render_snapshot_normal)
    bpy.utils.unregister_class(CAMERA_OT_render_snapshot_viewport)