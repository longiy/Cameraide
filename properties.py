"""
properties.py - NO CHANGES NEEDED

The imports still work because:
- update_frame_start is still in utils/callbacks.py
- update_frame_end is still in utils/callbacks.py

This file remains unchanged from the original.
"""

import bpy
from bpy.props import (IntProperty, StringProperty, EnumProperty, 
                      BoolProperty, PointerProperty, FloatProperty)
from bpy.types import PropertyGroup
from .utils.callbacks import (
    update_frame_start, 
    update_frame_end
)

def update_custom_settings(self, context):
    """Callback when use_custom_settings is toggled"""
    if self.use_custom_settings and not hasattr(self, '_frame_range_mode'):
        self.frame_range_mode = 'PER_CAMERA'

class CameraideSettings(PropertyGroup):
    # Basic Settings
    use_custom_settings: BoolProperty(
        name="Enable",
        description="Enable custom settings for this camera",
        default=False,
        update=update_custom_settings
    )
    
    # Resolution Settings
    resolution_x: IntProperty(
        name="X",
        description="Custom X resolution for this camera",
        default=1920,
        subtype="PIXEL"
    )
    resolution_y: IntProperty(
        name="Y",
        description="Custom Y resolution for this camera",
        default=1080,
        subtype="PIXEL"
    )
    resolution_percentage: IntProperty(
        name="Scale",
        description="Resolution scaling percentage",
        default=100,
        min=1,
        max=400,
        subtype='PERCENTAGE'
    )
    
    # Frame Range Mode
    frame_range_mode: EnumProperty(
        name="Frame Range Mode",
        description="Choose how frame ranges are determined for this camera",
        items=[
            ('TIMELINE_MARKERS', "Timeline Markers", 
             "Use Blender's timeline camera markers to define frame ranges"),
            ('PER_CAMERA', "Per-Camera Ranges", 
             "Use custom frame ranges defined per camera (allows overlaps)"),
        ],
        default='PER_CAMERA'
    )
    
    # Frame Range Settings
    stored_frame_start: IntProperty(
        name="Stored Start Frame",
        default=1
    )
    stored_frame_end: IntProperty(
        name="Stored End Frame",
        default=250
    )
    
    frame_start: IntProperty(
        name="Start",
        default=1,
        update=update_frame_start
    )
    frame_end: IntProperty(
        name="End",
        default=250,
        update=update_frame_end
    )
    
    frame_step: IntProperty(
        name="Step",
        description="Step between frames",
        default=1,
        min=1
    )
    
    sync_frame_range: BoolProperty(
        name="Sync Frame Range",
        description="Synchronize viewport timeline with camera's frame range",
        default=False
    )
    
    # Output Settings
    output_path: StringProperty(
        name="Path",
        description="Root output path",
        default="//",
        subtype='DIR_PATH'
    )

    output_subfolder: StringProperty(
        name="Folder",
        description="Subfolder name (will be created under the output path)",
        default="Folder"
    )

    output_filename: StringProperty(
        name="Name",
        description="Output file name",
        default="Name"
    )
    
    output_format: EnumProperty(
        name="Format",
        description="Output file format",
        items=[
            ('PNG', "PNG", "PNG Format\n• Color Depth: 8/16-bit\n• Lossless compression\n• Alpha support"),
            ('JPEG', "JPEG", "JPEG Format\n• 8-bit color depth\n• Quality: 90%\n• Lossy compression"),
            ('OPEN_EXR', "EXR", "OpenEXR Format\n• Color Depth: 16/32-bit float\n• Multiple compression options\n• HDR support\n• Alpha support"),
            ('H264_MP4', "MP4 H264", "MP4 with H.264\n• Standard MP4 container\n• H.264 codec\n• Universal compatibility"),
            ('H264_MKV', "MKV H264", "MKV with H.264\n• Matroska container\n• H.264 codec\n• Open format"),
            ('PRORES_MOV', "MOV ProRes", "MOV with ProRes 4444\n• QuickTime container\n• ProRes 4444 codec\n• Professional editing\n• Alpha support"),
        ],
        default='PNG'
    )

    # PNG Settings
    png_color_depth: EnumProperty(
        name="Color Depth",
        description="Color depth for PNG output",
        items=[
            ('8', "8", "8-bit"),
            ('16', "16", "16-bit"),
        ],
        default='8'
    )
    png_compression: IntProperty(
        name="Compression",
        description="PNG compression level",
        min=0,
        max=100,
        default=15,
        subtype='PERCENTAGE'
    )
    
    # JPEG Settings
    jpeg_quality: IntProperty(
        name="Quality",
        description="JPEG quality level",
        min=0,
        max=100,
        default=90,
        subtype='PERCENTAGE'
    )
    
    # EXR Settings
    exr_color_depth: EnumProperty(
        name="Color Depth",
        description="Color depth for EXR output",
        items=[
            ('16', "Half", "16-bit float"),
            ('32', "Full", "32-bit float"),
        ],
        default='16'
    )
    exr_codec: EnumProperty(
        name="Codec",
        description="Compression method for EXR output",
        items=[
            ('NONE', "None", "No compression"),
            ('PXR24', "Pxr24 (lossy)", "Pxr24 compression (lossy)"),
            ('ZIP', "ZIP (lossless)", "ZIP compression (lossless)"),
            ('PIZ', "PIZ (lossless)", "PIZ compression (lossless)"),
            ('RLE', "RLE (lossless)", "Run-length encoding (lossless)"),
            ('ZIPS', "ZIPS (lossless)", "ZIPS compression (lossless)"),
            ('B44', "B44 (lossy)", "B44 compression (lossy)"),
            ('B44A', "B44A (lossy)", "B44A compression (lossy)"),
            ('DWAA', "DWAA (lossy)", "DWAA compression (lossy)"),
            ('DWAB', "DWAB (lossy)", "DWAB compression (lossy)"),
        ],
        default='ZIP'
    )
    exr_preview: BoolProperty(
        name="Preview",
        description="Save JPEG preview images in the same directory",
        default=False
    )
    
    # Video Quality Settings
    video_quality: EnumProperty(
        name="Quality",
        description="Video encoding quality preset",
        items=[
            ('LOSSLESS', 'Lossless', 'Lossless encoding (huge files)'),
            ('PERC_LOSSLESS', 'Perceptually Lossless', 'High quality, nearly lossless'),
            ('HIGH', 'High Quality', 'High quality (recommended)'),
            ('MEDIUM', 'Medium Quality', 'Medium quality'),
            ('LOW', 'Low Quality', 'Low quality'),
        ],
        default='HIGH'
    )
    
    video_bitrate: IntProperty(
        name="Bitrate",
        description="Video bitrate (kb/s) - used when quality is set to custom",
        min=1,
        max=100000,
        default=6000,
        subtype='NONE'
    )
    
    video_gopsize: IntProperty(
        name="GOP Size",
        description="Distance between keyframes",
        min=0,
        max=500,
        default=12,
        subtype='NONE'
    )
    
    # Audio Settings
    use_audio: BoolProperty(
        name="Include Audio",
        description="Include audio in the rendered video",
        default=False
    )
    
    audio_codec: EnumProperty(
        name="Audio Codec",
        description="Audio codec settings",
        items=[
            ('NONE', "No Audio", "Don't include audio"),
            ('AAC', "AAC", "AAC audio codec (recommended)"),
            ('MP3', "MP3", "MP3 audio codec"),
        ],
        default='NONE'
    )
    
    audio_bitrate: IntProperty(
        name="Audio Bitrate",
        description="Audio bitrate (kb/s)",
        min=32,
        max=384,
        default=192,
        subtype='NONE'
    )
    
    # Additional Settings
    overwrite_existing: BoolProperty(
        name="Overwrite",
        description="If enabled, existing files will be overwritten",
        default=True
    )
    include_camera_name: BoolProperty(
        name="Camera Name",
        description="If enabled, the camera name will be included in the filename",
        default=False
    )
    burn_metadata: BoolProperty(
        name="Burn Metadata",
        description="Synchronize with 'Burn Into Image' metadata setting",
        default=False
    )
    film_transparent: BoolProperty(
        name="Alpha Transparency",
        description="Make the alpha channel transparent for this camera",
        default=True
    )
    
    # UI Display Properties
    show_resolution_settings: BoolProperty(
        name="Show Resolution Settings",
        description="Show or hide resolution settings",
        default=True
    )
    show_frame_range: BoolProperty(
        name="Show Frame Range",
        description="Show or hide frame range settings",
        default=True
    )
    show_file_output: BoolProperty(
        name="Show File Output",
        description="Show or hide file output settings",
        default=True
    )
    show_format_settings: BoolProperty(
        name="Show Format Settings",
        description="Show or hide format specific settings",
        default=True
    )
    show_extra_settings: BoolProperty(
        name="Show Extra Settings",
        description="Show or hide extra settings",
        default=False
    )


def register():
    bpy.utils.register_class(CameraideSettings)
    bpy.types.Camera.cameraide_settings = PointerProperty(type=CameraideSettings)

def unregister():
    del bpy.types.Camera.cameraide_settings
    bpy.utils.unregister_class(CameraideSettings)
