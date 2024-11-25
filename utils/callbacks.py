import bpy
from contextlib import contextmanager

class CameraFrameRanges:
    ranges = {}  # Store frame ranges by camera name
    is_updating = False
    previous_camera = None

    @classmethod
    def store_range(cls, camera_obj):
        """Store a camera's frame range"""
        if not camera_obj or camera_obj.type != 'CAMERA':
            return
            
        settings = camera_obj.data.cameraide_settings
        cls.ranges[camera_obj.name] = {
            'start': settings.frame_start,
            'end': settings.frame_end,
            'befriended': settings.use_custom_settings,
            'synced': settings.sync_frame_range
        }

    @classmethod
    def get_range(cls, camera_obj):
        """Get a camera's stored range"""
        if not camera_obj or camera_obj.name not in cls.ranges:
            return None
        return cls.ranges[camera_obj.name]
    
    @classmethod
    def clear(cls):
        """Clear stored ranges"""
        cls.ranges.clear()
        cls.previous_camera = None
        cls.is_updating = False

frame_manager = CameraFrameRanges()

@contextmanager
def prevent_recursive_update():
    """Context manager to prevent recursive updates"""
    if frame_manager.is_updating:
        yield
        return
    
    frame_manager.is_updating = True
    try:
        yield
    finally:
        frame_manager.is_updating = False

def update_viewport_resolution(context):
    """Update viewport resolution"""
    if not context.scene.camera or not context.scene.camera.data.cameraide_settings.use_custom_settings:
        return
        
    settings = context.scene.camera.data.cameraide_settings
    context.scene.render.resolution_x = settings.resolution_x
    context.scene.render.resolution_y = settings.resolution_y
    context.scene.render.resolution_percentage = settings.resolution_percentage

def apply_frame_range_to_scene(camera_obj, scene):
    """Apply camera frame range to scene"""
    if not camera_obj or camera_obj.type != 'CAMERA':
        return
        
    settings = camera_obj.data.cameraide_settings
    with prevent_recursive_update():
        scene.frame_start = settings.frame_start
        scene.frame_end = settings.frame_end

def store_scene_range_to_camera(camera_obj, scene):
    """Store scene frame range in camera"""
    if not camera_obj or camera_obj.type != 'CAMERA':
        return
        
    settings = camera_obj.data.cameraide_settings
    with prevent_recursive_update():
        settings.frame_start = scene.frame_start
        settings.frame_end = scene.frame_end
    frame_manager.store_range(camera_obj)

def update_frame_start(self, context):
    """Frame start update callback"""
    if frame_manager.is_updating:
        return
        
    camera = context.scene.camera
    if not camera or camera.data.cameraide_settings != self:
        return
        
    if self.use_custom_settings and self.sync_frame_range:
        with prevent_recursive_update():
            context.scene.frame_start = self.frame_start
            frame_manager.store_range(camera)

def update_frame_end(self, context):
    """Frame end update callback"""
    if frame_manager.is_updating:
        return
        
    camera = context.scene.camera
    if not camera or camera.data.cameraide_settings != self:
        return
        
    if self.use_custom_settings and self.sync_frame_range:
        with prevent_recursive_update():
            context.scene.frame_end = self.frame_end
            frame_manager.store_range(camera)

@bpy.app.handlers.persistent
def on_active_camera_changed(scene):
    """Handle camera switching"""
    if frame_manager.is_updating:
        return

    current_camera = scene.camera
    if not current_camera or current_camera.type != 'CAMERA':
        return
        
    settings = current_camera.data.cameraide_settings
    if settings.use_custom_settings and settings.sync_frame_range:
        with prevent_recursive_update():
            scene.frame_start = settings.frame_start
            scene.frame_end = settings.frame_end
            frame_manager.store_range(current_camera)
    
    frame_manager.previous_camera = current_camera
    update_viewport_resolution(bpy.context)



def on_befriend_toggle(camera_obj):
    """Handle befriend toggle"""
    if frame_manager.is_updating or not camera_obj:
        return

    scene = bpy.context.scene
    settings = camera_obj.data.cameraide_settings
    
    with prevent_recursive_update():
        if settings.use_custom_settings:
            # On befriend
            stored = frame_manager.get_range(camera_obj)
            if stored:
                settings.frame_start = stored['start']
                settings.frame_end = stored['end']
                if settings.sync_frame_range and camera_obj == scene.camera:
                    apply_frame_range_to_scene(camera_obj, scene)
        else:
            # On unfriend
            frame_manager.store_range(camera_obj)
        
        frame_manager.store_range(camera_obj)

def on_sync_toggle(camera_obj):
    """Handle sync toggle"""
    if frame_manager.is_updating or not camera_obj:
        return
        
    scene = bpy.context.scene
    settings = camera_obj.data.cameraide_settings
    
    with prevent_recursive_update():
        if settings.sync_frame_range:
            # On sync enable
            stored = frame_manager.get_range(camera_obj)
            if stored and camera_obj == scene.camera:
                apply_frame_range_to_scene(camera_obj, scene)
        else:
            # On sync disable
            frame_manager.store_range(camera_obj)
def register():
    frame_manager.clear()
    if on_active_camera_changed not in bpy.app.handlers.depsgraph_update_post:
        bpy.app.handlers.depsgraph_update_post.append(on_active_camera_changed)

def unregister():
    frame_manager.clear()
    if on_active_camera_changed in bpy.app.handlers.depsgraph_update_post:
        bpy.app.handlers.depsgraph_update_post.remove(on_active_camera_changed)
__all__ = [
    'update_viewport_resolution',
    'update_frame_start',
    'update_frame_end',
    'on_active_camera_changed',
    'on_befriend_toggle',
    'on_sync_toggle'
]