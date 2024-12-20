import bpy
import os
from bpy.types import Operator

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

        # Store original settings
        original_settings = {
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
            'ffmpeg_format': getattr(context.scene.render.ffmpeg, 'format', None),
            'ffmpeg_codec': getattr(context.scene.render.ffmpeg, 'codec', None),
            'ffmpeg_audio_codec': getattr(context.scene.render.ffmpeg, 'audio_codec', None),
            'ffmpeg_preset': getattr(context.scene.render.ffmpeg, 'preset', None)
        }

        try:
            # Apply basic settings
            context.scene.frame_start = settings.frame_start
            context.scene.frame_end = settings.frame_end
            context.scene.frame_step = settings.frame_step
            context.scene.render.resolution_x = settings.resolution_x
            context.scene.render.resolution_y = settings.resolution_y
            context.scene.render.resolution_percentage = settings.resolution_percentage
            context.scene.render.film_transparent = settings.film_transparent
            context.scene.render.use_stamp = settings.burn_metadata

            # Set the camera as active
            context.scene.camera = cam_obj

            # Apply format-specific settings
            if settings.file_format == 'FFMPEG':
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
            else:
                context.scene.render.image_settings.file_format = settings.file_format

            # Set output path
            filename = ""
            if settings.include_camera_name:
                filename += f"{cam_obj.name}_"
            filename += settings.file_name
            
            filepath = os.path.join(bpy.path.abspath(settings.output_folder), filename)
            context.scene.render.filepath = filepath

            # Start render
            bpy.ops.render.opengl(animation=True)

            return {'FINISHED'}

        except Exception as e:
            self.report({'ERROR'}, f"Render failed: {str(e)}")
            return {'CANCELLED'}

        finally:
            # Restore original settings
            context.scene.frame_start = original_settings['frame_start']
            context.scene.frame_end = original_settings['frame_end']
            context.scene.frame_step = original_settings['frame_step']
            context.scene.render.filepath = original_settings['filepath']
            context.scene.render.resolution_x = original_settings['resolution_x']
            context.scene.render.resolution_y = original_settings['resolution_y']
            context.scene.render.resolution_percentage = original_settings['resolution_percentage']
            context.scene.render.film_transparent = original_settings['film_transparent']
            context.scene.render.use_stamp = original_settings['use_stamp']
            context.scene.render.image_settings.file_format = original_settings['file_format']
            
            # Restore FFMPEG settings
            if original_settings['ffmpeg_format']:
                context.scene.render.ffmpeg.format = original_settings['ffmpeg_format']
            if original_settings['ffmpeg_codec']:
                context.scene.render.ffmpeg.codec = original_settings['ffmpeg_codec']
            if original_settings['ffmpeg_audio_codec']:
                context.scene.render.ffmpeg.audio_codec = original_settings['ffmpeg_audio_codec']
            if original_settings['ffmpeg_preset']:
                context.scene.render.ffmpeg.preset = original_settings['ffmpeg_preset']

class CAMERA_OT_render_selected_normal(Operator):
    bl_idname = "camera.render_selected_normal"
    bl_label = "Render Normal"
    bl_description = "Render animation using current render engine"
    
    def execute(self, context):
        cam_obj = context.active_object
        if cam_obj.type != 'CAMERA':
            self.report({'ERROR'}, "Selected object is not a camera")
            return {'CANCELLED'}

        settings = cam_obj.data.cameraide_settings
        if not settings.use_custom_settings:
            self.report({'ERROR'}, "Custom settings are not enabled for this camera")
            return {'CANCELLED'}

        try:
            # Store original settings
            original_settings = {
                'frame_start': context.scene.frame_start,
                'frame_end': context.scene.frame_end,
                'filepath': context.scene.render.filepath,
                'resolution_x': context.scene.render.resolution_x,
                'resolution_y': context.scene.render.resolution_y,
                'resolution_percentage': context.scene.render.resolution_percentage,
                'film_transparent': context.scene.render.film_transparent,
                'use_stamp': context.scene.render.use_stamp,
                'frame_step': context.scene.frame_step,
                'file_format': context.scene.render.image_settings.file_format
            }

            # Apply camera settings
            context.scene.frame_start = settings.frame_start
            context.scene.frame_end = settings.frame_end
            context.scene.frame_step = settings.frame_step
            context.scene.render.resolution_x = settings.resolution_x
            context.scene.render.resolution_y = settings.resolution_y
            context.scene.render.resolution_percentage = settings.resolution_percentage
            context.scene.render.film_transparent = settings.film_transparent
            context.scene.render.use_stamp = settings.burn_metadata

            # Apply format-specific settings
            if settings.file_format == 'FFMPEG':
                context.scene.render.image_settings.file_format = 'FFMPEG'
                context.scene.render.ffmpeg.format = settings.ffmpeg_format
                context.scene.render.ffmpeg.codec = settings.ffmpeg_codec
                
                # Set audio codec
                context.scene.render.ffmpeg.audio_codec = settings.ffmpeg_audio_codec
                if settings.ffmpeg_audio_codec == 'MP3':
                    context.scene.render.ffmpeg.audio_bitrate = settings.ffmpeg_audio_bitrate
                
                # Set quality/bitrate for H.264
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
                    
                # Set encoding speed preset
                if hasattr(context.scene.render.ffmpeg, 'preset'):
                    context.scene.render.ffmpeg.preset = settings.ffmpeg_preset
            else:
                # Handle other formats (PNG, JPEG, EXR)
                context.scene.render.image_settings.file_format = settings.file_format

            # Set the camera as active
            context.scene.camera = cam_obj

            # Set output path
            filename = ""
            if settings.include_camera_name:
                filename += f"{cam_obj.name}_"
            filename += settings.file_name
            
            filepath = os.path.join(bpy.path.abspath(settings.output_folder), filename)
            context.scene.render.filepath = filepath

            # Start render
            bpy.ops.render.render('INVOKE_DEFAULT', animation=True)

            return {'FINISHED'}

        except Exception as e:
            self.report({'ERROR'}, f"Render failed: {str(e)}")
            return {'CANCELLED'}

        finally:
            # Restore original settings
            for key, value in original_settings.items():
                if hasattr(context.scene.render, key):
                    setattr(context.scene.render, key, value)
                elif hasattr(context.scene.render.image_settings, key):
                    setattr(context.scene.render.image_settings, key, value)
                elif hasattr(context.scene, key):
                    setattr(context.scene, key, value)

def register():
    bpy.utils.register_class(CAMERA_OT_render_selected_viewport)
    bpy.utils.register_class(CAMERA_OT_render_selected_normal)

def unregister():
    bpy.utils.unregister_class(CAMERA_OT_render_selected_normal)
    bpy.utils.unregister_class(CAMERA_OT_render_selected_viewport)