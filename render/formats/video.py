"""Video format handlers for Cameraide"""
import bpy


def apply_video_format(settings, context):
    """Apply video-specific settings"""
    scene = context.scene
    
    # CRITICAL: Set media_type to VIDEO first
    scene.render.image_settings.media_type = 'VIDEO'
    
    # Now set file_format to FFMPEG
    scene.render.image_settings.file_format = 'FFMPEG'
    
    ffmpeg = scene.render.ffmpeg
    
    format_map = {
        'H264_MP4': 'MPEG4',
        'H264_MKV': 'MKV',
        'PRORES_MOV': 'QUICKTIME'
    }
    
    codec_map = {
        'H264_MP4': 'H264',
        'H264_MKV': 'H264',
        'PRORES_MOV': 'PRORES'
    }
    
    ffmpeg.format = format_map[settings.output_format]
    ffmpeg.codec = codec_map[settings.output_format]
    
    if settings.output_format == 'PRORES_MOV':
        if hasattr(ffmpeg, 'constant_rate_factor'):
            ffmpeg.constant_rate_factor = 'PERC_LOSSLESS'
        ffmpeg.gopsize = 1
    else:
        if hasattr(ffmpeg, 'constant_rate_factor'):
            ffmpeg.constant_rate_factor = settings.video_quality
        ffmpeg.video_bitrate = settings.video_bitrate
        ffmpeg.minrate = 0
        ffmpeg.maxrate = settings.video_bitrate * 2
        ffmpeg.gopsize = settings.video_gopsize
    
    if settings.use_audio and settings.audio_codec != 'NONE':
        ffmpeg.audio_codec = settings.audio_codec
        ffmpeg.audio_bitrate = settings.audio_bitrate
    else:
        ffmpeg.audio_codec = 'NONE'


def store_video_settings(storage_dict, context):
    """Store video format specific settings"""
    ffmpeg = context.scene.render.ffmpeg
    storage_dict.update({
        'ffmpeg_format': ffmpeg.format,
        'ffmpeg_codec': ffmpeg.codec,
        'ffmpeg_constant_rate_factor': getattr(ffmpeg, 'constant_rate_factor', None),
        'ffmpeg_video_bitrate': ffmpeg.video_bitrate,
        'ffmpeg_minrate': ffmpeg.minrate,
        'ffmpeg_maxrate': ffmpeg.maxrate,
        'ffmpeg_gopsize': ffmpeg.gopsize,
        'ffmpeg_audio_codec': ffmpeg.audio_codec,
        'ffmpeg_audio_bitrate': ffmpeg.audio_bitrate
    })
