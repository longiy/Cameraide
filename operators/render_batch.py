"""Batch render operators - RENDER_WRITE HANDLER"""
import bpy
from bpy.types import Operator
from ..utils.render_manager import RenderCleanupManager
from ..utils.marker_detection import get_all_marker_ranges


class ViewportBatchRender:
    """Viewport batch render controller"""
    
    def __init__(self):
        self.queue = []
        self.current_index = -1
        self.is_rendering = False
        self.cameraide_handler = None
        self.is_active = False
        self.expected_end_frame = -1
        
    def build_queue(self, context):
        """Build render queue from cameras"""
        all_cameras = [
            obj for obj in context.scene.objects 
            if obj.type == 'CAMERA' and obj.data.cameraide_settings.use_custom_settings
        ]
        
        self.queue = []
        for cam_obj in all_cameras:
            ranges = get_all_marker_ranges(cam_obj)
            for start, end in ranges:
                self.queue.append((cam_obj, start, end))
        
        return len(self.queue)
    
    def disable_cameraide_handler(self):
        """Disable Cameraide's camera change handler"""
        for handler in bpy.app.handlers.depsgraph_update_post:
            handler_name = getattr(handler, '__name__', '')
            if 'camera' in handler_name.lower() or 'cameraide' in handler_name.lower():
                self.cameraide_handler = handler
                bpy.app.handlers.depsgraph_update_post.remove(handler)
                return
    
    def restore_cameraide_handler(self):
        """Restore Cameraide's camera change handler"""
        if self.cameraide_handler and self.cameraide_handler not in bpy.app.handlers.depsgraph_update_post:
            bpy.app.handlers.depsgraph_update_post.append(self.cameraide_handler)
    
    def on_frame_written(self, scene, depsgraph=None):
        """Called after each frame is written - check if this is the last frame"""
        current_frame = scene.frame_current
        print(f"[Viewport] Frame {current_frame} written (end={self.expected_end_frame})")
        
        if current_frame >= self.expected_end_frame:
            print(f"[Viewport] Last frame reached! Job {self.current_index + 1}/{len(self.queue)} complete")
            self.is_rendering = False
            
            if self.current_index < len(self.queue) - 1:
                print(f"[Viewport] Scheduling next job...")
                bpy.app.timers.register(self.start_next_render, first_interval=0.5)
            else:
                print(f"[Viewport] All jobs complete!")
                bpy.app.timers.register(self.cleanup, first_interval=0.5)
    
    def start_next_render(self):
        """Start next render job"""
        try:
            self.current_index += 1
            
            if self.current_index >= len(self.queue):
                self.cleanup()
                return None
            
            cam_obj, start, end = self.queue[self.current_index]
            self.expected_end_frame = end
            
            print(f"\n{'='*60}")
            print(f"[Viewport] Job {self.current_index + 1}/{len(self.queue)}")
            print(f"  Camera: {cam_obj.name}")
            print(f"  Frames: {start}-{end}")
            print(f"{'='*60}")
            
            bpy.context.scene.camera = cam_obj
            RenderCleanupManager.apply_camera_settings(
                bpy.context, cam_obj,
                frame_range=(start, end),
                force_image_format=False
            )
            
            self.is_rendering = True
            
            for area in bpy.context.screen.areas:
                if area.type == 'VIEW_3D':
                    override = bpy.context.copy()
                    override['area'] = area
                    bpy.ops.render.opengl('INVOKE_DEFAULT', animation=True,
                                         sequencer=False, write_still=False, view_context=True)
                    break
            
        except Exception as e:
            print(f"[Viewport] Error: {e}")
            import traceback
            traceback.print_exc()
            self.cleanup()
        
        return None
    
    def cleanup(self):
        """Cleanup handlers and restore settings"""
        print(f"\n[Viewport] Cleaning up...")
        
        self.is_active = False
        
        if viewport_frame_written_handler in bpy.app.handlers.render_write:
            bpy.app.handlers.render_write.remove(viewport_frame_written_handler)
            print(f"[Viewport] Removed render_write handler")
        if viewport_render_cancel_handler in bpy.app.handlers.render_cancel:
            bpy.app.handlers.render_cancel.remove(viewport_render_cancel_handler)
            print(f"[Viewport] Removed render_cancel handler")
        
        RenderCleanupManager.restore_settings(bpy.context)
        self.restore_cameraide_handler()
        
        print(f"[Viewport] Cleanup complete!\n")
        return None
    
    def start(self, context):
        """Start batch rendering"""
        print(f"\n[Viewport] Starting batch render")
        
        RenderCleanupManager.store_settings(context)
        self.disable_cameraide_handler()
        
        if viewport_frame_written_handler in bpy.app.handlers.render_write:
            bpy.app.handlers.render_write.remove(viewport_frame_written_handler)
        if viewport_render_cancel_handler in bpy.app.handlers.render_cancel:
            bpy.app.handlers.render_cancel.remove(viewport_render_cancel_handler)
        
        bpy.app.handlers.render_write.append(viewport_frame_written_handler)
        bpy.app.handlers.render_cancel.append(viewport_render_cancel_handler)
        print(f"[Viewport] Handlers added")
        
        self.current_index = -1
        self.is_rendering = False
        self.is_active = True
        self.expected_end_frame = -1
        
        bpy.app.timers.register(self.start_next_render, first_interval=0.5)


class NormalBatchRender:
    """Normal batch render controller"""
    
    def __init__(self):
        self.queue = []
        self.current_index = -1
        self.is_rendering = False
        self.cameraide_handler = None
        self.is_active = False
        
    def build_queue(self, context):
        """Build render queue from cameras"""
        all_cameras = [
            obj for obj in context.scene.objects 
            if obj.type == 'CAMERA' and obj.data.cameraide_settings.use_custom_settings
        ]
        
        self.queue = []
        for cam_obj in all_cameras:
            ranges = get_all_marker_ranges(cam_obj)
            for start, end in ranges:
                self.queue.append((cam_obj, start, end))
        
        return len(self.queue)
    
    def disable_cameraide_handler(self):
        """Disable Cameraide's camera change handler"""
        for handler in bpy.app.handlers.depsgraph_update_post:
            handler_name = getattr(handler, '__name__', '')
            if 'camera' in handler_name.lower() or 'cameraide' in handler_name.lower():
                self.cameraide_handler = handler
                bpy.app.handlers.depsgraph_update_post.remove(handler)
                return
    
    def restore_cameraide_handler(self):
        """Restore Cameraide's camera change handler"""
        if self.cameraide_handler and self.cameraide_handler not in bpy.app.handlers.depsgraph_update_post:
            bpy.app.handlers.depsgraph_update_post.append(self.cameraide_handler)
    
    def on_render_complete(self):
        """Called when render completes"""
        print(f"[Normal] Job {self.current_index + 1}/{len(self.queue)} complete")
        self.is_rendering = False
        
        if self.current_index < len(self.queue) - 1:
            bpy.app.timers.register(self.start_next_render, first_interval=0.5)
        else:
            print(f"[Normal] All jobs complete!")
            bpy.app.timers.register(self.cleanup, first_interval=0.5)
    
    def on_render_cancel(self):
        """Called if render cancelled"""
        print(f"[Normal] Render cancelled")
        bpy.app.timers.register(self.cleanup, first_interval=0.5)
    
    def start_next_render(self):
        """Start next render job"""
        try:
            self.current_index += 1
            
            if self.current_index >= len(self.queue):
                self.cleanup()
                return None
            
            cam_obj, start, end = self.queue[self.current_index]
            
            print(f"\n[Normal] Job {self.current_index + 1}/{len(self.queue)}")
            print(f"  Camera: {cam_obj.name}")
            print(f"  Frames: {start}-{end}")
            
            bpy.context.scene.camera = cam_obj
            RenderCleanupManager.apply_camera_settings(
                bpy.context, cam_obj,
                frame_range=(start, end),
                force_image_format=False
            )
            
            self.is_rendering = True
            bpy.ops.render.render('INVOKE_DEFAULT', animation=True)
            
        except Exception as e:
            print(f"[Normal] Error: {e}")
            import traceback
            traceback.print_exc()
            self.cleanup()
        
        return None
    
    def cleanup(self):
        """Cleanup handlers and restore settings"""
        print(f"[Normal] Cleaning up...")
        
        self.is_active = False
        
        if normal_render_complete_handler in bpy.app.handlers.render_complete:
            bpy.app.handlers.render_complete.remove(normal_render_complete_handler)
        if normal_render_cancel_handler in bpy.app.handlers.render_cancel:
            bpy.app.handlers.render_cancel.remove(normal_render_cancel_handler)
        
        RenderCleanupManager.restore_settings(bpy.context)
        self.restore_cameraide_handler()
        
        return None
    
    def start(self, context):
        """Start batch rendering"""
        RenderCleanupManager.store_settings(context)
        self.disable_cameraide_handler()
        
        if normal_render_complete_handler in bpy.app.handlers.render_complete:
            bpy.app.handlers.render_complete.remove(normal_render_complete_handler)
        if normal_render_cancel_handler in bpy.app.handlers.render_cancel:
            bpy.app.handlers.render_cancel.remove(normal_render_cancel_handler)
        
        bpy.app.handlers.render_complete.append(normal_render_complete_handler)
        bpy.app.handlers.render_cancel.append(normal_render_cancel_handler)
        
        self.current_index = -1
        self.is_rendering = False
        self.is_active = True
        
        bpy.app.timers.register(self.start_next_render, first_interval=0.5)


# Global instances
viewport_batch = ViewportBatchRender()
normal_batch = NormalBatchRender()


# Module-level handlers
def viewport_frame_written_handler(scene, depsgraph=None):
    """Handler for viewport frame written - fires after each frame"""
    if viewport_batch.is_active:
        viewport_batch.on_frame_written(scene, depsgraph)


def viewport_render_cancel_handler(scene, depsgraph=None):
    """Handler for viewport render cancellation"""
    if viewport_batch.is_active:
        print(f"[Viewport] Render cancelled")
        bpy.app.timers.register(viewport_batch.cleanup, first_interval=0.5)


def normal_render_complete_handler(scene, depsgraph=None):
    """Handler for normal render completion"""
    if normal_batch.is_active:
        normal_batch.on_render_complete()


def normal_render_cancel_handler(scene, depsgraph=None):
    """Handler for normal render cancellation"""
    if normal_batch.is_active:
        normal_batch.on_render_cancel()


class CAMERA_OT_render_all_viewport(Operator):
    """Render all cameras with viewport render"""
    bl_idname = "camera.render_all_viewport"
    bl_label = "Render All Cameras (Viewport)"
    bl_description = "Render all cameras with viewport render"
    
    def execute(self, context):
        queue_size = viewport_batch.build_queue(context)
        
        if queue_size == 0:
            self.report({'WARNING'}, "No cameras with custom settings enabled")
            return {'CANCELLED'}
        
        print(f"\n{'='*60}")
        print(f"[Viewport Batch] Starting {queue_size} jobs")
        print(f"{'='*60}\n")
        
        viewport_batch.start(context)
        
        self.report({'INFO'}, f"Started batch viewport render: {queue_size} jobs")
        return {'FINISHED'}


class CAMERA_OT_render_all_normal(Operator):
    """Render all cameras with normal render"""
    bl_idname = "camera.render_all_normal"
    bl_label = "Render All Cameras (Normal)"
    bl_description = "Render all cameras with normal render"
    
    @classmethod
    def poll(cls, context):
        return any(
            obj.type == 'CAMERA' and obj.data.cameraide_settings.use_custom_settings 
            for obj in context.scene.objects
        )
    
    def execute(self, context):
        queue_size = normal_batch.build_queue(context)
        
        if queue_size == 0:
            self.report({'WARNING'}, "No cameras with custom settings found")
            return {'CANCELLED'}
        
        print(f"\n{'='*60}")
        print(f"[Normal Batch] Starting {queue_size} jobs")
        print(f"{'='*60}\n")
        
        normal_batch.start(context)
        
        self.report({'INFO'}, f"Started batch normal render: {queue_size} jobs")
        return {'FINISHED'}


def register():
    bpy.utils.register_class(CAMERA_OT_render_all_viewport)
    bpy.utils.register_class(CAMERA_OT_render_all_normal)


def unregister():
    if viewport_frame_written_handler in bpy.app.handlers.render_write:
        bpy.app.handlers.render_write.remove(viewport_frame_written_handler)
    if viewport_render_cancel_handler in bpy.app.handlers.render_cancel:
        bpy.app.handlers.render_cancel.remove(viewport_render_cancel_handler)
    if normal_render_complete_handler in bpy.app.handlers.render_complete:
        bpy.app.handlers.render_complete.remove(normal_render_complete_handler)
    if normal_render_cancel_handler in bpy.app.handlers.render_cancel:
        bpy.app.handlers.render_cancel.remove(normal_render_cancel_handler)
    
    viewport_batch.restore_cameraide_handler()
    normal_batch.restore_cameraide_handler()
    
    bpy.utils.unregister_class(CAMERA_OT_render_all_normal)
    bpy.utils.unregister_class(CAMERA_OT_render_all_viewport)