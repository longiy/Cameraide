"""Batch render operators for Cameraide"""
import bpy
from bpy.types import Operator
from ..utils.render_manager import RenderCleanupManager
from ..utils.marker_detection import get_marker_frame_ranges
from ..utils.callbacks import on_active_camera_changed, apply_cameraide_to_native


def build_render_queue(context):
    """List of (camera, frame_start, frame_end) jobs for all Cameraide cameras.

    Range per camera: marker ranges in marker mode, the cameraide range when
    frame sync is ON, otherwise the current timeline range.
    """
    scene = context.scene
    timeline_range = (scene.frame_start, scene.frame_end)
    queue = []
    for obj in scene.objects:
        if obj.type != 'CAMERA' or not obj.data.cameraide_settings.use_custom_settings:
            continue
        settings = obj.data.cameraide_settings

        ranges = None
        if settings.frame_range_mode == 'TIMELINE_MARKERS':
            ranges = get_marker_frame_ranges(obj)
        if not ranges:
            if settings.frame_range_mode == 'PER_CAMERA' and settings.sync_frame_range:
                ranges = [(settings.frame_start, settings.frame_end)]
            else:
                ranges = [timeline_range]

        for start, end in ranges:
            queue.append((obj, start, end))
    return queue


def disable_camera_handler():
    """Suspend the active-camera handler so camera switches during the batch
    don't re-sync frame ranges or native settings mid-render."""
    if on_active_camera_changed in bpy.app.handlers.depsgraph_update_post:
        bpy.app.handlers.depsgraph_update_post.remove(on_active_camera_changed)


def restore_camera_handler():
    if on_active_camera_changed not in bpy.app.handlers.depsgraph_update_post:
        bpy.app.handlers.depsgraph_update_post.append(on_active_camera_changed)


class CAMERA_OT_render_all_viewport(Operator):
    """Render all cameras with viewport render"""
    bl_idname = "camera.render_all_viewport"
    bl_label = "Render All Cameras (Viewport)"
    bl_description = "Render every Cameraide camera with the viewport renderer, one after another"

    @classmethod
    def poll(cls, context):
        return any(
            obj.type == 'CAMERA' and obj.data.cameraide_settings.use_custom_settings
            for obj in context.scene.objects
        )

    def execute(self, context):
        queue = build_render_queue(context)
        if not queue:
            self.report({'WARNING'}, "No cameras with custom settings enabled")
            return {'CANCELLED'}

        # OpenGL renders never fire render_complete/render_write handlers,
        # so run the queue synchronously and restore in finally.
        RenderCleanupManager.store_settings(context)
        disable_camera_handler()
        completed = 0
        try:
            for cam_obj, start, end in queue:
                context.scene.camera = cam_obj
                RenderCleanupManager.apply_camera_settings(
                    context, cam_obj, frame_range=(start, end)
                )
                # view_context=False renders through scene.camera, so every
                # job uses its own camera regardless of the viewport view.
                result = bpy.ops.render.opengl(
                    animation=True, sequencer=False,
                    write_still=False, view_context=False
                )
                if 'CANCELLED' in result:
                    break
                completed += 1
        finally:
            RenderCleanupManager.restore_settings(context)
            restore_camera_handler()
            apply_cameraide_to_native(context.scene.camera, context.scene)

        self.report({'INFO'}, f"Batch viewport render: {completed}/{len(queue)} jobs done")
        return {'FINISHED'}


class NormalBatchRender:
    """Queue controller for normal (F12) batch renders.

    Normal renders fire render_complete/render_cancel, so jobs run via
    INVOKE_DEFAULT (render window, cancelable) and the handlers advance
    the queue.
    """

    def __init__(self):
        self.queue = []
        self.current_index = -1
        self.is_active = False

    def start(self, context):
        RenderCleanupManager.store_settings(context)
        disable_camera_handler()

        if normal_render_complete_handler not in bpy.app.handlers.render_complete:
            bpy.app.handlers.render_complete.append(normal_render_complete_handler)
        if normal_render_cancel_handler not in bpy.app.handlers.render_cancel:
            bpy.app.handlers.render_cancel.append(normal_render_cancel_handler)

        self.current_index = -1
        self.is_active = True
        bpy.app.timers.register(self.start_next_render, first_interval=0.5)

    def start_next_render(self):
        try:
            self.current_index += 1
            if self.current_index >= len(self.queue):
                self.cleanup()
                return None

            cam_obj, start, end = self.queue[self.current_index]
            context = bpy.context
            context.scene.camera = cam_obj
            RenderCleanupManager.apply_camera_settings(
                context, cam_obj, frame_range=(start, end)
            )

            # Timers run without a window in context; INVOKE_DEFAULT needs one.
            window = context.window_manager.windows[0]
            with context.temp_override(window=window, screen=window.screen):
                bpy.ops.render.render('INVOKE_DEFAULT', animation=True)

        except Exception:
            import traceback
            traceback.print_exc()
            self.cleanup()

        return None

    def on_render_complete(self):
        if self.current_index < len(self.queue) - 1:
            bpy.app.timers.register(self.start_next_render, first_interval=0.5)
        else:
            bpy.app.timers.register(self.cleanup, first_interval=0.5)

    def on_render_cancel(self):
        bpy.app.timers.register(self.cleanup, first_interval=0.5)

    def cleanup(self):
        self.is_active = False

        if normal_render_complete_handler in bpy.app.handlers.render_complete:
            bpy.app.handlers.render_complete.remove(normal_render_complete_handler)
        if normal_render_cancel_handler in bpy.app.handlers.render_cancel:
            bpy.app.handlers.render_cancel.remove(normal_render_cancel_handler)

        RenderCleanupManager.restore_settings(bpy.context)
        restore_camera_handler()
        scene = bpy.context.scene
        apply_cameraide_to_native(scene.camera, scene)

        return None


normal_batch = NormalBatchRender()


def normal_render_complete_handler(scene, depsgraph=None):
    if normal_batch.is_active:
        normal_batch.on_render_complete()


def normal_render_cancel_handler(scene, depsgraph=None):
    if normal_batch.is_active:
        normal_batch.on_render_cancel()


class CAMERA_OT_render_all_normal(Operator):
    """Render all cameras with normal render"""
    bl_idname = "camera.render_all_normal"
    bl_label = "Render All Cameras (Normal)"
    bl_description = "Render every Cameraide camera with the normal renderer, one after another"

    @classmethod
    def poll(cls, context):
        return any(
            obj.type == 'CAMERA' and obj.data.cameraide_settings.use_custom_settings
            for obj in context.scene.objects
        )

    def execute(self, context):
        if normal_batch.is_active:
            self.report({'WARNING'}, "Batch render already running")
            return {'CANCELLED'}

        normal_batch.queue = build_render_queue(context)
        if not normal_batch.queue:
            self.report({'WARNING'}, "No cameras with custom settings enabled")
            return {'CANCELLED'}

        normal_batch.start(context)
        self.report({'INFO'}, f"Started batch normal render: {len(normal_batch.queue)} jobs")
        return {'FINISHED'}


def register():
    bpy.utils.register_class(CAMERA_OT_render_all_viewport)
    bpy.utils.register_class(CAMERA_OT_render_all_normal)


def unregister():
    if normal_render_complete_handler in bpy.app.handlers.render_complete:
        bpy.app.handlers.render_complete.remove(normal_render_complete_handler)
    if normal_render_cancel_handler in bpy.app.handlers.render_cancel:
        bpy.app.handlers.render_cancel.remove(normal_render_cancel_handler)

    normal_batch.is_active = False
    restore_camera_handler()

    bpy.utils.unregister_class(CAMERA_OT_render_all_normal)
    bpy.utils.unregister_class(CAMERA_OT_render_all_viewport)
