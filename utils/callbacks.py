"""Viewport and camera change callbacks for Cameraide"""
import bpy
from .frame_manager import frame_manager, prevent_recursive_update
from .camera_names import update_camera_name


def update_viewport_resolution(context):
    """Update viewport resolution"""
    if not context.scene.camera or not context.scene.camera.data.cameraide_settings.use_custom_settings:
        return
        
    settings = context.scene.camera.data.cameraide_settings
    context.scene.render.resolution_x = settings.resolution_x
    context.scene.render.resolution_y = settings.resolution_y
    context.scene.render.resolution_percentage = settings.resolution_percentage


def update_frame_start(self, context):
    """Frame start update callback"""
    if frame_manager.is_updating:
        return
        
    camera = context.scene.camera
    if not camera or camera.data.cameraide_settings != self:
        return
    
    # Only sync if in per-camera mode and sync is enabled
    if self.use_custom_settings and self.sync_frame_range and self.frame_range_mode == 'PER_CAMERA':
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
        
    # Only sync if in per-camera mode and sync is enabled
    if self.use_custom_settings and self.sync_frame_range and self.frame_range_mode == 'PER_CAMERA':
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
    
    # Only apply frame range if in per-camera mode with sync enabled
    if settings.use_custom_settings and settings.sync_frame_range and settings.frame_range_mode == 'PER_CAMERA':
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
            # On befriend - auto-detect frame mode
            from .marker_detection import auto_detect_frame_mode
            settings.frame_range_mode = auto_detect_frame_mode(camera_obj)
            
            stored = frame_manager.get_range(camera_obj)
            if stored:
                settings.frame_start = stored['start']
                settings.frame_end = stored['end']
                if settings.sync_frame_range and settings.frame_range_mode == 'PER_CAMERA' and camera_obj == scene.camera:
                    from .frame_manager import apply_frame_range_to_scene
                    apply_frame_range_to_scene(camera_obj, scene)
            
            update_camera_name(camera_obj, True)
        else:
            # On unfriend
            frame_manager.store_range(camera_obj)
            update_camera_name(camera_obj, False)
        
        frame_manager.store_range(camera_obj)


def on_sync_toggle(camera_obj):
    """Handle sync toggle"""
    if frame_manager.is_updating or not camera_obj:
        return
        
    scene = bpy.context.scene
    settings = camera_obj.data.cameraide_settings
    
    with prevent_recursive_update():
        if settings.sync_frame_range and settings.frame_range_mode == 'PER_CAMERA':
            # On sync enable (only in per-camera mode)
            stored = frame_manager.get_range(camera_obj)
            if stored and camera_obj == scene.camera:
                from .frame_manager import apply_frame_range_to_scene
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
