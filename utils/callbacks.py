"""Viewport and camera change callbacks for Cameraide"""
import bpy
from .frame_manager import frame_manager, prevent_recursive_update
from .camera_names import update_camera_name

# Guards against feedback loops
_syncing_native = False

# Tracks what cameraide last wrote to Blender's native render panel, per camera name.
# The handler only syncs native → cameraide when native DIVERGES from this snapshot,
# meaning the user actually touched the native panel (not the cameraide panel).
_native_snapshot = {}


# ---------------------------------------------------------------------------
# Native ↔ Cameraide helpers
# ---------------------------------------------------------------------------

def _get_native_state(scene):
    """Read a comparable snapshot of current native render settings."""
    render = scene.render
    img = render.image_settings
    state = {
        'file_format': img.file_format,
        'film_transparent': render.film_transparent,
        'resolution_x': render.resolution_x,
        'resolution_y': render.resolution_y,
        'resolution_percentage': render.resolution_percentage,
    }
    if img.file_format in {'PNG', 'OPEN_EXR'}:
        state['color_depth'] = getattr(img, 'color_depth', None)
    if img.file_format == 'PNG':
        state['compression'] = getattr(img, 'compression', None)
    if img.file_format == 'JPEG':
        state['quality'] = getattr(img, 'quality', None)
    if img.file_format == 'OPEN_EXR':
        state['exr_codec'] = getattr(img, 'exr_codec', None)
    if img.file_format == 'FFMPEG':
        ffmpeg = render.ffmpeg
        state['ffmpeg_format'] = ffmpeg.format
        state['ffmpeg_codec'] = ffmpeg.codec
        state['video_bitrate'] = ffmpeg.video_bitrate
        state['audio_codec'] = ffmpeg.audio_codec
        state['audio_bitrate'] = ffmpeg.audio_bitrate
        state['gopsize'] = ffmpeg.gopsize
        state['constant_rate_factor'] = getattr(ffmpeg, 'constant_rate_factor', None)
    return state


def apply_cameraide_to_native(cam, scene):
    """Push active cameraide camera settings into Blender's native render panel.
    Call this whenever the active cameraide camera changes so the native panel
    reflects its per-camera settings.  Records a snapshot so the handler can
    tell when the USER subsequently edits native (vs. cameraide editing it).
    """
    global _syncing_native
    if _syncing_native:
        return
    if not cam or not cam.data.cameraide_settings.use_custom_settings:
        return

    settings = cam.data.cameraide_settings
    _syncing_native = True
    try:
        render = scene.render
        img = render.image_settings
        fmt = settings.output_format

        render.resolution_x = settings.resolution_x
        render.resolution_y = settings.resolution_y
        render.resolution_percentage = settings.resolution_percentage

        if fmt == 'PNG':
            img.media_type = 'IMAGE'
            img.file_format = 'PNG'
            img.color_mode = 'RGBA'
            img.color_depth = settings.png_color_depth
            img.compression = settings.png_compression
            render.film_transparent = settings.png_film_transparent

        elif fmt == 'JPEG':
            img.media_type = 'IMAGE'
            img.file_format = 'JPEG'
            img.color_mode = 'RGB'
            img.quality = settings.jpeg_quality
            render.film_transparent = False

        elif fmt == 'OPEN_EXR':
            img.media_type = 'IMAGE'
            img.file_format = 'OPEN_EXR'
            img.color_mode = 'RGBA'
            img.color_depth = settings.exr_color_depth
            img.exr_codec = settings.exr_codec
            render.film_transparent = settings.exr_film_transparent

        elif fmt in {'H264_MP4', 'H264_MKV', 'PRORES_MOV'}:
            img.media_type = 'VIDEO'
            img.file_format = 'FFMPEG'
            ffmpeg = render.ffmpeg
            if fmt == 'H264_MP4':
                ffmpeg.format = 'MPEG4'
                ffmpeg.codec = 'H264'
                if hasattr(ffmpeg, 'constant_rate_factor'):
                    ffmpeg.constant_rate_factor = settings.video_quality
                ffmpeg.video_bitrate = settings.video_bitrate
                ffmpeg.gopsize = settings.video_gopsize
                render.film_transparent = False
            elif fmt == 'H264_MKV':
                ffmpeg.format = 'MKV'
                ffmpeg.codec = 'H264'
                if hasattr(ffmpeg, 'constant_rate_factor'):
                    ffmpeg.constant_rate_factor = settings.video_quality
                ffmpeg.video_bitrate = settings.video_bitrate
                ffmpeg.gopsize = settings.video_gopsize
                render.film_transparent = False
            elif fmt == 'PRORES_MOV':
                ffmpeg.format = 'QUICKTIME'
                ffmpeg.codec = 'PRORES'
                if hasattr(ffmpeg, 'constant_rate_factor'):
                    ffmpeg.constant_rate_factor = 'PERC_LOSSLESS'
                ffmpeg.gopsize = 1
                render.film_transparent = settings.prores_film_transparent

            if settings.use_audio and settings.audio_codec != 'NONE':
                ffmpeg.audio_codec = settings.audio_codec
                ffmpeg.audio_bitrate = settings.audio_bitrate
            else:
                ffmpeg.audio_codec = 'NONE'

        _native_snapshot[cam.name] = _get_native_state(scene)
    finally:
        _syncing_native = False


def _sync_native_to_cameraide(cam, scene):
    """Copy current native settings into the cameraide camera's properties."""
    settings = cam.data.cameraide_settings
    render = scene.render
    img = render.image_settings
    fmt = img.file_format

    settings.resolution_x = render.resolution_x
    settings.resolution_y = render.resolution_y
    settings.resolution_percentage = render.resolution_percentage

    if fmt == 'PNG':
        settings.output_format = 'PNG'
        settings.png_color_depth = getattr(img, 'color_depth', '8')
        settings.png_compression = getattr(img, 'compression', 15)
        settings.png_film_transparent = render.film_transparent

    elif fmt == 'JPEG':
        settings.output_format = 'JPEG'
        settings.jpeg_quality = getattr(img, 'quality', 90)

    elif fmt == 'OPEN_EXR':
        settings.output_format = 'OPEN_EXR'
        settings.exr_color_depth = getattr(img, 'color_depth', '16')
        settings.exr_codec = getattr(img, 'exr_codec', 'ZIP')
        settings.exr_film_transparent = render.film_transparent

    elif fmt == 'FFMPEG':
        ffmpeg = render.ffmpeg
        if ffmpeg.format == 'MPEG4' and ffmpeg.codec == 'H264':
            settings.output_format = 'H264_MP4'
        elif ffmpeg.format == 'MKV' and ffmpeg.codec == 'H264':
            settings.output_format = 'H264_MKV'
        elif ffmpeg.format == 'QUICKTIME':
            settings.output_format = 'PRORES_MOV'
            settings.prores_film_transparent = render.film_transparent

        if settings.output_format in {'H264_MP4', 'H264_MKV'}:
            if hasattr(ffmpeg, 'constant_rate_factor'):
                try:
                    settings.video_quality = ffmpeg.constant_rate_factor
                except Exception:
                    pass
            settings.video_bitrate = ffmpeg.video_bitrate
            settings.video_gopsize = ffmpeg.gopsize

        if ffmpeg.audio_codec != 'NONE':
            settings.use_audio = True
            try:
                settings.audio_codec = ffmpeg.audio_codec
            except Exception:
                pass
            settings.audio_bitrate = ffmpeg.audio_bitrate
        else:
            settings.use_audio = False


# ---------------------------------------------------------------------------
# Resolution live-update (existing)
# ---------------------------------------------------------------------------

def update_viewport_resolution(context):
    """Update viewport resolution"""
    if not context.scene.camera or not context.scene.camera.data.cameraide_settings.use_custom_settings:
        return

    settings = context.scene.camera.data.cameraide_settings
    context.scene.render.resolution_x = settings.resolution_x
    context.scene.render.resolution_y = settings.resolution_y
    context.scene.render.resolution_percentage = settings.resolution_percentage


# ---------------------------------------------------------------------------
# Frame range update callbacks (properties.py hooks)
# ---------------------------------------------------------------------------

def update_frame_start(self, context):
    """Frame start update callback"""
    if frame_manager.is_updating:
        return

    camera = context.scene.camera
    if not camera or camera.data.cameraide_settings != self:
        return

    if self.use_custom_settings and self.sync_frame_range and self.frame_range_mode == 'PER_CAMERA':
        with prevent_recursive_update():
            context.scene.frame_start = self.frame_start
            frame_manager.store_range(camera)


def update_frame_end(self, context):
    """Frame end update callback"""
    if frame_manager.is_updating:
        return

    camera = context.scene.camera
    if not camera or camera.data.cameraide_settings != self:
        return

    if self.use_custom_settings and self.sync_frame_range and self.frame_range_mode == 'PER_CAMERA':
        with prevent_recursive_update():
            context.scene.frame_end = self.frame_end
            frame_manager.store_range(camera)


# ---------------------------------------------------------------------------
# Persistent handlers
# ---------------------------------------------------------------------------

@bpy.app.handlers.persistent
def on_active_camera_changed(scene):
    """Handle camera switching — apply frame range sync and push cameraide
    settings into the native Blender render panel."""
    if frame_manager.is_updating:
        return

    current_camera = scene.camera
    if not current_camera or current_camera.type != 'CAMERA':
        return

    settings = current_camera.data.cameraide_settings

    if settings.use_custom_settings and settings.sync_frame_range and settings.frame_range_mode == 'PER_CAMERA':
        with prevent_recursive_update():
            scene.frame_start = settings.frame_start
            scene.frame_end = settings.frame_end
            frame_manager.store_range(current_camera)

    frame_manager.previous_camera = current_camera
    update_viewport_resolution(bpy.context)

    # Push this camera's settings into the native panel and record the snapshot
    apply_cameraide_to_native(current_camera, scene)


@bpy.app.handlers.persistent
def on_native_render_settings_changed(scene):
    """Sync native Blender render panel → active cameraide camera, but ONLY
    when native actually diverged from what cameraide last wrote there.

    This means:
    - Cameraide panel edits: native stays == snapshot → no sync, cameraide wins.
    - Native panel edits:    native != snapshot       → sync to cameraide + refresh snapshot.
    """
    global _syncing_native
    if _syncing_native or frame_manager.is_updating:
        return

    from .render_manager import RenderCleanupManager
    if RenderCleanupManager._original_settings is not None:
        return  # Mid-render; cameraide is controlling native — don't read back

    cam = scene.camera
    if not cam or not cam.data.cameraide_settings.use_custom_settings:
        return

    snapshot = _native_snapshot.get(cam.name)
    if snapshot is None:
        # We haven't established a baseline for this camera yet; do it now
        apply_cameraide_to_native(cam, scene)
        return

    current = _get_native_state(scene)
    if current == snapshot:
        return  # Nothing changed in native

    # Native diverged — user edited the native panel; propagate to cameraide
    _syncing_native = True
    try:
        _sync_native_to_cameraide(cam, scene)
        # After syncing, push cameraide back to native so snapshot is fresh
        # (needed because _sync writes to settings, not to native)
        _native_snapshot[cam.name] = current
    finally:
        _syncing_native = False


# ---------------------------------------------------------------------------
# Befriend / sync-toggle helpers
# ---------------------------------------------------------------------------

def on_befriend_toggle(camera_obj):
    """Handle befriend toggle"""
    if frame_manager.is_updating or not camera_obj:
        return

    scene = bpy.context.scene
    settings = camera_obj.data.cameraide_settings

    with prevent_recursive_update():
        if settings.use_custom_settings:
            from .marker_detection import auto_detect_frame_mode
            settings.frame_range_mode = auto_detect_frame_mode(camera_obj)

            stored = frame_manager.get_range(camera_obj)
            if stored:
                settings.frame_start = stored['start']
                settings.frame_end = stored['end']
                if settings.sync_frame_range and settings.frame_range_mode == 'PER_CAMERA' and camera_obj == scene.camera:
                    from .frame_manager import apply_frame_range_to_scene
                    apply_frame_range_to_scene(camera_obj, scene)

            update_camera_name(camera_obj, True)
            # Push new cameraide settings into native panel
            apply_cameraide_to_native(camera_obj, scene)
        else:
            frame_manager.store_range(camera_obj)
            update_camera_name(camera_obj, False)

        frame_manager.store_range(camera_obj)


def on_sync_toggle(camera_obj):
    """Handle sync toggle"""
    if frame_manager.is_updating or not camera_obj:
        return

    scene = bpy.context.scene
    settings = camera_obj.data.cameraide_settings

    with prevent_recursive_update():
        if settings.sync_frame_range and settings.frame_range_mode == 'PER_CAMERA':
            stored = frame_manager.get_range(camera_obj)
            if stored and camera_obj == scene.camera:
                from .frame_manager import apply_frame_range_to_scene
                apply_frame_range_to_scene(camera_obj, scene)
        else:
            frame_manager.store_range(camera_obj)


# ---------------------------------------------------------------------------
# Register / unregister
# ---------------------------------------------------------------------------

def register():
    frame_manager.clear()
    _native_snapshot.clear()
    if on_active_camera_changed not in bpy.app.handlers.depsgraph_update_post:
        bpy.app.handlers.depsgraph_update_post.append(on_active_camera_changed)
    if on_native_render_settings_changed not in bpy.app.handlers.depsgraph_update_post:
        bpy.app.handlers.depsgraph_update_post.append(on_native_render_settings_changed)


def unregister():
    frame_manager.clear()
    _native_snapshot.clear()
    if on_active_camera_changed in bpy.app.handlers.depsgraph_update_post:
        bpy.app.handlers.depsgraph_update_post.remove(on_active_camera_changed)
    if on_native_render_settings_changed in bpy.app.handlers.depsgraph_update_post:
        bpy.app.handlers.depsgraph_update_post.remove(on_native_render_settings_changed)


__all__ = [
    'update_viewport_resolution',
    'update_frame_start',
    'update_frame_end',
    'on_active_camera_changed',
    'on_native_render_settings_changed',
    'on_befriend_toggle',
    'on_sync_toggle',
    'apply_cameraide_to_native',
]
