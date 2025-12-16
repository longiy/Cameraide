"""Batch render operators for multiple cameras"""
import bpy
import time
from bpy.types import Operator
from ..utils.render_manager import RenderCleanupManager
from ..utils.marker_detection import get_all_marker_ranges


class CAMERA_OT_render_all_viewport(Operator):
    """Render all cameras with viewport render"""
    bl_idname = "camera.render_all_viewport"
    bl_label = "Render All Cameras"
    bl_description = "Render all cameras with viewport render"
    
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
        self.__class__._current_index += 1
        cam_obj, start, end = self._render_queue[self._current_index]
        self.__class__._current_camera = cam_obj
        
        self.__class__._has_rendered = False
        self.__class__._last_frame = -1
        
        context.scene.camera = cam_obj
        RenderCleanupManager.store_settings(context)
        RenderCleanupManager.apply_camera_settings(context, cam_obj, frame_range=(start, end))
        
        bpy.ops.render.opengl('INVOKE_DEFAULT', animation=True, 
                            sequencer=False, write_still=False, view_context=True)
    
    def execute(self, context):
        cameras = [obj for obj in context.scene.objects 
                  if obj.type == 'CAMERA' 
                  and obj.data.cameraide_settings.use_custom_settings]
        
        if not cameras:
            self.report({'WARNING'}, "No cameras with settings enabled")
            return {'CANCELLED'}
        
        self._render_queue = []
        for cam_obj in cameras:
            ranges = get_all_marker_ranges(cam_obj)
            for start, end in ranges:
                self._render_queue.append((cam_obj, start, end))
        
        self.__class__.reset_flags()
        
        if self.__class__.frame_change not in bpy.app.handlers.frame_change_post:
            bpy.app.handlers.frame_change_post.append(self.__class__.frame_change)
        
        wm = context.window_manager
        self._timer = wm.event_timer_add(0.5, window=context.window)
        wm.modal_handler_add(self)
        
        return {'RUNNING_MODAL'}
    
    def cleanup(self, context):
        """Clean up timer and restore settings"""
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
    """Render all cameras with normal render"""
    bl_idname = "camera.render_all_normal"
    bl_label = "Render All Cameras (Normal)"
    bl_description = "Render all cameras with normal render"
    
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
        
        self._render_queue = []
        for cam_obj in cameras:
            ranges = get_all_marker_ranges(cam_obj)
            for start, end in ranges:
                self._render_queue.append((cam_obj, start, end))
        
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
    
    def modal(self, context, event):
        if self._render_complete:
            return {'FINISHED'}
        return {'PASS_THROUGH'}
    
    def cancel(self, context):
        self.finish_rendering(context)
        return {'CANCELLED'}


def register():
    bpy.utils.register_class(CAMERA_OT_render_all_viewport)
    bpy.utils.register_class(CAMERA_OT_render_all_normal)


def unregister():
    bpy.utils.unregister_class(CAMERA_OT_render_all_normal)
    bpy.utils.unregister_class(CAMERA_OT_render_all_viewport)
