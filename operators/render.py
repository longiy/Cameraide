import bpy
import os
from bpy.types import Operator

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
            'color_depth': context.scene.render.image_settings.color_depth if hasattr(context.scene.render.image_settings, 'color_depth') else None,
            'compression': context.scene.render.image_settings.compression if hasattr(context.scene.render.image_settings, 'compression') else None,
            'quality': context.scene.render.image_settings.quality if hasattr(context.scene.render.image_settings, 'quality') else None,
            'exr_codec': context.scene.render.image_settings.exr_codec if hasattr(context.scene.render.image_settings, 'exr_codec') else None,
            # Store view transform settings
            'view_transform': context.scene.view_settings.view_transform,
            'look': context.scene.view_settings.look,
            'exposure': context.scene.view_settings.exposure,
            'gamma': context.scene.view_settings.gamma,
            'use_curve_mapping': context.scene.view_settings.use_curve_mapping
        }
        
        # Store FFMPEG settings only if they exist
        if context.scene.render.image_settings.file_format == 'FFMPEG':
            ffmpeg_settings = {
                'ffmpeg_format': context.scene.render.ffmpeg.format,
                'ffmpeg_codec': context.scene.render.ffmpeg.codec,
                'ffmpeg_audio_codec': context.scene.render.ffmpeg.audio_codec,
                'ffmpeg_preset': context.scene.render.ffmpeg.preset if hasattr(context.scene.render.ffmpeg, 'preset') else None
            }
            cls._original_settings.update(ffmpeg_settings)
    
    @classmethod
    def restore_settings(cls, context):
        """Restore original render settings"""
        if cls._original_settings:
            for key, value in cls._original_settings.items():
                if value is None:
                    continue
                    
                if key.startswith('ffmpeg_'):
                    if context.scene.render.image_settings.file_format == 'FFMPEG':
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
    def apply_camera_settings(cls, context, cam_obj):
        """Apply camera settings to render"""
        settings = cam_obj.data.cameraide_settings
        cls._current_camera = cam_obj
        
        # Basic settings
        context.scene.frame_start = settings.frame_start
        context.scene.frame_end = settings.frame_end
        context.scene.frame_step = settings.frame_step
        context.scene.render.resolution_x = settings.resolution_x
        context.scene.render.resolution_y = settings.resolution_y
        context.scene.render.resolution_percentage = settings.resolution_percentage
        context.scene.render.film_transparent = settings.film_transparent
        context.scene.render.use_stamp = settings.burn_metadata
        
        # Format settings
        if settings.file_format == 'FFMPEG':
            cls._apply_ffmpeg_settings(context, settings)
        else:
            context.scene.render.image_settings.file_format = settings.file_format
            # Apply format-specific settings
            cls._apply_format_settings(context, settings)
            
        # Output path
        filename = f"{cam_obj.name}_" if settings.include_camera_name else ""
        filename += settings.file_name
        filepath = os.path.join(bpy.path.abspath(settings.output_folder), filename)
        context.scene.render.filepath = filepath
    
    @classmethod
    def _apply_format_settings(cls, context, settings):
        """Apply format-specific settings"""
        image_settings = context.scene.render.image_settings
        
        if settings.file_format == 'PNG':
            image_settings.color_mode = 'RGBA'
            image_settings.color_depth = settings.png_color_depth
            image_settings.compression = settings.png_compression
            
        elif settings.file_format == 'JPEG':
            image_settings.color_mode = 'RGB'
            image_settings.quality = settings.jpeg_quality
            
        elif settings.file_format == 'OPEN_EXR':
            image_settings.color_mode = 'RGBA'
            image_settings.color_depth = settings.exr_color_depth
            image_settings.exr_codec = settings.exr_codec
            if hasattr(image_settings, 'use_preview'):
                image_settings.use_preview = settings.exr_preview
    
    @classmethod
    def _apply_ffmpeg_settings(cls, context, settings):
        """Apply FFMPEG-specific settings"""
        context.scene.render.image_settings.file_format = 'FFMPEG'
        context.scene.render.ffmpeg.format = settings.ffmpeg_format
        context.scene.render.ffmpeg.codec = settings.ffmpeg_codec
        context.scene.render.ffmpeg.audio_codec = settings.ffmpeg_audio_codec
        
        if settings.ffmpeg_audio_codec == 'MP3':
            context.scene.render.ffmpeg.audio_bitrate = settings.ffmpeg_audio_bitrate
            
        if hasattr(context.scene.render.ffmpeg, 'preset'):
            context.scene.render.ffmpeg.preset = settings.ffmpeg_preset
            
        if settings.ffmpeg_codec == 'H264':
            if settings.ffmpeg_constant_rate_factor == 'NONE':
                context.scene.render.ffmpeg.constant_rate_factor = 'NONE'
                context.scene.render.ffmpeg.video_bitrate = settings.ffmpeg_video_bitrate
                context.scene.render.ffmpeg.minrate = settings.ffmpeg_minrate
                context.scene.render.ffmpeg.maxrate = settings.ffmpeg_maxrate
            else:
                context.scene.render.ffmpeg.constant_rate_factor = settings.ffmpeg_constant_rate_factor
            context.scene.render.ffmpeg.gopsize = settings.ffmpeg_gopsize
        else:
            context.scene.render.ffmpeg.constant_rate_factor = 'LOSSLESS'


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
            # Store settings and register handlers
            RenderCleanupManager.store_settings(context)
            remove_handlers()  # Remove any existing handlers first
            bpy.app.handlers.render_complete.append(render_complete_handler)
            bpy.app.handlers.render_cancel.append(render_cancel_handler)
            
            # Apply camera settings
            context.scene.camera = cam_obj
            RenderCleanupManager.apply_camera_settings(context, cam_obj)
            
            # Find active 3D viewport
            for area in context.screen.areas:
                if area.type == 'VIEW_3D':
                    # Use context override to ensure the operator runs in the 3D viewport
                    override = context.copy()
                    override['area'] = area
                    # Try the viewport render animation operator
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
    bl_description = "Render animation using current render engine"
    
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
            # Store settings and register handlers
            RenderCleanupManager.store_settings(context)
            remove_handlers()  # Remove any existing handlers first
            bpy.app.handlers.render_complete.append(render_complete_handler)
            bpy.app.handlers.render_cancel.append(render_cancel_handler)
            
            # Apply camera settings
            context.scene.camera = cam_obj
            RenderCleanupManager.apply_camera_settings(context, cam_obj)
            
            # Start render
            bpy.ops.render.render('INVOKE_DEFAULT', animation=True)
            return {'FINISHED'}
            
        except Exception as e:
            self.report({'ERROR'}, f"Render failed: {str(e)}")
            RenderCleanupManager.restore_settings(context)
            remove_handlers()
            return {'CANCELLED'}

def register():
    bpy.utils.register_class(CAMERA_OT_render_selected_viewport)
    bpy.utils.register_class(CAMERA_OT_render_selected_normal)

def unregister():
    remove_handlers()  # Clean up any lingering handlers
    bpy.utils.unregister_class(CAMERA_OT_render_selected_normal)
    bpy.utils.unregister_class(CAMERA_OT_render_selected_viewport)