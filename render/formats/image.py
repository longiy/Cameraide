"""Image format handlers for Cameraide"""
import bpy


def apply_image_format(settings, context):
    """Apply image format specific settings"""
    image_settings = context.scene.render.image_settings
    
    if settings.output_format == 'PNG':
        image_settings.color_mode = 'RGBA'
        image_settings.color_depth = settings.png_color_depth
        image_settings.compression = settings.png_compression
        
    elif settings.output_format == 'JPEG':
        image_settings.color_mode = 'RGB'
        image_settings.quality = settings.jpeg_quality
        
    elif settings.output_format == 'OPEN_EXR':
        image_settings.color_mode = 'RGBA'
        image_settings.color_depth = settings.exr_color_depth
        image_settings.exr_codec = settings.exr_codec
        if hasattr(image_settings, 'use_preview'):
            image_settings.use_preview = settings.exr_preview


def store_image_settings(storage_dict, context):
    """Store image format specific settings"""
    image_settings = context.scene.render.image_settings
    format_settings = {}
    
    if hasattr(image_settings, 'color_depth'):
        format_settings['color_depth'] = image_settings.color_depth
    if hasattr(image_settings, 'compression'):
        format_settings['compression'] = image_settings.compression
    if hasattr(image_settings, 'quality'):
        format_settings['quality'] = image_settings.quality
    if hasattr(image_settings, 'exr_codec'):
        format_settings['exr_codec'] = image_settings.exr_codec
    if hasattr(image_settings, 'use_preview'):
        format_settings['use_preview'] = image_settings.use_preview
    
    storage_dict.update(format_settings)
