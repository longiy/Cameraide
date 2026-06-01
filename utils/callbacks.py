"""Viewport and camera change callbacks for Cameraide"""
import bpy
from .frame_manager import frame_manager, prevent_recursive_update
from .camera_names import update_camera_name

_syncing_native = False


def update_viewport_resolution(context):
    """Update viewport resolution"""
    if not context.scene.camera or not context.scene.camera.data.cameraide_settings.use_custom_settings:
        return
        
    settings = context.scene.camera.data.cameraide_settings
    context.scene.render.resolution_x = settings.resolution_x
    context.scene.render.resolution_y = settings.resolution_y
    context.scene.render.resolution_percentage = settings.resolution_percentage


def update_frame_start(self, context):
    """Frame start update callback"""
    if frame_manager.is_updating:
        return
        
    camera = context.scene.camera
    if not camera or camera.data.cameraide_settings != self:
        return
    
    # Only sync if in per-camera mode and sync is enabled
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
        
    # Only sync if in per-camera mode and sync is enabled
    if self.use_custom_settings and self.sync_frame_range and self.frame_range_mode == 'PER_CAMERA':
        with prevent_recursive_update():
            context.scene.frame_end = self.frame_end
            frame_manager.store_range(camera)


@bpy.app.handlers.persistent
def on_active_camera_changed(scene):
    """Handle camera switching"""
    if frame_manager.is_updating:
        return

    current_camera = scene.camera
    if not current_camera or current_camera.type != 'CAMERA':
        return
        
    settings = current_camera.data.cameraide_settings
    
    # Only apply frame range if in per-camera mode with sync enabled
    if settings.use_custom_settings and settings.sync_frame_range and settings.frame_range_mode == 'PER_CAMERA':
        with prevent_recursive_update():
            scene.frame_start = settings.frame_start
            scene.frame_end = settings.frame_end
            frame_manager.store_range(current_camera)
    
    frame_manager.previous_camera = current_camera
    update_viewport_resolution(bpy.context)


def on_befriend_toggle(camera_obj):
    """Handle befriend toggle"""
    if frame_manager.is_updating or not camera_obj:
        return

    scene = bpy.context.scene
    settings = camera_obj.data.cameraide_settings
    
    with prevent_recursive_update():
        if settings.use_custom_settings:
            # On befriend - auto-detect frame mode
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
        else:
            # On unfriend
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
            # On sync enable (only in per-camera mode)
            stored = frame_manager.get_range(camera_obj)
            if stored and camera_obj == scene.camera:
                from .frame_manager import apply_frame_range_to_scene
                apply_frame_range_to_scene(camera_obj, scene)
        else:
            # On sync disable
            frame_manager.store_range(camera_obj)


@bpy.app.handlers.persistent
def on_native_render_settings_changed(scene):
    """Sync native Blender render settings back into the active cameraide camera"""
    global _syncing_native
    if _syncing_native or frame_manager.is_updating:
        return

    from .render_manager import RenderCleanupManager
    if RenderCleanupManager._original_settings is not None:
        return  # Cameraide is applying settings for a render — don't read back

    cam = scene.camera
    if not cam or not cam.data.cameraide_settings.use_custom_settings:
        return

    settings = cam.data.cameraide_settings
    render = scene.render
    image_settings = render.image_settings

    _syncing_native = True
    try:
        fmt = image_settings.file_format

        # Map native file_format back to cameraide output_format
        if fmt == 'PNG' and settings.output_format != 'PNG':
            settings.output_format = 'PNG'
        elif fmt == 'JPEG' and settings.output_format != 'JPEG':
            settings.output_format = 'JPEG'
        elif fmt == 'OPEN_EXR' and settings.output_format != 'OPEN_EXR':
            settings.output_format = 'OPEN_EXR'
        elif fmt == 'FFMPEG':
            ffmpeg = render.ffmpeg
            new_fmt = None
            if ffmpeg.format == 'MPEG4' and ffmpeg.codec == 'H264':
                new_fmt = 'H264_MP4'
            elif ffmpeg.format == 'MKV' and ffmpeg.codec == 'H264':
                new_fmt = 'H264_MKV'
            elif ffmpeg.format == 'QUICKTIME':
                new_fmt = 'PRORES_MOV'
            if new_fmt and settings.output_format != new_fmt:
                settings.output_format = new_fmt

        # Sync format-specific settings
        current = settings.output_format
        if current == 'PNG':
            if hasattr(image_settings, 'color_depth') and settings.png_color_depth != image_settings.color_depth:
                settings.png_color_depth = image_settings.color_depth
            if hasattr(image_settings, 'compression') and settings.png_compression != image_settings.compression:
                settings.png_compression = image_settings.compression
            if settings.png_film_transparent != render.film_transparent:
                settings.png_film_transparent = render.film_transparent
        elif current == 'JPEG':
            if hasattr(image_settings, 'quality') and settings.jpeg_quality != image_settings.quality:
                settings.jpeg_quality = image_settings.quality
        elif current == 'OPEN_EXR':
            if hasattr(image_settings, 'color_depth') and settings.exr_color_depth != image_settings.color_depth:
                settings.exr_color_depth = image_settings.color_depth
            if hasattr(image_settings, 'exr_codec') and settings.exr_codec != image_settings.exr_codec:
                settings.exr_codec = image_settings.exr_codec
            if settings.exr_film_transparent != render.film_transparent:
                settings.exr_film_transparent = render.film_transparent
        elif current == 'PRORES_MOV':
            if settings.prores_film_transparent != render.film_transparent:
                settings.prores_film_transparent = render.film_transparent
        elif current in {'H264_MP4', 'H264_MKV'}:
            ffmpeg = render.ffmpeg
            if hasattr(ffmpeg, 'constant_rate_factor'):
                try:
                    if settings.video_quality != ffmpeg.constant_rate_factor:
                        settings.video_quality = ffmpeg.constant_rate_factor
                except Exception:
                    pass
            if settings.video_bitrate != ffmpeg.video_bitrate:
                settings.video_bitrate = ffmpeg.video_bitrate
            if settings.video_gopsize != ffmpeg.gopsize:
                settings.video_gopsize = ffmpeg.gopsize
            if ffmpeg.audio_codec != 'NONE':
                if not settings.use_audio:
                    settings.use_audio = True
                if settings.audio_codec != ffmpeg.audio_codec:
                    try:
                        settings.audio_codec = ffmpeg.audio_codec
                    except Exception:
                        pass
                if settings.audio_bitrate != ffmpeg.audio_bitrate:
                    settings.audio_bitrate = ffmpeg.audio_bitrate
            else:
                if settings.use_audio:
                    settings.use_audio = False

        # Resolution
        if settings.resolution_x != render.resolution_x:
            settings.resolution_x = render.resolution_x
        if settings.resolution_y != render.resolution_y:
            settings.resolution_y = render.resolution_y
        if settings.resolution_percentage != render.resolution_percentage:
            settings.resolution_percentage = render.resolution_percentage

    finally:
        _syncing_native = False


def register():
    frame_manager.clear()
    if on_active_camera_changed not in bpy.app.handlers.depsgraph_update_post:
        bpy.app.handlers.depsgraph_update_post.append(on_active_camera_changed)
    if on_native_render_settings_changed not in bpy.app.handlers.depsgraph_update_post:
        bpy.app.handlers.depsgraph_update_post.append(on_native_render_settings_changed)


def unregister():
    frame_manager.clear()
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
    'on_sync_toggle'
]
