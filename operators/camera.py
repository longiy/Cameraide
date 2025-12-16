"""Camera-related operators for Cameraide addon"""
import bpy
from bpy.types import Operator
from ..utils.callbacks import update_viewport_resolution, on_befriend_toggle, on_sync_toggle


class CAMERA_OT_toggle_custom_settings(Operator):
    """Toggle custom camera settings (befriend/unfriend)"""
    bl_idname = "camera.toggle_custom_settings"
    bl_label = "FRIENDSHIP"
    bl_description = "Toggle custom camera settings"

    def execute(self, context):
        if context.active_object and context.active_object.type == 'CAMERA':
            cam = context.active_object
        elif context.scene.camera:
            cam = context.scene.camera
        else:
            self.report({'ERROR'}, "No active camera found")
            return {'CANCELLED'}

        settings = cam.data.cameraide_settings
        settings.use_custom_settings = not settings.use_custom_settings

        # Clear render flags
        for handler in bpy.app.handlers.frame_change_post:
            if hasattr(handler, 'has_rendered'):
                handler.has_rendered = False
            if hasattr(handler, 'current_camera') and handler.current_camera == cam:
                handler.current_camera = None
                handler.last_frame = -1
        
        on_befriend_toggle(cam)
        
        return {'FINISHED'}


class CAMERA_OT_toggle_frame_range_sync(Operator):
    """Toggle frame range sync with viewport timeline"""
    bl_idname = "camera.toggle_frame_range_sync"
    bl_label = "Toggle Frame Range Sync"
    bl_description = "Toggle synchronization of viewport timeline with camera's frame range"

    def execute(self, context):
        if context.active_object and context.active_object.type == 'CAMERA':
            cam = context.active_object
        elif context.scene.camera:
            cam = context.scene.camera
        else:
            self.report({'ERROR'}, "No active camera found")
            return {'CANCELLED'}

        settings = cam.data.cameraide_settings
        settings.sync_frame_range = not settings.sync_frame_range
        
        on_sync_toggle(cam)
        update_viewport_resolution(context)
        
        return {'FINISHED'}


class CAMERAIDE_OT_switch_to_timeline_mode(Operator):
    """Switch to Timeline Markers mode"""
    bl_idname = "cameraide.switch_to_timeline_mode"
    bl_label = "Switch to Timeline Mode"
    bl_options = {'REGISTER', 'UNDO'}
    
    camera_name: bpy.props.StringProperty()
    
    def execute(self, context):
        camera_obj = context.scene.objects.get(self.camera_name)
        if camera_obj and camera_obj.type == 'CAMERA':
            camera_obj.data.cameraide_settings.frame_range_mode = 'TIMELINE_MARKERS'
        return {'FINISHED'}


class CAMERAIDE_OT_switch_to_percamera_mode(Operator):
    """Switch to Per-Camera Ranges mode"""
    bl_idname = "cameraide.switch_to_percamera_mode"
    bl_label = "Switch to Per-Camera Mode"
    bl_options = {'REGISTER', 'UNDO'}
    
    camera_name: bpy.props.StringProperty()
    
    def execute(self, context):
        camera_obj = context.scene.objects.get(self.camera_name)
        if camera_obj and camera_obj.type == 'CAMERA':
            camera_obj.data.cameraide_settings.frame_range_mode = 'PER_CAMERA'
        return {'FINISHED'}


def register():
    bpy.utils.register_class(CAMERA_OT_toggle_custom_settings)
    bpy.utils.register_class(CAMERA_OT_toggle_frame_range_sync)
    bpy.utils.register_class(CAMERAIDE_OT_switch_to_timeline_mode)
    bpy.utils.register_class(CAMERAIDE_OT_switch_to_percamera_mode)


def unregister():
    bpy.utils.unregister_class(CAMERAIDE_OT_switch_to_percamera_mode)
    bpy.utils.unregister_class(CAMERAIDE_OT_switch_to_timeline_mode)
    bpy.utils.unregister_class(CAMERA_OT_toggle_frame_range_sync)
    bpy.utils.unregister_class(CAMERA_OT_toggle_custom_settings)
