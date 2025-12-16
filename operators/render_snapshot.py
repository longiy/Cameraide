"""Snapshot render operators for Cameraide"""
import bpy
from bpy.types import Operator
from ..utils.render_manager import RenderCleanupManager
from ..render.handlers import add_render_handlers, remove_render_handlers


class CAMERA_OT_render_snapshot_viewport(Operator):
    """Render current frame using viewport renderer"""
    bl_idname = "camera.render_snapshot_viewport"
    bl_label = "Render Snapshot (Viewport)"
    bl_description = "Render current frame using viewport renderer"
    
    @classmethod
    def poll(cls, context):
        return context.active_object and context.active_object.type == 'CAMERA'
    
    def execute(self, context):
        cam_obj = context.active_object
        settings = cam_obj.data.cameraide_settings
        
        if not settings.use_custom_settings:
            self.report({'ERROR'}, "Custom settings are not enabled for this camera")
            return {'CANCELLED'}
        
        # Check if video format
        is_video = settings.output_format in {'H264_MP4', 'H264_MKV', 'PRORES_MOV'}
        if is_video:
            self.report({'INFO'}, f"Camera set to {settings.output_format} - temporarily using PNG for snapshot")
            
        try:
            RenderCleanupManager.store_settings(context)
            remove_render_handlers()
            add_render_handlers()
            
            context.scene.camera = cam_obj
            
            # Force image format for snapshots (can't render single frame as video)
            RenderCleanupManager.apply_camera_settings(context, cam_obj, force_image_format=True)
            
            for area in context.screen.areas:
                if area.type == 'VIEW_3D':
                    override = context.copy()
                    override['area'] = area
                    bpy.ops.render.opengl('INVOKE_DEFAULT', animation=False, 
                                         sequencer=False, write_still=True, view_context=True)
                    break
            
            return {'FINISHED'}
            
        except Exception as e:
            self.report({'ERROR'}, f"Render failed: {str(e)}")
            RenderCleanupManager.restore_settings(context)
            remove_render_handlers()
            return {'CANCELLED'}


class CAMERA_OT_render_snapshot_normal(Operator):
    """Render current frame using normal renderer"""
    bl_idname = "camera.render_snapshot_normal"
    bl_label = "Render Snapshot (Normal)"
    bl_description = "Render current frame using normal renderer"
    
    @classmethod
    def poll(cls, context):
        return context.active_object and context.active_object.type == 'CAMERA'
    
    def execute(self, context):
        cam_obj = context.active_object
        settings = cam_obj.data.cameraide_settings
        
        if not settings.use_custom_settings:
            self.report({'ERROR'}, "Custom settings are not enabled for this camera")
            return {'CANCELLED'}
        
        # Check if video format
        is_video = settings.output_format in {'H264_MP4', 'H264_MKV', 'PRORES_MOV'}
        if is_video:
            self.report({'INFO'}, f"Camera set to {settings.output_format} - temporarily using PNG for snapshot")
            
        try:
            RenderCleanupManager.store_settings(context)
            
            context.scene.camera = cam_obj
            
            # Force image format for snapshots (can't render single frame as video)
            RenderCleanupManager.apply_camera_settings(context, cam_obj, force_image_format=True)
            
            bpy.ops.render.render('INVOKE_DEFAULT', animation=False, write_still=True)
            
            return {'FINISHED'}
            
        except Exception as e:
            self.report({'ERROR'}, f"Render failed: {str(e)}")
            RenderCleanupManager.restore_settings(context)
            return {'CANCELLED'}


def register():
    bpy.utils.register_class(CAMERA_OT_render_snapshot_viewport)
    bpy.utils.register_class(CAMERA_OT_render_snapshot_normal)


def unregister():
    bpy.utils.unregister_class(CAMERA_OT_render_snapshot_normal)
    bpy.utils.unregister_class(CAMERA_OT_render_snapshot_viewport)