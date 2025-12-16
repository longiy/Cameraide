"""Frame range manager for Cameraide"""
from contextlib import contextmanager


class CameraFrameRanges:
    """Manages frame ranges for cameras"""
    ranges = {}
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
            'synced': settings.sync_frame_range,
            'mode': settings.frame_range_mode
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


# Global instance
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


def apply_frame_range_to_scene(camera_obj, scene):
    """Apply camera frame range to scene (only in PER_CAMERA mode)"""
    if not camera_obj or camera_obj.type != 'CAMERA':
        return
        
    settings = camera_obj.data.cameraide_settings
    
    # Only apply if in per-camera mode
    if settings.frame_range_mode == 'PER_CAMERA':
        with prevent_recursive_update():
            scene.frame_start = settings.frame_start
            scene.frame_end = settings.frame_end


def store_scene_range_to_camera(camera_obj, scene):
    """Store scene frame range in camera (only in PER_CAMERA mode)"""
    if not camera_obj or camera_obj.type != 'CAMERA':
        return
        
    settings = camera_obj.data.cameraide_settings
    
    # Only store if in per-camera mode
    if settings.frame_range_mode == 'PER_CAMERA':
        with prevent_recursive_update():
            settings.frame_start = scene.frame_start
            settings.frame_end = scene.frame_end
        frame_manager.store_range(camera_obj)
