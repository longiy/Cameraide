"""Camera naming utilities for Cameraide"""

HEART_PREFIX = "❤️ "


def get_clean_camera_name(camera_obj):
    """Get camera name without heart emoji prefix"""
    if not camera_obj:
        return ""
    current_name = camera_obj.name
    if current_name.startswith(HEART_PREFIX):
        return current_name[len(HEART_PREFIX):]
    return current_name


def update_camera_name(camera_obj, add_heart=True):
    """Update camera name to add or remove heart emoji prefix"""
    if not camera_obj:
        return
        
    current_name = camera_obj.name
    clean_name = get_clean_camera_name(camera_obj)
    
    new_name = HEART_PREFIX + clean_name if add_heart else clean_name
        
    if new_name != current_name:
        camera_obj.name = new_name
