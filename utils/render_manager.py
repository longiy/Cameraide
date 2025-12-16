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
            'media_type': scene.render.image_settings.media_type,  # Store first
            'file_format': scene.render.image_settings.file_format,
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
        
        if not cls._original_settings:
            return
        
        # CRITICAL: Restore media_type FIRST, then file_format
        # This prevents enum mismatch errors
        if 'media_type' in cls._original_settings:
            scene.render.image_settings.media_type = cls._original_settings['media_type']
        
        if 'file_format' in cls._original_settings:
            scene.render.image_settings.file_format = cls._original_settings['file_format']
        
        # Restore everything else
        for key, value in cls._original_settings.items():
            if value is None:
                continue
            
            # Skip media_type and file_format (already done)
            if key in ['media_type', 'file_format']:
                continue
                
            if key.startswith('ffmpeg_'):
                if scene.render.image_settings.file_format == 'FFMPEG':
                    clean_key = key.replace('ffmpeg_', '')
                    if hasattr(scene.render.ffmpeg, clean_key):
                        try:
                            setattr(scene.render.ffmpeg, clean_key, value)
                        except:
                            pass
            elif key in ['view_transform', 'look', 'exposure', 'gamma', 'use_curve_mapping']:
                try:
                    setattr(scene.view_settings, key, value)
                except:
                    pass
            elif hasattr(scene.render, key):
                try:
                    setattr(scene.render, key, value)
                except:
                    pass
            elif hasattr(scene.render.image_settings, key):
                try:
                    setattr(scene.render.image_settings, key, value)
                except:
                    pass
            elif hasattr(scene, key):
                try:
                    setattr(scene, key, value)
                except:
                    pass
        
        cls._original_settings = None
    
    @classmethod
    def apply_camera_settings(cls, context, cam_obj, frame_range=None, force_image_format=False):
        """Apply camera settings to render
        
        Args:
            force_image_format: If True, force PNG for single-frame renders (snapshots)
        """
        scene = context.scene
        settings = cam_obj.data.cameraide_settings
        cls._current_camera = cam_obj
        
        # Resolution
        res_x = settings.resolution_x
        res_y = settings.resolution_y
        percentage = settings.resolution_percentage
        
        # Check if video format
        is_video = settings.output_format in {'H264_MP4', 'H264_MKV', 'PRORES_MOV'}
        
        # For snapshots with video format, force PNG
        if force_image_format and is_video:
            is_video = False
            forced_format = 'PNG'
        else:
            forced_format = None
        
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
        if forced_format:
            # Force image format for snapshot
            scene.render.image_settings.media_type = 'IMAGE'
            scene.render.image_settings.file_format = forced_format
            scene.render.image_settings.color_mode = 'RGBA'
            scene.render.image_settings.color_depth = '8'
            scene.render.image_settings.compression = 15
        elif settings.output_format in {'PNG', 'JPEG', 'OPEN_EXR'}:
            scene.render.image_settings.media_type = 'IMAGE'
            scene.render.image_settings.file_format = settings.output_format
            apply_image_format(settings, context)
        else:
            apply_video_format(settings, context)