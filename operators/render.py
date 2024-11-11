import bpy
import os
from bpy.types import Operator
from bpy.props import FloatProperty, BoolProperty

class CAMERA_OT_render_selected_viewport(Operator):
    bl_idname = "camera.render_selected_viewport"
    bl_label = "Render Viewport"
    bl_description = "Render animation using viewport renderer"
    
    _timer = None
    _current_frame = 0
    _total_frames = 0
    
    def modal(self, context, event):
        if event.type == 'ESC':
            self.report({'INFO'}, "Rendering canceled by user")
            self.finish(context)
            return {'FINISHED'}

        if event.type == 'TIMER':
            if self._current_frame <= context.scene.frame_end:
                context.scene.frame_set(self._current_frame)
                
                # Calculate and show only overall progress
                progress = (self._current_frame - context.scene.frame_start) / self._total_frames
                context.window_manager.progress_update(progress)
                
                # Generate filename with frame number
                settings = context.scene.camera.data.cameraide_settings
                filename = ""
                if settings.include_camera_name:
                    filename += f"{context.scene.camera.name}_"
                filename += settings.file_name
                filename += f"_{self._current_frame:04d}"
                
                if settings.file_format == 'PNG':
                    filename += ".png"
                elif settings.file_format == 'JPEG':
                    filename += ".jpg"
                elif settings.file_format == 'OPEN_EXR':
                    filename += ".exr"
                
                filepath = os.path.join(bpy.path.abspath(settings.output_folder), filename)
                context.scene.render.filepath = filepath
                
                # Render frame
                bpy.ops.render.opengl(write_still=True)
                
                self._current_frame += context.scene.camera.data.cameraide_settings.frame_step
            else:
                self.finish(context)
                return {'FINISHED'}
        
        return {'PASS_THROUGH'}

    def execute(self, context):
        cam_obj = context.active_object
        if cam_obj.type != 'CAMERA':
            self.report({'ERROR'}, "Selected object is not a camera")
            return {'CANCELLED'}

        settings = cam_obj.data.cameraide_settings
        if not settings.use_custom_settings:
            self.report({'ERROR'}, "Custom settings are not enabled for this camera")
            return {'CANCELLED'}

        # Store original settings
        self.original_settings = {
            'frame_start': context.scene.frame_start,
            'frame_end': context.scene.frame_end,
            'filepath': context.scene.render.filepath,
            'resolution_x': context.scene.render.resolution_x,
            'resolution_y': context.scene.render.resolution_y,
            'resolution_percentage': context.scene.render.resolution_percentage,
            'film_transparent': context.scene.render.film_transparent,
            'use_stamp': context.scene.render.use_stamp,
            'frame_step': context.scene.frame_step
        }

        try:
            # Apply settings
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

            # Initialize rendering variables
            self._current_frame = settings.frame_start
            self._total_frames = (settings.frame_end - settings.frame_start + 1)

            # Initialize progress bar
            context.window_manager.progress_begin(0, 1)

            # Add the timer
            wm = context.window_manager
            self._timer = wm.event_timer_add(0.1, window=context.window)
            wm.modal_handler_add(self)

            return {'RUNNING_MODAL'}
            
        except Exception as e:
            self.report({'ERROR'}, f"Setup failed: {str(e)}")
            self.restore_settings(context)
            return {'CANCELLED'}

    def finish(self, context):
        context.window_manager.progress_end()
        
        if hasattr(self, '_timer') and self._timer:
            wm = context.window_manager
            wm.event_timer_remove(self._timer)

        self.restore_settings(context)

    def restore_settings(self, context):
        if hasattr(self, 'original_settings'):
            context.scene.frame_start = self.original_settings['frame_start']
            context.scene.frame_end = self.original_settings['frame_end']
            context.scene.frame_step = self.original_settings['frame_step']
            context.scene.render.filepath = self.original_settings['filepath']
            context.scene.render.resolution_x = self.original_settings['resolution_x']
            context.scene.render.resolution_y = self.original_settings['resolution_y']
            context.scene.render.resolution_percentage = self.original_settings['resolution_percentage']
            context.scene.render.film_transparent = self.original_settings['film_transparent']
            context.scene.render.use_stamp = self.original_settings['use_stamp']

class CAMERA_OT_render_selected_normal(Operator):
    bl_idname = "camera.render_selected_normal"
    bl_label = "Render Normal"
    bl_description = "Render animation using current render engine (like F12)"

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
                'file_format': context.scene.render.image_settings.file_format,
                'color_mode': context.scene.render.image_settings.color_mode,
                'color_depth': context.scene.render.image_settings.color_depth,
                'exr_codec': context.scene.render.image_settings.exr_codec,
                'quality': context.scene.render.image_settings.quality,
                'compression': context.scene.render.image_settings.compression,
                'use_preview': context.scene.render.image_settings.use_preview,
                'resolution_x': context.scene.render.resolution_x,
                'resolution_y': context.scene.render.resolution_y,
                'resolution_percentage': context.scene.render.resolution_percentage,
                'film_transparent': context.scene.render.film_transparent,
                'use_stamp': context.scene.render.use_stamp,
                'frame_step': context.scene.frame_step
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
            if settings.file_format == 'PNG':
                context.scene.render.image_settings.file_format = 'PNG'
                context.scene.render.image_settings.color_mode = settings.png_color_mode
                context.scene.render.image_settings.color_depth = settings.png_color_depth
                context.scene.render.image_settings.compression = settings.png_compression
            elif settings.file_format == 'JPEG':
                context.scene.render.image_settings.file_format = 'JPEG'
                context.scene.render.image_settings.color_mode = settings.jpeg_color_mode
                context.scene.render.image_settings.quality = settings.jpeg_quality
            elif settings.file_format == 'OPEN_EXR':
                context.scene.render.image_settings.file_format = 'OPEN_EXR'
                context.scene.render.image_settings.color_mode = settings.exr_color_mode
                context.scene.render.image_settings.exr_codec = settings.exr_codec
                context.scene.render.image_settings.color_depth = settings.exr_color_depth
                context.scene.render.image_settings.use_preview = settings.exr_preview

            # Set the camera as active
            context.scene.camera = cam_obj

            # Set output path
            filename = ""
            if settings.include_camera_name:
                filename += f"{cam_obj.name}_"
            filename += settings.file_name
            
            filepath = os.path.join(bpy.path.abspath(settings.output_folder), filename)
            context.scene.render.filepath = filepath

            # Start render using Blender's native dialog
            bpy.ops.render.render('INVOKE_DEFAULT', animation=True)

            return {'FINISHED'}

        except Exception as e:
            self.report({'ERROR'}, f"Render failed: {str(e)}")
            return {'CANCELLED'}

        finally:
            # Restore original settings
            try:
                context.scene.frame_start = original_settings['frame_start']
                context.scene.frame_end = original_settings['frame_end']
                context.scene.frame_step = original_settings['frame_step']
                context.scene.render.filepath = original_settings['filepath']
                context.scene.render.image_settings.file_format = original_settings['file_format']
                context.scene.render.image_settings.color_mode = original_settings['color_mode']
                context.scene.render.resolution_x = original_settings['resolution_x']
                context.scene.render.resolution_y = original_settings['resolution_y']
                context.scene.render.resolution_percentage = original_settings['resolution_percentage']
                context.scene.render.film_transparent = original_settings['film_transparent']
                context.scene.render.use_stamp = original_settings['use_stamp']
            except:
                pass

def register():
    bpy.utils.register_class(CAMERA_OT_render_selected_viewport)
    bpy.utils.register_class(CAMERA_OT_render_selected_normal)

def unregister():
    bpy.utils.unregister_class(CAMERA_OT_render_selected_normal)
    bpy.utils.unregister_class(CAMERA_OT_render_selected_viewport)