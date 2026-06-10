"""Snapshot render operators for Cameraide"""
import bpy
from bpy.types import Operator
from ..utils.render_manager import RenderCleanupManager
from ..utils.callbacks import apply_cameraide_to_native
from ..render.handlers import add_render_handlers, remove_render_handlers

VIDEO_FORMATS = {'H264_MP4', 'H264_MKV', 'PRORES_MOV'}


def _get_target_camera(context):
    if (context.active_object and context.active_object.type == 'CAMERA'
            and context.active_object.data.cameraide_settings.use_custom_settings):
        return context.active_object
    return context.scene.camera


class CAMERA_OT_render_snapshot_viewport(Operator):
    """Render current frame using viewport renderer"""
    bl_idname = "camera.render_snapshot_viewport"
    bl_label = "Render Snapshot (Viewport)"
    bl_description = "Render current frame using viewport renderer"

    @classmethod
    def poll(cls, context):
        cam = context.scene.camera
        return cam is not None and cam.data.cameraide_settings.use_custom_settings

    def execute(self, context):
        cam_obj = _get_target_camera(context)
        settings = cam_obj.data.cameraide_settings

        if settings.output_format in VIDEO_FORMATS:
            self.report({'INFO'}, f"Camera set to {settings.output_format} - temporarily using PNG for snapshot")

        # OpenGL renders never fire render_complete/render_cancel handlers,
        # so render synchronously and always restore in finally.
        RenderCleanupManager.store_settings(context)
        try:
            context.scene.camera = cam_obj
            # Force image format (single frames can't be video); a snapshot
            # must not touch the scene frame range.
            RenderCleanupManager.apply_camera_settings(
                context, cam_obj,
                force_image_format=True, apply_frame_range=False
            )
            bpy.ops.render.opengl(animation=False, sequencer=False,
                                  write_still=True, view_context=True)
            return {'FINISHED'}
        except Exception as e:
            self.report({'ERROR'}, f"Render failed: {e}")
            return {'CANCELLED'}
        finally:
            RenderCleanupManager.restore_settings(context)
            apply_cameraide_to_native(context.scene.camera, context.scene)


class CAMERA_OT_render_snapshot_normal(Operator):
    """Render current frame using normal renderer"""
    bl_idname = "camera.render_snapshot_normal"
    bl_label = "Render Snapshot (Normal)"
    bl_description = "Render current frame using normal renderer"

    @classmethod
    def poll(cls, context):
        cam = context.scene.camera
        return cam is not None and cam.data.cameraide_settings.use_custom_settings

    def execute(self, context):
        cam_obj = _get_target_camera(context)
        settings = cam_obj.data.cameraide_settings

        if settings.output_format in VIDEO_FORMATS:
            self.report({'INFO'}, f"Camera set to {settings.output_format} - temporarily using PNG for snapshot")

        try:
            RenderCleanupManager.store_settings(context)
            # Normal renders fire render_complete/render_cancel — the
            # handlers restore settings when the render finishes.
            remove_render_handlers()
            add_render_handlers()

            context.scene.camera = cam_obj
            RenderCleanupManager.apply_camera_settings(
                context, cam_obj,
                force_image_format=True, apply_frame_range=False
            )

            bpy.ops.render.render('INVOKE_DEFAULT', animation=False, write_still=True)
            return {'FINISHED'}

        except Exception as e:
            self.report({'ERROR'}, f"Render failed: {e}")
            RenderCleanupManager.restore_settings(context)
            remove_render_handlers()
            return {'CANCELLED'}


def register():
    bpy.utils.register_class(CAMERA_OT_render_snapshot_viewport)
    bpy.utils.register_class(CAMERA_OT_render_snapshot_normal)


def unregister():
    bpy.utils.unregister_class(CAMERA_OT_render_snapshot_normal)
    bpy.utils.unregister_class(CAMERA_OT_render_snapshot_viewport)
