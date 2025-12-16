"""Batch render operators for multiple cameras - REDESIGNED"""
import bpy
from bpy.types import Operator
from ..utils.render_manager import RenderCleanupManager
from ..utils.marker_detection import get_all_marker_ranges


class BatchRenderQueue:
    """Global render queue manager"""
    queue = []
    current_index = -1
    is_active = False
    render_in_progress = False
    controller_operator = None
    render_type = None  # 'VIEWPORT' or 'NORMAL'
    
    @classmethod
    def reset(cls):
        """Reset queue state"""
        cls.queue = []
        cls.current_index = -1
        cls.is_active = False
        cls.render_in_progress = False
        cls.controller_operator = None
        cls.render_type = None
    
    @classmethod
    def start_queue(cls, queue, render_type, controller):
        """Initialize queue for batch rendering"""
        cls.queue = queue
        cls.current_index = -1
        cls.is_active = True
        cls.render_in_progress = False
        cls.render_type = render_type
        cls.controller_operator = controller
    
    @classmethod
    def mark_render_complete(cls):
        """Called by handlers when render finishes"""
        print(f"[Queue] Render complete for job {cls.current_index + 1}/{len(cls.queue)}")
        cls.render_in_progress = False


# Global instance
render_queue = BatchRenderQueue()


def viewport_render_complete_handler(scene, depsgraph=None):
    """Handler for viewport render completion"""
    if render_queue.is_active and render_queue.render_type == 'VIEWPORT':
        render_queue.mark_render_complete()


def normal_render_complete_handler(scene, depsgraph=None):
    """Handler for normal render completion"""
    if render_queue.is_active and render_queue.render_type == 'NORMAL':
        render_queue.mark_render_complete()


def normal_render_cancel_handler(scene, depsgraph=None):
    """Handler for render cancellation"""
    if render_queue.is_active and render_queue.render_type == 'NORMAL':
        print(f"[Queue] Render cancelled")
        render_queue.mark_render_complete()


class CAMERA_OT_render_queue_controller(Operator):
    """Controller operator for batch rendering"""
    bl_idname = "camera.render_queue_controller"
    bl_label = "Render Queue Controller"
    
    render_type: bpy.props.StringProperty()
    
    _timer = None
    
    def execute(self, context):
        # Start modal operation
        wm = context.window_manager
        self._timer = wm.event_timer_add(0.5, window=context.window)
        wm.modal_handler_add(self)
        
        print(f"\n[Controller] Starting batch render controller")
        print(f"[Controller] Queue size: {len(render_queue.queue)}")
        print(f"[Controller] Render type: {self.render_type}")
        
        return {'RUNNING_MODAL'}
    
    def modal(self, context, event):
        if event.type != 'TIMER':
            return {'PASS_THROUGH'}
        
        # Check if queue is still active
        if not render_queue.is_active:
            print(f"[Controller] Queue deactivated, finishing")
            self.cleanup(context)
            return {'FINISHED'}
        
        # Check if a render is in progress
        if render_queue.render_in_progress:
            return {'RUNNING_MODAL'}
        
        # No render in progress - start next job
        render_queue.current_index += 1
        
        # Check if queue is complete
        if render_queue.current_index >= len(render_queue.queue):
            print(f"[Controller] All jobs complete!")
            self.cleanup(context)
            self.report({'INFO'}, f"Completed all {len(render_queue.queue)} render jobs")
            return {'FINISHED'}
        
        # Start next render job
        cam_obj, start, end = render_queue.queue[render_queue.current_index]
        
        print(f"\n[Controller] Starting job {render_queue.current_index + 1}/{len(render_queue.queue)}")
        print(f"  Camera: {cam_obj.name}")
        print(f"  Frames: {start}-{end}")
        print(f"  Format: {cam_obj.data.cameraide_settings.output_format}")
        
        # Store settings
        RenderCleanupManager.store_settings(context)
        
        # Apply camera settings
        context.scene.camera = cam_obj
        RenderCleanupManager.apply_camera_settings(
            context, cam_obj, 
            frame_range=(start, end), 
            force_image_format=False
        )
        
        # Mark render as in progress
        render_queue.render_in_progress = True
        
        # Start render based on type
        if self.render_type == 'VIEWPORT':
            print(f"[Controller] Invoking viewport render...")
            bpy.ops.render.opengl('INVOKE_DEFAULT', animation=True, 
                                sequencer=False, write_still=False, view_context=True)
        else:  # NORMAL
            print(f"[Controller] Invoking normal render...")
            bpy.ops.render.render('INVOKE_DEFAULT', animation=True)
        
        return {'RUNNING_MODAL'}
    
    def cleanup(self, context):
        """Cleanup after batch render"""
        if self._timer:
            context.window_manager.event_timer_remove(self._timer)
            self._timer = None
        
        # Restore settings
        RenderCleanupManager.restore_settings(context)
        
        # Remove handlers
        if viewport_render_complete_handler in bpy.app.handlers.render_post:
            bpy.app.handlers.render_post.remove(viewport_render_complete_handler)
        if normal_render_complete_handler in bpy.app.handlers.render_complete:
            bpy.app.handlers.render_complete.remove(normal_render_complete_handler)
        if normal_render_cancel_handler in bpy.app.handlers.render_cancel:
            bpy.app.handlers.render_cancel.remove(normal_render_cancel_handler)
        
        # Reset queue
        render_queue.reset()
        
        print(f"[Controller] Cleanup complete\n")
    
    def cancel(self, context):
        print(f"[Controller] Cancelled by user")
        self.cleanup(context)
        return {'CANCELLED'}


class CAMERA_OT_render_all_viewport(Operator):
    """Render all cameras with viewport render"""
    bl_idname = "camera.render_all_viewport"
    bl_label = "Render All Cameras (Viewport)"
    bl_description = "Render all cameras with viewport render"
    
    def execute(self, context):
        # Get all cameras with custom settings
        all_cameras = [
            obj for obj in context.scene.objects 
            if obj.type == 'CAMERA' and obj.data.cameraide_settings.use_custom_settings
        ]
        
        if not all_cameras:
            self.report({'WARNING'}, "No cameras with custom settings enabled")
            return {'CANCELLED'}
        
        # Build render queue
        queue = []
        for cam_obj in all_cameras:
            ranges = get_all_marker_ranges(cam_obj)
            for start, end in ranges:
                queue.append((cam_obj, start, end))
        
        if not queue:
            self.report({'WARNING'}, "No valid frame ranges found")
            return {'CANCELLED'}
        
        print(f"\n{'='*60}")
        print(f"[Batch Viewport] Queuing {len(queue)} jobs from {len(all_cameras)} cameras:")
        for i, (cam, start, end) in enumerate(queue, 1):
            print(f"  {i}. {cam.name}: frames {start}-{end}")
        print(f"{'='*60}\n")
        
        # Setup queue
        render_queue.start_queue(queue, 'VIEWPORT', self)
        
        # Add viewport render completion handler (render_post)
        if viewport_render_complete_handler not in bpy.app.handlers.render_post:
            bpy.app.handlers.render_post.append(viewport_render_complete_handler)
        
        # Start controller operator
        bpy.ops.camera.render_queue_controller('INVOKE_DEFAULT', render_type='VIEWPORT')
        
        self.report({'INFO'}, f"Started batch render: {len(queue)} jobs")
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
        # Get all cameras with custom settings
        all_cameras = [
            obj for obj in context.scene.objects 
            if obj.type == 'CAMERA' and obj.data.cameraide_settings.use_custom_settings
        ]
        
        if not all_cameras:
            self.report({'WARNING'}, "No cameras with custom settings found")
            return {'CANCELLED'}
        
        # Build render queue
        queue = []
        for cam_obj in all_cameras:
            ranges = get_all_marker_ranges(cam_obj)
            for start, end in ranges:
                queue.append((cam_obj, start, end))
        
        if not queue:
            self.report({'WARNING'}, "No valid frame ranges found")
            return {'CANCELLED'}
        
        print(f"\n{'='*60}")
        print(f"[Batch Normal] Queuing {len(queue)} jobs from {len(all_cameras)} cameras:")
        for i, (cam, start, end) in enumerate(queue, 1):
            print(f"  {i}. {cam.name}: frames {start}-{end}")
        print(f"{'='*60}\n")
        
        # Setup queue
        render_queue.start_queue(queue, 'NORMAL', self)
        
        # Add normal render completion handlers
        if normal_render_complete_handler not in bpy.app.handlers.render_complete:
            bpy.app.handlers.render_complete.append(normal_render_complete_handler)
        if normal_render_cancel_handler not in bpy.app.handlers.render_cancel:
            bpy.app.handlers.render_cancel.append(normal_render_cancel_handler)
        
        # Start controller operator
        bpy.ops.camera.render_queue_controller('INVOKE_DEFAULT', render_type='NORMAL')
        
        self.report({'INFO'}, f"Started batch render: {len(queue)} jobs")
        return {'FINISHED'}


def register():
    bpy.utils.register_class(CAMERA_OT_render_queue_controller)
    bpy.utils.register_class(CAMERA_OT_render_all_viewport)
    bpy.utils.register_class(CAMERA_OT_render_all_normal)


def unregister():
    # Clean up handlers
    if viewport_render_complete_handler in bpy.app.handlers.render_post:
        bpy.app.handlers.render_post.remove(viewport_render_complete_handler)
    if normal_render_complete_handler in bpy.app.handlers.render_complete:
        bpy.app.handlers.render_complete.remove(normal_render_complete_handler)
    if normal_render_cancel_handler in bpy.app.handlers.render_cancel:
        bpy.app.handlers.render_cancel.remove(normal_render_cancel_handler)
    
    # Reset queue
    render_queue.reset()
    
    bpy.utils.unregister_class(CAMERA_OT_render_all_normal)
    bpy.utils.unregister_class(CAMERA_OT_render_all_viewport)
    bpy.utils.unregister_class(CAMERA_OT_render_queue_controller)