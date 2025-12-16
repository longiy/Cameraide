"""Render completion handlers for Cameraide"""
import bpy
from ..utils.render_manager import RenderCleanupManager


def render_complete_handler(scene, depsgraph):
    """Handler for render completion"""
    RenderCleanupManager.restore_settings(bpy.context)
    remove_render_handlers()


def render_cancel_handler(scene, depsgraph):
    """Handler for render cancellation"""
    RenderCleanupManager.restore_settings(bpy.context)
    remove_render_handlers()


def add_render_handlers():
    """Add render completion handlers"""
    if render_complete_handler not in bpy.app.handlers.render_complete:
        bpy.app.handlers.render_complete.append(render_complete_handler)
    if render_cancel_handler not in bpy.app.handlers.render_cancel:
        bpy.app.handlers.render_cancel.append(render_cancel_handler)


def remove_render_handlers():
    """Remove render handlers"""
    if render_complete_handler in bpy.app.handlers.render_complete:
        bpy.app.handlers.render_complete.remove(render_complete_handler)
    if render_cancel_handler in bpy.app.handlers.render_cancel:
        bpy.app.handlers.render_cancel.remove(render_cancel_handler)
