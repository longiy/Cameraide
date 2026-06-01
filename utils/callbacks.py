"""Viewport and camera change callbacks for Cameraide"""
import bpy
from .frame_manager import frame_manager, prevent_recursive_update
from .camera_names import update_camera_name

# Set True while cameraide is writing to native Blender settings so the
# msgbus listener ignores those writes (they're not user edits).
_syncing_native = False

# A single owner object keeps all msgbus subscriptions alive.
_msgbus_owner = object()


# ---------------------------------------------------------------------------
# Cameraide → Native  (push cameraide settings into Blender's render panel)
# ---------------------------------------------------------------------------

def apply_cameraide_to_native(cam, scene):
    """Push this camera's cameraide settings into Blender's native render panel.
    Called on camera switch so the native panel always reflects the active camera.
    Sets _syncing_native so msgbus ignores the writes.
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
            elif fmt == 'H264_MKV':
                ffmpeg.format = 'MKV'
                ffmpeg.codec = 'H264'
            elif fmt == 'PRORES_MOV':
                ffmpeg.format = 'QUICKTIME'
                ffmpeg.codec = 'PRORES'
                if hasattr(ffmpeg, 'constant_rate_factor'):
                    ffmpeg.constant_rate_factor = 'PERC_LOSSLESS'
                ffmpeg.gopsize = 1
                render.film_transparent = settings.prores_film_transparent

            if fmt in {'H264_MP4', 'H264_MKV'}:
                if hasattr(ffmpeg, 'constant_rate_factor'):
                    ffmpeg.constant_rate_factor = settings.video_quality
                ffmpeg.video_bitrate = settings.video_bitrate
                ffmpeg.gopsize = settings.video_gopsize
                render.film_transparent = False

            ffmpeg.audio_codec = settings.audio_codec if settings.audio_codec != 'NONE' else 'NONE'
            if settings.audio_codec != 'NONE':
                ffmpeg.audio_bitrate = settings.audio_bitrate

    finally:
        _syncing_native = False


# ---------------------------------------------------------------------------
# Native → Cameraide  (read native panel back into cameraide settings)
# ---------------------------------------------------------------------------

def _sync_native_to_cameraide(cam, scene):
    """Read current native render settings into the camera's cameraide properties."""
    settings = cam.data.cameraide_settings
    render = scene.render
    img = render.image_settings
    native_fmt = img.file_format

    if native_fmt == 'PNG':
        settings.output_format = 'PNG'
        settings.png_color_depth = getattr(img, 'color_depth', '8')
        settings.png_compression = getattr(img, 'compression', 15)
        settings.png_film_transparent = render.film_transparent

    elif native_fmt == 'JPEG':
        settings.output_format = 'JPEG'
        settings.jpeg_quality = getattr(img, 'quality', 90)

    elif native_fmt == 'OPEN_EXR':
        settings.output_format = 'OPEN_EXR'
        settings.exr_color_depth = getattr(img, 'color_depth', '16')
        settings.exr_codec = getattr(img, 'exr_codec', 'ZIP')
        settings.exr_film_transparent = render.film_transparent

    elif native_fmt == 'FFMPEG':
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

        try:
            settings.audio_codec = ffmpeg.audio_codec
        except Exception:
            pass
        if ffmpeg.audio_codec != 'NONE':
            settings.audio_bitrate = ffmpeg.audio_bitrate

def _sync_native_resolution_to_cameraide(cam, scene):
    """Sync only resolution from native → cameraide."""
    settings = cam.data.cameraide_settings
    render = scene.render
    settings.resolution_x = render.resolution_x
    settings.resolution_y = render.resolution_y
    settings.resolution_percentage = render.resolution_percentage


def _sync_native_film_transparent_to_cameraide(cam, scene):
    """Sync only film_transparent from native → cameraide (per active format)."""
    settings = cam.data.cameraide_settings
    val = scene.render.film_transparent
    fmt = settings.output_format
    if fmt == 'PNG':
        settings.png_film_transparent = val
    elif fmt == 'OPEN_EXR':
        settings.exr_film_transparent = val
    elif fmt == 'PRORES_MOV':
        settings.prores_film_transparent = val


# ---------------------------------------------------------------------------
# Two separate msgbus callbacks — format/codec vs resolution/transparency
# Keeping them apart prevents update_viewport_resolution (which writes
# RenderSettings.resolution_*) from ever triggering a format revert.
# ---------------------------------------------------------------------------

def _guard_check():
    """Shared early-exit logic. Returns (cam, scene) or (None, None)."""
    if _syncing_native:
        return None, None
    from .render_manager import RenderCleanupManager
    if RenderCleanupManager._original_settings is not None:
        return None, None
    context = bpy.context
    if not context or not hasattr(context, 'scene'):
        return None, None
    scene = context.scene
    cam = scene.camera
    if not cam or not cam.data.cameraide_settings.use_custom_settings:
        return None, None
    return cam, scene


def _on_native_format_changed():
    """Fired by ImageFormatSettings and FFmpegSettings msgbus.
    Syncs format/codec/quality/audio — never touches resolution."""
    global _syncing_native
    cam, scene = _guard_check()
    if cam is None:
        return

    _syncing_native = True
    try:
        _sync_native_to_cameraide(cam, scene)
    finally:
        _syncing_native = False


def _on_native_resolution_changed():
    """Fired by RenderSettings.resolution_* and film_transparent msgbus.
    Syncs only those values — never touches output_format."""
    global _syncing_native
    cam, scene = _guard_check()
    if cam is None:
        return

    _syncing_native = True
    try:
        _sync_native_resolution_to_cameraide(cam, scene)
        _sync_native_film_transparent_to_cameraide(cam, scene)
    finally:
        _syncing_native = False


# ---------------------------------------------------------------------------
# Resolution live push (cameraide panel → native, real-time)
# ---------------------------------------------------------------------------

def update_viewport_resolution(context):
    """Write active cameraide camera resolution into native Blender render settings."""
    global _syncing_native
    cam = context.scene.camera
    if not cam or not cam.data.cameraide_settings.use_custom_settings:
        return

    settings = cam.data.cameraide_settings
    _syncing_native = True  # suppress msgbus from treating this as a user edit
    try:
        context.scene.render.resolution_x = settings.resolution_x
        context.scene.render.resolution_y = settings.resolution_y
        context.scene.render.resolution_percentage = settings.resolution_percentage
    finally:
        _syncing_native = False


# ---------------------------------------------------------------------------
# Frame range update callbacks (hooked from properties.py)
# ---------------------------------------------------------------------------

def update_frame_start(self, context):
    if frame_manager.is_updating:
        return
    # Clamp start to at most end - 1
    if self.frame_start >= self.frame_end:
        self.frame_start = self.frame_end - 1
        return
    camera = context.scene.camera
    if not camera or camera.data.cameraide_settings != self:
        return
    if self.use_custom_settings and self.sync_frame_range and self.frame_range_mode == 'PER_CAMERA':
        with prevent_recursive_update():
            context.scene.frame_start = self.frame_start
            frame_manager.store_range(camera)


def update_frame_end(self, context):
    if frame_manager.is_updating:
        return
    # Clamp end to at least start + 1
    if self.frame_end <= self.frame_start:
        self.frame_end = self.frame_start + 1
        return
    camera = context.scene.camera
    if not camera or camera.data.cameraide_settings != self:
        return
    if self.use_custom_settings and self.sync_frame_range and self.frame_range_mode == 'PER_CAMERA':
        with prevent_recursive_update():
            context.scene.frame_end = self.frame_end
            frame_manager.store_range(camera)


# ---------------------------------------------------------------------------
# Persistent depsgraph handler — camera switching only
# ---------------------------------------------------------------------------

@bpy.app.handlers.persistent
def on_active_camera_changed(scene):
    if frame_manager.is_updating:
        return

    current_camera = scene.camera
    if not current_camera or current_camera.type != 'CAMERA':
        return

    camera_switched = (frame_manager.previous_camera != current_camera)

    settings = current_camera.data.cameraide_settings
    if settings.use_custom_settings and settings.sync_frame_range and settings.frame_range_mode == 'PER_CAMERA':
        with prevent_recursive_update():
            scene.frame_start = settings.frame_start
            scene.frame_end = settings.frame_end
            frame_manager.store_range(current_camera)

    frame_manager.previous_camera = current_camera
    update_viewport_resolution(bpy.context)

    if camera_switched:
        apply_cameraide_to_native(current_camera, scene)


# ---------------------------------------------------------------------------
# Befriend / sync-toggle helpers
# ---------------------------------------------------------------------------

def on_befriend_toggle(camera_obj):
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
            apply_cameraide_to_native(camera_obj, scene)
        else:
            frame_manager.store_range(camera_obj)
            update_camera_name(camera_obj, False)

        frame_manager.store_range(camera_obj)


def on_sync_toggle(camera_obj):
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

def _subscribe_msgbus():
    """Subscribe to native Blender render property changes via msgbus.

    Two separate callbacks:
    - _on_native_format_changed  → ImageFormatSettings + FFmpegSettings
    - _on_native_resolution_changed → specific RenderSettings properties only

    Keeping them separate ensures that update_viewport_resolution writing
    resolution never accidentally triggers a format sync.
    """
    # Format / codec callbacks
    for rna_type in (bpy.types.ImageFormatSettings, bpy.types.FFmpegSettings):
        bpy.msgbus.subscribe_rna(
            key=rna_type,
            owner=_msgbus_owner,
            args=(),
            notify=_on_native_format_changed,
        )

    # Resolution + transparency — full RenderSettings type is fine here because
    # _on_native_resolution_changed never touches output_format, so even if it
    # fires from update_viewport_resolution writes it only does a resolution
    # no-op (native == cameraide at that point).
    bpy.msgbus.subscribe_rna(
        key=bpy.types.RenderSettings,
        owner=_msgbus_owner,
        args=(),
        notify=_on_native_resolution_changed,
    )



def register():
    frame_manager.clear()
    if on_active_camera_changed not in bpy.app.handlers.depsgraph_update_post:
        bpy.app.handlers.depsgraph_update_post.append(on_active_camera_changed)
    # msgbus must be set up after a short delay because Blender's RNA isn't
    # fully ready at register time — use a one-shot timer
    bpy.app.timers.register(_subscribe_msgbus, first_interval=0.1)


def unregister():
    frame_manager.clear()
    bpy.msgbus.clear_by_owner(_msgbus_owner)
    if on_active_camera_changed in bpy.app.handlers.depsgraph_update_post:
        bpy.app.handlers.depsgraph_update_post.remove(on_active_camera_changed)


__all__ = [
    'update_viewport_resolution',
    'update_frame_start',
    'update_frame_end',
    'on_active_camera_changed',
    'on_befriend_toggle',
    'on_sync_toggle',
    'apply_cameraide_to_native',
]
