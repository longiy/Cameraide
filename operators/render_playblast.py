"""Playblast (animation) render operators for Cameraide"""
import bpy
from bpy.types import Operator
from ..utils.render_manager import RenderCleanupManager
from ..utils.callbacks import apply_cameraide_to_native
from ..render.handlers import add_render_handlers, remove_render_handlers


def _get_target_camera(context):
    if (context.active_object and context.active_object.type == 'CAMERA'
            and context.active_object.data.cameraide_settings.use_custom_settings):
        return context.active_object
    return context.scene.camera


class CAMERA_OT_render_selected_viewport(Operator):
    """Render animation using viewport renderer"""
    bl_idname = "camera.render_selected_viewport"
    bl_label = "Render Viewport"
    bl_description = "Render animation using viewport renderer"

    @classmethod
    def poll(cls, context):
        cam = context.scene.camera
        return cam is not None and cam.data.cameraide_settings.use_custom_settings

    def execute(self, context):
        cam_obj = _get_target_camera(context)

        # OpenGL renders never fire render_complete/render_cancel handlers,
        # so render synchronously and always restore in finally — otherwise
        # the scene frame range and render settings stay modified.
        RenderCleanupManager.store_settings(context)
        try:
            context.scene.camera = cam_obj
            RenderCleanupManager.apply_camera_settings(context, cam_obj)
            bpy.ops.render.opengl(animation=True, sequencer=False,
                                  write_still=False, view_context=True)
            return {'FINISHED'}
        except Exception as e:
            self.report({'ERROR'}, f"Render failed: {e}")
            return {'CANCELLED'}
        finally:
            RenderCleanupManager.restore_settings(context)
            apply_cameraide_to_native(context.scene.camera, context.scene)


class CAMERA_OT_render_selected_normal(Operator):
    """Render animation using normal renderer"""
    bl_idname = "camera.render_selected_normal"
    bl_label = "Render Normal"
    bl_description = "Render selected camera with normal render"

    @classmethod
    def poll(cls, context):
        cam = context.scene.camera
        return cam is not None and cam.data.cameraide_settings.use_custom_settings

    def execute(self, context):
        cam_obj = _get_target_camera(context)

        try:
            RenderCleanupManager.store_settings(context)
            # Normal renders do fire render_complete/render_cancel — the
            # handlers restore settings when the render window finishes.
            remove_render_handlers()
            add_render_handlers()

            context.scene.camera = cam_obj
            RenderCleanupManager.apply_camera_settings(context, cam_obj)

            bpy.ops.render.render('INVOKE_DEFAULT', animation=True)
            return {'FINISHED'}

        except Exception as e:
            self.report({'ERROR'}, f"Render failed: {e}")
            RenderCleanupManager.restore_settings(context)
            remove_render_handlers()
            return {'CANCELLED'}


def register():
    bpy.utils.register_class(CAMERA_OT_render_selected_viewport)
    bpy.utils.register_class(CAMERA_OT_render_selected_normal)


def unregister():
    bpy.utils.unregister_class(CAMERA_OT_render_selected_normal)
    bpy.utils.unregister_class(CAMERA_OT_render_selected_viewport)
