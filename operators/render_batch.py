"""Batch render operators - RELIABLE VERSION"""
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
    
    def render_complete_handler(self, scene, depsgraph=None):
        """Called when viewport render completes"""
        print(f"[Viewport] Render complete for job {self.current_index + 1}/{len(self.queue)}")
        self.is_rendering = False
        
        if self.current_index < len(self.queue) - 1:
            bpy.app.timers.register(self.start_next_render, first_interval=0.5)
        else:
            print(f"[Viewport] All jobs complete!")
            bpy.app.timers.register(self.cleanup, first_interval=0.5)
    
    def start_next_render(self):
        """Start next render job - called by timer"""
        try:
            self.current_index += 1
            
            if self.current_index >= len(self.queue):
                self.cleanup()
                return None
            
            cam_obj, start, end = self.queue[self.current_index]
            
            print(f"\n[Viewport] Job {self.current_index + 1}/{len(self.queue)}")
            print(f"  Camera: {cam_obj.name}")
            print(f"  Frames: {start}-{end}")
            
            # Apply settings
            bpy.context.scene.camera = cam_obj
            RenderCleanupManager.apply_camera_settings(
                bpy.context, cam_obj,
                frame_range=(start, end),
                force_image_format=False
            )
            
            self.is_rendering = True
            
            # Start viewport render
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
        print(f"[Viewport] Cleaning up...")
        
        if self.render_complete_handler in bpy.app.handlers.render_post:
            bpy.app.handlers.render_post.remove(self.render_complete_handler)
        
        RenderCleanupManager.restore_settings(bpy.context)
        self.restore_cameraide_handler()
        
        return None
    
    def start(self, context):
        """Start batch rendering"""
        # Store original settings
        RenderCleanupManager.store_settings(context)
        
        # Disable Cameraide handler
        self.disable_cameraide_handler()
        
        # Clean existing handlers
        if self.render_complete_handler in bpy.app.handlers.render_post:
            bpy.app.handlers.render_post.remove(self.render_complete_handler)
        
        # Add handler
        bpy.app.handlers.render_post.append(self.render_complete_handler)
        
        # Reset state
        self.current_index = -1
        self.is_rendering = False
        
        # Start first render
        bpy.app.timers.register(self.start_next_render, first_interval=0.5)


class NormalBatchRender:
    """Normal batch render controller"""
    
    def __init__(self):
        self.queue = []
        self.current_index = -1
        self.is_rendering = False
        self.cameraide_handler = None
        
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
    
    def render_complete_handler(self, scene, depsgraph=None):
        """Called when render completes"""
        print(f"[Normal] Render complete for job {self.current_index + 1}/{len(self.queue)}")
        self.is_rendering = False
        
        if self.current_index < len(self.queue) - 1:
            bpy.app.timers.register(self.start_next_render, first_interval=0.5)
        else:
            print(f"[Normal] All jobs complete!")
            bpy.app.timers.register(self.cleanup, first_interval=0.5)
    
    def render_cancel_handler(self, scene, depsgraph=None):
        """Called if render cancelled"""
        print(f"[Normal] Render cancelled")
        bpy.app.timers.register(self.cleanup, first_interval=0.5)
    
    def start_next_render(self):
        """Start next render job - called by timer"""
        try:
            self.current_index += 1
            
            if self.current_index >= len(self.queue):
                self.cleanup()
                return None
            
            cam_obj, start, end = self.queue[self.current_index]
            
            print(f"\n[Normal] Job {self.current_index + 1}/{len(self.queue)}")
            print(f"  Camera: {cam_obj.name}")
            print(f"  Frames: {start}-{end}")
            
            # Apply settings
            bpy.context.scene.camera = cam_obj
            RenderCleanupManager.apply_camera_settings(
                bpy.context, cam_obj,
                frame_range=(start, end),
                force_image_format=False
            )
            
            self.is_rendering = True
            
            # Start normal render
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
        
        if self.render_complete_handler in bpy.app.handlers.render_complete:
            bpy.app.handlers.render_complete.remove(self.render_complete_handler)
        if self.render_cancel_handler in bpy.app.handlers.render_cancel:
            bpy.app.handlers.render_cancel.remove(self.render_cancel_handler)
        
        RenderCleanupManager.restore_settings(bpy.context)
        self.restore_cameraide_handler()
        
        return None
    
    def start(self, context):
        """Start batch rendering"""
        # Store original settings
        RenderCleanupManager.store_settings(context)
        
        # Disable Cameraide handler
        self.disable_cameraide_handler()
        
        # Clean existing handlers
        if self.render_complete_handler in bpy.app.handlers.render_complete:
            bpy.app.handlers.render_complete.remove(self.render_complete_handler)
        if self.render_cancel_handler in bpy.app.handlers.render_cancel:
            bpy.app.handlers.render_cancel.remove(self.render_cancel_handler)
        
        # Add handlers
        bpy.app.handlers.render_complete.append(self.render_complete_handler)
        bpy.app.handlers.render_cancel.append(self.render_cancel_handler)
        
        # Reset state
        self.current_index = -1
        self.is_rendering = False
        
        # Start first render
        bpy.app.timers.register(self.start_next_render, first_interval=0.5)


# Global instances
viewport_batch = ViewportBatchRender()
normal_batch = NormalBatchRender()


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
    # Cleanup any active renders
    if viewport_batch.render_complete_handler in bpy.app.handlers.render_post:
        bpy.app.handlers.render_post.remove(viewport_batch.render_complete_handler)
    if normal_batch.render_complete_handler in bpy.app.handlers.render_complete:
        bpy.app.handlers.render_complete.remove(normal_batch.render_complete_handler)
    if normal_batch.render_cancel_handler in bpy.app.handlers.render_cancel:
        bpy.app.handlers.render_cancel.remove(normal_batch.render_cancel_handler)
    
    viewport_batch.restore_cameraide_handler()
    normal_batch.restore_cameraide_handler()
    
    bpy.utils.unregister_class(CAMERA_OT_render_all_normal)
    bpy.utils.unregister_class(CAMERA_OT_render_all_viewport)