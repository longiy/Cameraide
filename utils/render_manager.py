"""Render settings manager for Cameraide"""
import bpy
import os
from ..render.formats.image import apply_image_format, store_image_settings
from ..render.formats.video import apply_video_format, store_video_settings
from .camera_names import get_clean_camera_name


class RenderCleanupManager:
    """Manages render settings storage and restoration"""
    
    _original_settings = None
    _current_camera = None
    
    @classmethod
    def store_settings(cls, context):
        """Store original render settings"""
        scene = context.scene
        
        cls._original_settings = {
            'frame_start': scene.frame_start,
            'frame_end': scene.frame_end,
            'filepath': scene.render.filepath,
            'resolution_x': scene.render.resolution_x,
            'resolution_y': scene.render.resolution_y,
            'resolution_percentage': scene.render.resolution_percentage,
            'film_transparent': scene.render.film_transparent,
            'use_stamp': scene.render.use_stamp,
            'frame_step': scene.frame_step,
            'file_format': scene.render.image_settings.file_format,
            'media_type': scene.render.image_settings.media_type,
            'color_mode': scene.render.image_settings.color_mode,
            'view_transform': scene.view_settings.view_transform,
            'look': scene.view_settings.look,
            'exposure': scene.view_settings.exposure,
            'gamma': scene.view_settings.gamma,
            'use_curve_mapping': scene.view_settings.use_curve_mapping
        }
        
        current_format = scene.render.image_settings.file_format
        if current_format in {'PNG', 'JPEG', 'OPEN_EXR'}:
            store_image_settings(cls._original_settings, context)
        elif current_format == 'FFMPEG':
            store_video_settings(cls._original_settings, context)

    @classmethod
    def restore_settings(cls, context):
        """Restore original render settings"""
        scene = context.scene
        
        if cls._original_settings:
            for key, value in cls._original_settings.items():
                if value is None:
                    continue
                    
                if key.startswith('ffmpeg_'):
                    if scene.render.image_settings.file_format == 'FFMPEG':
                        clean_key = key.replace('ffmpeg_', '')
                        if hasattr(scene.render.ffmpeg, clean_key):
                            setattr(scene.render.ffmpeg, clean_key, value)
                elif key in ['view_transform', 'look', 'exposure', 'gamma', 'use_curve_mapping']:
                    setattr(scene.view_settings, key, value)
                elif hasattr(scene.render, key):
                    setattr(scene.render, key, value)
                elif hasattr(scene.render.image_settings, key):
                    setattr(scene.render.image_settings, key, value)
                elif hasattr(scene, key):
                    setattr(scene, key, value)
            cls._original_settings = None
    
    @classmethod
    def apply_camera_settings(cls, context, cam_obj, frame_range=None):
        """Apply camera settings to render"""
        scene = context.scene
        settings = cam_obj.data.cameraide_settings
        cls._current_camera = cam_obj
        
        # Resolution
        res_x = settings.resolution_x
        res_y = settings.resolution_y
        percentage = settings.resolution_percentage
        
        is_video = settings.output_format in {'H264_MP4', 'H264_MKV', 'PRORES_MOV'}
        if is_video:
            scaled_x = int((res_x * percentage) / 100)
            scaled_y = int((res_y * percentage) / 100)
            res_x = scaled_x + (scaled_x % 2)
            res_y = scaled_y + (scaled_y % 2)
            scene.render.resolution_percentage = 100
        else:
            scene.render.resolution_percentage = percentage
            
        # Frame range
        if frame_range:
            scene.frame_start = frame_range[0]
            scene.frame_end = frame_range[1]
        else:
            from .marker_detection import get_effective_frame_range
            start, end = get_effective_frame_range(cam_obj)
            scene.frame_start = start
            scene.frame_end = end
        
        scene.frame_step = settings.frame_step
        scene.render.resolution_x = res_x
        scene.render.resolution_y = res_y
        scene.render.film_transparent = settings.film_transparent
        scene.render.use_stamp = settings.burn_metadata

        # Output path
        base_path = bpy.path.abspath(settings.output_path)
        subfolder = settings.output_subfolder
        if settings.include_camera_name:
            clean_name = get_clean_camera_name(cam_obj)
            filename = f"{clean_name}_{settings.output_filename}"
        else:
            filename = settings.output_filename
            
        filepath = os.path.join(base_path, subfolder, filename)
        scene.render.filepath = filepath
        
        # Format settings
        if settings.output_format in {'PNG', 'JPEG', 'OPEN_EXR'}:
            scene.render.image_settings.media_type = 'IMAGE'
            scene.render.image_settings.file_format = settings.output_format
            apply_image_format(settings, context)
        else:
            apply_video_format(settings, context)
