"""Utilities package for Cameraide"""
from .callbacks import (
    update_viewport_resolution,
    update_frame_start,
    update_frame_end,
    on_active_camera_changed,
    on_befriend_toggle,
    on_sync_toggle,
    register,
    unregister
)

# Import utility modules
from . import marker_detection
from . import frame_manager
from . import camera_names
from . import render_manager

__all__ = [
    'update_viewport_resolution',
    'update_frame_start',
    'update_frame_end',
    'on_active_camera_changed',
    'on_befriend_toggle',
    'on_sync_toggle',
    'marker_detection',
    'frame_manager',
    'camera_names',
    'render_manager'
]
