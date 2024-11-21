import bpy
from bpy.props import (IntProperty, StringProperty, EnumProperty, 
                      BoolProperty, PointerProperty, FloatProperty)
from bpy.types import PropertyGroup
from .utils.callbacks import (
    update_frame_start, 
    update_frame_end
)

class CameraideSettings(PropertyGroup):
    # Basic Settings
    use_custom_settings: BoolProperty(
        name="Enable",
        description="Enable custom settings for this camera",
        default=False
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
        max=100,
        subtype='PERCENTAGE'
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
        name="Start Frame",
        default=1,
        update=update_frame_start
    )
    frame_end: IntProperty(
        name="End Frame",
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
    
    # File Output Settings
    output_folder: StringProperty(
        name="Output",
        description="Custom output folder for this camera",
        default="//tmp/",
        subtype='DIR_PATH'
    )
    file_name: StringProperty(
        name="Name",
        description="Custom output file name for this camera",
        default="render"
    )
    file_format: EnumProperty(
        name="Format",
        description="Custom output file format for this camera",
        items=[
            ('PNG', "PNG", "Save as PNG"),
            ('JPEG', "JPEG", "Save as JPEG"),
            ('OPEN_EXR', "OpenEXR", "Save as OpenEXR"),
        ],
        default='PNG'
    )
    
    # PNG Settings
    png_color_mode: EnumProperty(
        name="Color Mode",
        description="Color mode for PNG output",
        items=[
            ('BW', "BW", "Greyscale"),
            ('RGB', "RGB", "RGB"),
            ('RGBA', "RGBA", "RGB with Alpha"),
        ],
        default='RGBA'
    )
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
    jpeg_color_mode: EnumProperty(
        name="Color Mode",
        description="Color mode for JPEG output",
        items=[
            ('BW', "BW", "Greyscale"),
            ('RGB', "RGB", "RGB"),
        ],
        default='RGB'
    )
    jpeg_quality: IntProperty(
        name="Quality",
        description="JPEG quality level",
        min=0,
        max=100,
        default=90,
        subtype='PERCENTAGE'
    )
    
    # EXR Settings
    exr_color_mode: EnumProperty(
        name="Color Mode",
        description="Color mode for EXR output",
        items=[
            ('BW', "BW", "Greyscale"),
            ('RGB', "RGB", "RGB"),
            ('RGBA', "RGBA", "RGB with Alpha"),
        ],
        default='RGBA'
    )
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
    ignore_markers: BoolProperty(
        name="Ignore Markers",
        description="Temporarily remove camera markers during rendering",
        default=True
    )

def register():
    bpy.utils.register_class(CameraideSettings)
    bpy.types.Camera.cameraide_settings = PointerProperty(type=CameraideSettings)

def unregister():
    del bpy.types.Camera.cameraide_settings
    bpy.utils.unregister_class(CameraideSettings)