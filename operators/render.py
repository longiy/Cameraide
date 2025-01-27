import bpy
import os
from bpy.types import Operator
import time

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
            # Store view transform settings
            'view_transform': context.scene.view_settings.view_transform,
            'look': context.scene.view_settings.look,
            'exposure': context.scene.view_settings.exposure,
            'gamma': context.scene.view_settings.gamma,
            'use_curve_mapping': context.scene.view_settings.use_curve_mapping
        }
        
        # Store format-specific settings if needed
        current_format = context.scene.render.image_settings.file_format
        if current_format in {'PNG', 'JPEG', 'OPEN_EXR'}:
            cls._store_image_settings(context)
        elif current_format == 'FFMPEG':
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
            'ffmpeg_format': ffmpeg.format,
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
        from ..utils.callbacks import get_clean_camera_name  # Add this import
        
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

        # Construct full output path
        base_path = bpy.path.abspath(settings.output_path)
        subfolder = settings.output_subfolder
        # Use clean camera name when including camera name in filename
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
            # Apply format-specific settings
            cls._apply_format_settings(context, settings)
        else:  # Video formats
            context.scene.render.image_settings.file_format = 'FFMPEG'
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
        context.scene.render.ffmpeg.format = {
            'MP4': 'MPEG4',
            'MKV': 'MKV',
            'MOV': 'QUICKTIME'
        }[settings.output_format]
        
        if settings.output_format == 'MOV':
            # QuickTime with Animation codec
            context.scene.render.ffmpeg.codec = 'QTRLE'
            if hasattr(context.scene.render.ffmpeg, 'constant_rate_factor'):
                context.scene.render.ffmpeg.constant_rate_factor = 'LOSSLESS'
            context.scene.render.ffmpeg.gopsize = 1
        else:
            # MP4 and MKV with H.264
            context.scene.render.ffmpeg.codec = 'H264'
            if hasattr(context.scene.render.ffmpeg, 'constant_rate_factor'):
                context.scene.render.ffmpeg.constant_rate_factor = 'HIGH'
            context.scene.render.ffmpeg.video_bitrate = 6000
            context.scene.render.ffmpeg.minrate = 0
            context.scene.render.ffmpeg.maxrate = 9000
            context.scene.render.ffmpeg.gopsize = 12
        
        # Audio settings
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
    bl_description = "Render all Cameras with Normal render"
    
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
            
            # Apply camera settings
            context.scene.camera = cam_obj
            RenderCleanupManager.apply_camera_settings(context, cam_obj)
            
            # Start render
            bpy.ops.render.render('INVOKE_DEFAULT', animation=True)
            return {'FINISHED'}
            
        except Exception as e:
            self.report({'ERROR'}, f"Render failed: {str(e)}")
            RenderCleanupManager.restore_settings(context)
            return {'CANCELLED'}
        
class CAMERA_OT_render_all_normal(Operator):
    bl_idname = "camera.render_all_normal"
    bl_label = "Render All Cameras (Normal)"
    bl_description = "Render all Cameras with Normally"
    
    is_rendering: bpy.props.BoolProperty(default=False)
    render_started: bpy.props.BoolProperty(default=False)
    last_frame: bpy.props.IntProperty(default=-1)
    
    def prepare_next_camera(self, context):
        """Prepare the next camera for rendering"""
        # Move to next camera
        self.current_index += 1
        camera = self.cameras[self.current_index]
        print(f"\nProcessing camera {self.current_index + 1}/{len(self.cameras)}: {camera.name}")
        
        # Setup camera
        context.scene.camera = camera
        
        # Force camera view in all 3D viewports
        for area in context.screen.areas:
            if area.type == 'VIEW_3D':
                area.spaces[0].region_3d.view_perspective = 'CAMERA'
        
        # Store and apply settings
        RenderCleanupManager.store_settings(context)
        RenderCleanupManager.apply_camera_settings(context, camera)
        
        # Get end frame for this camera
        self.last_frame = camera.data.cameraide_settings.frame_end
        
        # Reset flags
        self.is_rendering = False
        self.render_started = False
    
    def check_render_complete(self, context):
        """Check if the current render is complete"""
        # If we've reached the last frame, render is complete
        return context.scene.frame_current >= self.last_frame
    
    def modal(self, context, event):
        # If we haven't started rendering current camera yet
        if not self.render_started and not self.is_rendering:
            self.is_rendering = True
            self.render_started = True
            
            # Force a render using normal render engine
            bpy.ops.render.render('INVOKE_DEFAULT', animation=True)
            
        # Check if render is complete by checking current frame
        elif self.is_rendering and self.check_render_complete(context):
            self.is_rendering = False
            
            # Wait a bit to ensure render is truly complete
            time.sleep(0.1)
            
            # If we have more cameras to process
            if self.current_index < len(self.cameras) - 1:
                self.prepare_next_camera(context)
            else:
                # All cameras done
                print("\nFinished rendering all cameras")
                RenderCleanupManager.restore_settings(context)
                return {'FINISHED'}
        
        return {'PASS_THROUGH'}
    
    def execute(self, context):
        try:
            # Get all cameras with Cameraide enabled
            self.cameras = [obj for obj in context.scene.objects 
                          if obj.type == 'CAMERA' 
                          and obj.data.cameraide_settings.use_custom_settings]
            
            if not self.cameras:
                self.report({'WARNING'}, "No cameras with Cameraide settings enabled")
                return {'CANCELLED'}
            
            print(f"\nFound {len(self.cameras)} cameras to render")
            
            # Initialize variables
            self.current_index = -1
            self.is_rendering = False
            self.render_started = False
            self.last_frame = -1
            
            # Prepare first camera
            self.prepare_next_camera(context)
            
            # Add modal handler
            context.window_manager.modal_handler_add(self)
            
            return {'RUNNING_MODAL'}
            
        except Exception as e:
            self.report({'ERROR'}, f"Failed to start batch render: {str(e)}")
            print(f"Error: {str(e)}")
            return {'CANCELLED'}
    
    def cancel(self, context):
        RenderCleanupManager.restore_settings(context)
        return {'CANCELLED'}
        
class CAMERA_OT_render_all_viewport(Operator):
    bl_idname = "camera.render_all_viewport"
    bl_label = "Render All Cameras"
    bl_description = "Render all Cameras with Viewport render"
    
    is_rendering: bpy.props.BoolProperty(default=False)
    render_started: bpy.props.BoolProperty(default=False)
    last_frame: bpy.props.IntProperty(default=-1)
    
    def prepare_next_camera(self, context):
        """Prepare the next camera for rendering"""
        # Move to next camera
        self.current_index += 1
        camera = self.cameras[self.current_index]
        print(f"\nProcessing camera {self.current_index + 1}/{len(self.cameras)}: {camera.name}")
        
        # Setup camera
        context.scene.camera = camera
        
        # Force camera view in all 3D viewports
        for area in context.screen.areas:
            if area.type == 'VIEW_3D':
                area.spaces[0].region_3d.view_perspective = 'CAMERA'
        
        # Store and apply settings
        RenderCleanupManager.store_settings(context)
        RenderCleanupManager.apply_camera_settings(context, camera)
        
        # Get end frame for this camera
        self.last_frame = camera.data.cameraide_settings.frame_end
        
        # Reset flags
        self.is_rendering = False
        self.render_started = False
    
    def check_render_complete(self, context):
        """Check if the current render is complete"""
        # If we've reached the last frame, render is complete
        return context.scene.frame_current >= self.last_frame
    
    def modal(self, context, event):
        # If we haven't started rendering current camera yet
        if not self.render_started and not self.is_rendering:
            self.is_rendering = True
            self.render_started = True
            
            # Force a render
            bpy.ops.render.opengl('INVOKE_DEFAULT', animation=True, 
                                sequencer=False, write_still=False, view_context=True)
            
        # Check if render is complete by checking current frame
        elif self.is_rendering and self.check_render_complete(context):
            self.is_rendering = False
            
            # Wait a bit to ensure render is truly complete
            time.sleep(0.5)
            
            # If we have more cameras to process
            if self.current_index < len(self.cameras) - 1:
                self.prepare_next_camera(context)
            else:
                # All cameras done
                print("\nFinished rendering all cameras")
                RenderCleanupManager.restore_settings(context)
                return {'FINISHED'}
        
        return {'PASS_THROUGH'}
    
    def execute(self, context):
        try:
            # Get all cameras with Cameraide enabled
            self.cameras = [obj for obj in context.scene.objects 
                          if obj.type == 'CAMERA' 
                          and obj.data.cameraide_settings.use_custom_settings]
            
            if not self.cameras:
                self.report({'WARNING'}, "No cameras with Cameraide settings enabled")
                return {'CANCELLED'}
            
            print(f"\nFound {len(self.cameras)} cameras to render")
            
            # Initialize variables
            self.current_index = -1
            self.is_rendering = False
            self.render_started = False
            self.last_frame = -1
            
            # Prepare first camera
            self.prepare_next_camera(context)
            
            # Add modal handler
            context.window_manager.modal_handler_add(self)
            
            return {'RUNNING_MODAL'}
            
        except Exception as e:
            self.report({'ERROR'}, f"Failed to start batch render: {str(e)}")
            print(f"Error: {str(e)}")
            return {'CANCELLED'}
    
    def cancel(self, context):
        RenderCleanupManager.restore_settings(context)
        return {'CANCELLED'}

def register():
    bpy.utils.register_class(CAMERA_OT_render_selected_viewport)
    bpy.utils.register_class(CAMERA_OT_render_selected_normal)
    bpy.utils.register_class(CAMERA_OT_render_all_viewport)
    bpy.utils.register_class(CAMERA_OT_render_all_normal)

def unregister():
    bpy.utils.unregister_class(CAMERA_OT_render_all_normal)
    bpy.utils.unregister_class(CAMERA_OT_render_all_viewport)
    bpy.utils.unregister_class(CAMERA_OT_render_selected_normal)
    bpy.utils.unregister_class(CAMERA_OT_render_selected_viewport)