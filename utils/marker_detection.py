"""
Timeline marker detection and frame range calculation for Cameraide.
"""
import bpy

def get_camera_markers(camera_obj):
    """
    Get all timeline markers bound to a specific camera.
    Returns list of (marker, frame) tuples sorted by frame.
    """
    if not camera_obj or camera_obj.type != 'CAMERA':
        return []
    
    markers = []
    for marker in bpy.context.scene.timeline_markers:
        if marker.camera == camera_obj:
            markers.append((marker, marker.frame))
    
    return sorted(markers, key=lambda x: x[1])

def get_marker_frame_ranges(camera_obj):
    """
    Calculate frame ranges from timeline markers for a camera.
    Returns list of (start_frame, end_frame) tuples in timeline order.
    """
    markers = get_camera_markers(camera_obj)
    if not markers:
        return []
    
    ranges = []
    scene = bpy.context.scene
    
    for i, (marker, frame) in enumerate(markers):
        start = frame
        
        # End is either next marker or scene end
        if i < len(markers) - 1:
            end = markers[i + 1][1] - 1
        else:
            end = scene.frame_end
        
        ranges.append((start, end))
    
    return ranges

def has_timeline_markers(camera_obj):
    """Check if camera has any timeline markers"""
    return len(get_camera_markers(camera_obj)) > 0

def get_marker_count(camera_obj):
    """Get count of timeline markers for camera"""
    return len(get_camera_markers(camera_obj))

def auto_detect_frame_mode(camera_obj):
    """
    Auto-detect appropriate frame range mode for camera.
    Returns 'TIMELINE_MARKERS' or 'PER_CAMERA'
    """
    if has_timeline_markers(camera_obj):
        return 'TIMELINE_MARKERS'
    return 'PER_CAMERA'

def get_effective_frame_range(camera_obj):
    """
    Get the effective frame range based on current mode.
    Returns (start, end) tuple.
    """
    if not camera_obj or camera_obj.type != 'CAMERA':
        return (1, 250)
    
    settings = camera_obj.data.cameraide_settings
    
    if settings.frame_range_mode == 'TIMELINE_MARKERS':
        ranges = get_marker_frame_ranges(camera_obj)
        if ranges:
            # Return first marker range
            return ranges[0]
        # Fallback to custom if no markers found
        return (settings.frame_start, settings.frame_end)
    else:
        # PER_CAMERA mode
        return (settings.frame_start, settings.frame_end)

def get_all_marker_ranges(camera_obj):
    """
    Get all marker ranges for a camera (for batch rendering).
    Returns list of (start, end) tuples.
    """
    if not camera_obj or camera_obj.type != 'CAMERA':
        return []
    
    settings = camera_obj.data.cameraide_settings
    
    if settings.frame_range_mode == 'TIMELINE_MARKERS':
        ranges = get_marker_frame_ranges(camera_obj)
        if ranges:
            return ranges
    
    # Fallback to single custom range
    return [(settings.frame_start, settings.frame_end)]