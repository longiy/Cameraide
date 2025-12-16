"""Playblast (animation) render operators for Cameraide"""
import bpy
from bpy.types import Operator
from ..utils.render_manager import RenderCleanupManager
from ..render.handlers import add_render_handlers, remove_render_handlers


class CAMERA_OT_render_selected_viewport(Operator):
    """Render animation using viewport renderer"""
    bl_idname = "camera.render_selected_viewport"
    bl_label = "Render Viewport"
    bl_description = "Render animation using viewport renderer"
    
    @classmethod
    def poll(cls, context):
        return context.active_object and context.active_object.type == 'CAMERA'
    
    def execute(self, context):
        cam_obj = context.active_object
        settings = cam_obj.data.cameraide_settings
        
        if not settings.use_custom_settings:
            self.report({'ERROR'}, "Custom settings are not enabled for this camera")
            return {'CANCELLED'}
            
        try:
            RenderCleanupManager.store_settings(context)
            remove_render_handlers()
            add_render_handlers()
            
            context.scene.camera = cam_obj
            
            # Don't force image format - animations can use video formats
            RenderCleanupManager.apply_camera_settings(context, cam_obj, force_image_format=False)
            
            for area in context.screen.areas:
                if area.type == 'VIEW_3D':
                    override = context.copy()
                    override['area'] = area
                    bpy.ops.render.opengl('INVOKE_DEFAULT', animation=True, 
                                         sequencer=False, write_still=False, view_context=True)
                    break
            
            return {'FINISHED'}
            
        except Exception as e:
            self.report({'ERROR'}, f"Render failed: {str(e)}")
            RenderCleanupManager.restore_settings(context)
            remove_render_handlers()
            return {'CANCELLED'}


class CAMERA_OT_render_selected_normal(Operator):
    """Render animation using normal renderer"""
    bl_idname = "camera.render_selected_normal"
    bl_label = "Render Normal"
    bl_description = "Render selected camera with normal render"
    
    @classmethod
    def poll(cls, context):
        return context.active_object and context.active_object.type == 'CAMERA'
    
    def execute(self, context):
        cam_obj = context.active_object
        settings = cam_obj.data.cameraide_settings
        
        if not settings.use_custom_settings:
            self.report({'ERROR'}, "Custom settings are not enabled for this camera")
            return {'CANCELLED'}
            
        try:
            RenderCleanupManager.store_settings(context)
            context.scene.camera = cam_obj
            
            # Don't force image format - animations can use video formats
            RenderCleanupManager.apply_camera_settings(context, cam_obj, force_image_format=False)
            
            bpy.ops.render.render('INVOKE_DEFAULT', animation=True)
            return {'FINISHED'}
            
        except Exception as e:
            self.report({'ERROR'}, f"Render failed: {str(e)}")
            RenderCleanupManager.restore_settings(context)
            return {'CANCELLED'}


def register():
    bpy.utils.register_class(CAMERA_OT_render_selected_viewport)
    bpy.utils.register_class(CAMERA_OT_render_selected_normal)


def unregister():
    bpy.utils.unregister_class(CAMERA_OT_render_selected_normal)
    bpy.utils.unregister_class(CAMERA_OT_render_selected_viewport)