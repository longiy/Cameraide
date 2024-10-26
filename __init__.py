bl_info = {
    "name": "Cameraide", 
    "author": "longiy",
    "version": (0, 1, 0),
    "blender": (4, 2, 0),
    "location": "Properties > Camera > Cameraide, 3D View > Sidebar > Cameraide",
    "description": "Adds custom settings for each camera with improved UI and features",
    "category": "Camera",
}

import bpy
import os
from bpy.props import IntProperty, StringProperty, EnumProperty, BoolProperty, PointerProperty, FloatProperty
from bpy.types import Panel, PropertyGroup, Operator, WindowManager

def on_active_camera_changed(scene):
    if scene.camera and scene.camera.data.cameraide_settings.use_custom_settings:
        settings = scene.camera.data.cameraide_settings
        if settings.sync_frame_range:
            scene.frame_start = settings.frame_start
            scene.frame_end = settings.frame_end
    update_viewport_resolution(bpy.context)

def update_viewport_resolution(context):
    scene = context.scene
    if scene.camera and scene.camera.data.cameraide_settings.use_custom_settings:
        settings = scene.camera.data.cameraide_settings
        render = scene.render
        render.resolution_x = settings.resolution_x
        render.resolution_y = settings.resolution_y
        render.resolution_percentage = settings.resolution_percentage
        
        if settings.sync_frame_range:
            scene.frame_start = settings.frame_start
            scene.frame_end = settings.frame_end
        
        # Update all 3D Viewports
        for area in context.screen.areas:
            if area.type == 'VIEW_3D':
                for region in area.regions:
                    if region.type == 'WINDOW':
                        region.tag_redraw()

def update_resolution(self, context):
    update_viewport_resolution(context)

def swap_resolution(self, context):
    settings = self
    settings.resolution_x, settings.resolution_y = settings.resolution_y, settings.resolution_x
    update_viewport_resolution(context)

def update_frame_range(self, context):
     if self.sync_frame_range:
        context.scene.frame_start = self.frame_start
        context.scene.frame_end = self.frame_end
        update_viewport_resolution(context)

def update_camera_frame_range(self, context):
    if self.sync_frame_range:
        # Update viewport timeline
        context.scene.frame_start = self.frame_start
        context.scene.frame_end = self.frame_end


class CameraideSettings(PropertyGroup):

    def swap_resolution(self, context):
        self.resolution_x, self.resolution_y = self.resolution_y, self.resolution_x
        update_viewport_resolution(context)


    sync_frame_range: BoolProperty(
        name="Sync Frame Range",
        description="Synchronize viewport timeline with camera's frame range",
        default=False,
        update=update_frame_range
    )    
    use_custom_settings: BoolProperty(
        name="Enable",
        description="Enable custom settings for this camera",
        default=False,
        update=update_frame_range
    )
    frame_start: IntProperty(
        name="Start",
        description="Custom start frame for this camera",
        default=1,
        
        update=update_frame_range
    )
    frame_end: IntProperty(
        name="End",
        description="Custom end frame for this camera",
        default=250,
        
        update=update_frame_range
    )
    frame_step: IntProperty(
        name="Step",
        description="Step between frames",
        default=1,
        min=1
    )
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
    resolution_x: IntProperty(
        name="X",
        description="Custom X resolution for this camera",
        default=1920,
        subtype="PIXEL",
        update=update_resolution
    )
    resolution_y: IntProperty(
        name="Y",
        description="Custom Y resolution for this camera",
        default=1080,
        subtype="PIXEL",
        update=update_resolution
    )
    resolution_percentage: IntProperty(
        name="Scale",
        description="Resolution scaling percentage",
        default=100,
        min=1,
        max=100,
        subtype='PERCENTAGE',
        update=update_resolution
    )
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
    
    # New properties for format-specific options
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

    ignore_markers: BoolProperty(
        name="Ignore Markers",
        description="Temporarily remove camera markers during rendering",
        default=True
    )

class Cameraide_settings(Panel):
    bl_label = "Cameraide Settings"
    bl_idname = "Cameraide_settings"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "data"

    @classmethod
    def poll(cls, context):
        return context.camera is not None

    def draw(self, context):
        layout = self.layout
        scene = bpy.context.scene

    
        # Determine which camera to use
        if context.active_object and context.active_object.type == 'CAMERA':
            cam = context.active_object.data
            camera_name = context.active_object.name  # Use the active camera object name
        elif context.scene.camera:
            cam = context.scene.camera.data
            camera_name = context.scene.camera.name  # Use the scene camera name
        else:
            layout.label(text="No active camera in the scene")
            return  # Exit if no camera is available

        settings = cam.cameraide_settings

        # Create the BEFRIEND/FRIEND button based on custom settings status
        row = layout.row()
        row.scale_y = 2.0  # Makes the row 2 times taller
        if settings.use_custom_settings:
            row.operator("camera.toggle_custom_settings", text=f"FRIEND: {camera_name}", icon='FUND', depress=True)
        else:
            row.operator("camera.toggle_custom_settings", text=f"BEFRIEND: {camera_name}", icon='DECORATE')


        if settings.use_custom_settings:

            # Resolution
            split = layout.split(factor=0.5)    
            col = split.column(heading="Resolution")
            col.prop(settings, "resolution_percentage", slider=True)
            row = col.row()
            row.prop(settings, "resolution_x")
            row.prop(settings, "resolution_y")

            row = col.row()
            row.operator("camera.swap_resolution", text="Swap Resolution", icon='ARROW_LEFTRIGHT')


            # Frame Range
            col = split.column(heading="Frame Range")
            col.prop(settings, "frame_step")
            row = col.row()
            row.prop(settings, "frame_start")
            row.prop(settings, "frame_end")

            row = col.row()
            row.operator("camera.toggle_frame_range_sync", 
                         text="Sync " + ("ON" if settings.sync_frame_range else "OFF"), 
                         icon='PREVIEW_RANGE',
                         depress=settings.sync_frame_range)

            # File Output
            split = layout.split(factor=0.7)    
            col = split.column(heading="File Output")
            col.prop(settings, "output_folder",text="")
            col.prop(settings, "file_name",text="")

            col = split.column()
            row = col.row()
            row.prop(settings, "file_format",text="",icon="IMAGE_DATA")

            # Format-specific options
            if settings.file_format == 'PNG':
                # row = layout.row(align=True)
                col.prop(settings, "png_color_mode",text="")
                row = col.row()   
                row.prop(settings, "png_color_depth",text="")
                row.prop(settings, "png_compression", slider=True)
            elif settings.file_format == 'JPEG':
                # row = layout.row(align=True)
                col.prop(settings, "jpeg_color_mode",text="")
                col.prop(settings, "jpeg_quality", slider=True)
            elif settings.file_format == 'OPEN_EXR':
                # row = layout.row(align=True)
                row = col.row() 
                row.prop(settings, "exr_color_mode",text="")
                row.prop(settings, "exr_color_depth",text="")
                row = col.row() 
                row.prop(settings, "exr_codec", text="")
                row.prop(settings, "exr_preview")

            layout.separator()

            row = layout.row()       
            row.prop(settings, "film_transparent")
            row.prop(settings, "overwrite_existing")
            row.prop(settings, "burn_metadata")
            row.prop(settings, "ignore_markers")
            row.prop(settings, "include_camera_name")

            layout.separator()
            layout.separator()
            
            row = layout.row(align=True)
            row.operator("camera.render_selected_viewport", text="Render Viewport", icon="RENDER_ANIMATION")
            row.operator("camera.render_selected_normal", text="Render Normal",icon="RENDER_ANIMATION")

class Cameraide_settings_3dview(Panel):
    bl_label = "Cameraide Settings"
    bl_idname = "Cameraide_settings_3dview"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Camera"
    bl_options = {'DEFAULT_CLOSED'}

    @classmethod
    def poll(cls, context):
        return True  # Always show the panel

    def draw(self, context):
        layout = self.layout
        scene = bpy.context.scene

    
        # Determine which camera to use
        if context.active_object and context.active_object.type == 'CAMERA':
            cam = context.active_object.data
            camera_name = context.active_object.name  # Use the active camera object name
        elif context.scene.camera:
            cam = context.scene.camera.data
            camera_name = context.scene.camera.name  # Use the scene camera name
        else:
            layout.label(text="No active camera in the scene")
            return  # Exit if no camera is available

        settings = cam.cameraide_settings

        # Create the BEFRIEND/FRIEND button based on custom settings status
        row = layout.row()
        row.scale_y = 2.0  # Makes the row 2 times taller
        if settings.use_custom_settings:
            row.operator("camera.toggle_custom_settings", text=f"FRIEND: {camera_name}", icon='FUND', depress=True)
        else:
            row.operator("camera.toggle_custom_settings", text=f"BEFRIEND: {camera_name}", icon='DECORATE')

        
        if settings.use_custom_settings:

            box =layout.box()
            box.label(text="Resolution", icon="KEYTYPE_EXTREME_VEC")

            row = layout.row(align=True)
            row.prop(settings, "resolution_x")
            row.prop(settings, "resolution_y")
            layout.prop(settings, "resolution_percentage", slider=True)
            layout.operator("camera.swap_resolution", text="Swap Resolution", icon='ARROW_LEFTRIGHT')

            box =layout.box()
            box.label(text="Frame Range", icon="KEYTYPE_EXTREME_VEC")
 
            row = layout.row(align=True)
            row.prop(settings, "frame_start")
            row.prop(settings, "frame_end")
            layout.prop(settings, "frame_step")
            layout.operator("camera.toggle_frame_range_sync", 
                         text="Sync " + ("ON" if settings.sync_frame_range else "OFF"), 
                         icon='PREVIEW_RANGE',
                         depress=settings.sync_frame_range)

            layout.separator()
            box =layout.box()
            box.label(text="File Output", icon="KEYTYPE_EXTREME_VEC")
            
            row = layout.row(align=True)
            layout.prop(settings, "output_folder",text="")
            layout.prop(settings, "file_name",text="")

            row = layout.row(align=True)
            row.prop(settings, "file_format",text="")
            row.prop(settings, "png_color_mode",text="")

            # Format-specific options
            if settings.file_format == 'PNG':
                row = layout.row(align=True)
                row.prop(settings, "png_color_depth",text="")
                row.prop(settings, "png_compression", slider=True)
                layout.prop(settings, "overwrite_existing")
            elif settings.file_format == 'JPEG':
                row = layout.row(align=True)
                row.prop(settings, "jpeg_quality", slider=True)
                layout.prop(settings, "overwrite_existing")
            elif settings.file_format == 'OPEN_EXR':
                row = layout.row(align=True)
                row.prop(settings, "exr_color_depth",text="")
                row.prop(settings, "exr_codec", text="")
                row = layout.row(align=True)
                row.prop(settings, "overwrite_existing")
                row.prop(settings, "exr_preview")
                
            box =layout.box()
            box.label(text="File Output Extra", icon="KEYTYPE_EXTREME_VEC")
       
            row = layout.row(align=True)
            layout.prop(settings, "film_transparent")
            layout.prop(settings, "ignore_markers")
            layout.prop(settings, "include_camera_name")
            layout.prop(settings, "burn_metadata")

            row = layout.row()
            row.scale_y = 2.0  # Makes the row 2 times taller
            row.operator("camera.render_selected_viewport", text="Render Viewport", icon="RENDER_ANIMATION")
            row = layout.row()
            row.operator("camera.render_selected_normal", text="Render Normal", icon="RENDER_ANIMATION")


class CAMERA_OT_toggle_custom_settings(Operator):
    bl_idname = "camera.toggle_custom_settings"
    bl_label = "FRIENDSHIP"
    bl_description = "Toggle custom camera settings"

    def execute(self, context):
        if context.active_object and context.active_object.type == 'CAMERA':
            cam = context.active_object.data
        elif context.scene.camera:
            cam = context.scene.camera.data
        else:
            self.report({'ERROR'}, "No active camera found")
            return {'CANCELLED'}

        settings = cam.cameraide_settings
        settings.use_custom_settings = not settings.use_custom_settings
        return {'FINISHED'}

class CAMERA_OT_swap_resolution(Operator):
    bl_idname = "camera.swap_resolution"
    bl_label = "Swap Resolution"
    bl_description = "Swap X and Y resolution values"

    def execute(self, context):
        if context.active_object and context.active_object.type == 'CAMERA':
            cam = context.active_object.data
        elif context.scene.camera:
            cam = context.scene.camera.data
        else:
            self.report({'ERROR'}, "No active camera found")
            return {'CANCELLED'}

        settings = cam.cameraide_settings
        settings.swap_resolution(context)
        return {'FINISHED'}

class CAMERA_OT_toggle_frame_range_sync(Operator):
    bl_idname = "camera.toggle_frame_range_sync"
    bl_label = "Toggle Frame Range Sync"
    bl_description = "Toggle synchronization of viewport timeline with camera's frame range"

    def execute(self, context):
        if context.active_object and context.active_object.type == 'CAMERA':
            cam = context.active_object.data
        elif context.scene.camera:
            cam = context.scene.camera.data
        else:
            self.report({'ERROR'}, "No active camera found")
            return {'CANCELLED'}

        settings = cam.cameraide_settings
        settings.sync_frame_range = not settings.sync_frame_range
        update_frame_range(settings, context)
        return {'FINISHED'}


class CAMERA_OT_render_selected(Operator):
    bl_idname = "camera.render_selected"
    bl_label = "Render Selected Camera"
    bl_description = "Render the active camera with its custom settings"

    _timer = None
    _current_frame = 0
    _total_frames = 0
    progress: FloatProperty(default=0.0)
    is_rendering: BoolProperty(default=False)

    def execute(self, context):
        cam_obj = context.active_object
        if cam_obj.type != 'CAMERA':
            self.report({'ERROR'}, "Selected object is not a camera")
            return {'CANCELLED'}

        settings = cam_obj.data.cameraide_settings
        if not settings.use_custom_settings:
            self.report({'ERROR'}, "Custom settings are not enabled for this camera")
            return {'CANCELLED'}

        # Store original render settings
        self.original_settings = {
            'markers': [],
            'frame_start': context.scene.frame_start,
            'frame_end': context.scene.frame_end,
            'filepath': context.scene.render.filepath,
            'file_format': context.scene.render.image_settings.file_format,
            'color_mode': context.scene.render.image_settings.color_mode,
            'color_depth': context.scene.render.image_settings.color_depth,
            'exr_codec': context.scene.render.image_settings.exr_codec,
            'quality': context.scene.render.image_settings.quality,
            'compression': context.scene.render.image_settings.compression,
            'use_preview': context.scene.render.image_settings.use_preview,
            'resolution_x': context.scene.render.resolution_x,
            'resolution_y': context.scene.render.resolution_y,
            'resolution_percentage': context.scene.render.resolution_percentage,
            'engine': context.scene.render.engine,
            'film_transparent': context.scene.render.film_transparent,
            'use_stamp': context.scene.render.use_stamp
        }

        if settings.ignore_markers:
            self.remove_markers(context)

        # Apply custom settings
        context.scene.frame_start = settings.frame_start
        context.scene.frame_end = settings.frame_end
        context.scene.render.image_settings.file_format = settings.file_format
        context.scene.render.resolution_x = settings.resolution_x
        context.scene.render.resolution_y = settings.resolution_y
        context.scene.render.resolution_percentage = settings.resolution_percentage
        context.scene.render.film_transparent = settings.film_transparent
        context.scene.render.use_stamp = settings.burn_metadata

        # Apply format-specific settings
        if settings.file_format == 'PNG':
            context.scene.render.image_settings.color_mode = settings.png_color_mode
            context.scene.render.image_settings.color_depth = settings.png_color_depth
            context.scene.render.image_settings.compression = settings.png_compression
        elif settings.file_format == 'JPEG':
            context.scene.render.image_settings.color_mode = settings.jpeg_color_mode
            context.scene.render.image_settings.quality = settings.jpeg_quality
        elif settings.file_format == 'OPEN_EXR':
            context.scene.render.image_settings.color_mode = settings.exr_color_mode
            context.scene.render.image_settings.exr_codec = settings.exr_codec
            context.scene.render.image_settings.color_depth = settings.exr_color_depth
            if settings.exr_color_depth == '16':
                context.scene.render.image_settings.use_preview = settings.exr_preview

        # Set the camera as active
        context.scene.camera = cam_obj

        # Set the appropriate render engine (either normal or viewport)
        if self.render_engine:
            context.scene.render.engine = self.render_engine

        # Initialize rendering variables
        self._current_frame = settings.frame_start
        self._total_frames = (settings.frame_end - settings.frame_start) // settings.frame_step + 1
        self.is_rendering = True

        # Add the timer
        wm = context.window_manager
        self._timer = wm.event_timer_add(0.1, window=context.window)
        wm.modal_handler_add(self)

        return {'RUNNING_MODAL'}

    def modal(self, context, event):
        if event.type == 'ESC':
            self.report({'INFO'}, "Rendering canceled by user")
            self.finish(context)
            return {'FINISHED'}

        if event.type == 'TIMER':
            if self._current_frame <= context.scene.frame_end:
                context.scene.frame_set(self._current_frame)
                filename = self.generate_filename(context)

                if not context.scene.camera.data.cameraide_settings.overwrite_existing and os.path.exists(filename):
                    self.report({'WARNING'}, f"Skipping frame {self._current_frame}: File already exists")
                else:
                    context.scene.render.filepath = filename
                    bpy.ops.render.render(write_still=True)

                self.progress = (self._current_frame - context.scene.frame_start + 1) / self._total_frames
                self._current_frame += context.scene.camera.data.cameraide_settings.frame_step
                context.area.tag_redraw()
            else:
                self.finish(context)
                return {'FINISHED'}

        return {'PASS_THROUGH'}

    def remove_markers(self, context):
        scene = context.scene
        self.original_settings['markers'] = []
        markers_to_remove = list(scene.timeline_markers)  # Create a copy of the list
        for marker in markers_to_remove:
            self.original_settings['markers'].append((marker.frame, marker.name, marker.camera))
            scene.timeline_markers.remove(marker)

    def restore_markers(self, context):
        scene = context.scene
        for frame, name, camera in self.original_settings['markers']:
            marker = scene.timeline_markers.new(name, frame=frame)
            marker.camera = camera
    

    def generate_filename(self, context):
        settings = context.scene.camera.data.cameraide_settings
        filename = ""

        if settings.include_camera_name:
            filename += f"{context.scene.camera.name}_"  # Camera name as prefix

        filename += settings.file_name
        filename += f"_{self._current_frame:04d}"
        
        if settings.file_format == 'PNG':
            filename += ".png"
        elif settings.file_format == 'JPEG':
            filename += ".jpg"
        elif settings.file_format == 'OPEN_EXR':
            filename += ".exr"
        
        return os.path.join(settings.output_folder, filename)

    def finish(self, context):
        self.is_rendering = False
        wm = context.window_manager
        wm.event_timer_remove(self._timer)

        # Restore original settings
        context.scene.frame_start = self.original_settings['frame_start']
        context.scene.frame_end = self.original_settings['frame_end']
        context.scene.render.filepath = self.original_settings['filepath']
        context.scene.render.image_settings.file_format = self.original_settings['file_format']
        context.scene.render.image_settings.color_mode = self.original_settings['color_mode']
        context.scene.render.resolution_x = self.original_settings['resolution_x']
        context.scene.render.resolution_y = self.original_settings['resolution_y']
        context.scene.render.resolution_percentage = self.original_settings['resolution_percentage']
        context.scene.render.engine = self.original_settings['engine']
        context.scene.render.film_transparent = self.original_settings['film_transparent']
        context.scene.render.use_stamp = self.original_settings['use_stamp']

        if context.scene.camera.data.cameraide_settings.ignore_markers:
            self.restore_markers(context)

        self.report({'INFO'}, "Rendering complete" if self._current_frame > context.scene.frame_end else "Rendering stopped")
        context.area.tag_redraw()

class CAMERA_OT_render_selected_viewport(CAMERA_OT_render_selected):
    bl_idname = "camera.render_selected_viewport"
    bl_label = "Render Viewport"
    bl_description = "Render using the viewport renderer"
    render_engine = 'BLENDER_EEVEE_NEXT'

class CAMERA_OT_render_selected_normal(CAMERA_OT_render_selected):
    bl_idname = "camera.render_selected_normal"
    bl_label = "Render Normal"
    bl_description = "Render using the normal renderer"
    render_engine = None


def register():
    bpy.utils.register_class(CameraideSettings)
    bpy.utils.register_class(Cameraide_settings)
    bpy.utils.register_class(Cameraide_settings_3dview)
    bpy.utils.register_class(CAMERA_OT_render_selected_viewport)
    bpy.utils.register_class(CAMERA_OT_render_selected_normal)
    bpy.utils.register_class(CAMERA_OT_render_selected)
    bpy.utils.register_class(CAMERA_OT_toggle_custom_settings)
    bpy.utils.register_class(CAMERA_OT_toggle_frame_range_sync)
    bpy.utils.register_class(CAMERA_OT_swap_resolution)
    bpy.types.Camera.cameraide_settings = PointerProperty(type=CameraideSettings)
    
    # Add handler for active camera change
    bpy.app.handlers.depsgraph_update_post.append(on_active_camera_changed)

def unregister():
    bpy.utils.unregister_class(CameraideSettings)
    bpy.utils.unregister_class(Cameraide_settings)
    bpy.utils.unregister_class(Cameraide_settings_3dview)
    bpy.utils.unregister_class(CAMERA_OT_render_selected_viewport)
    bpy.utils.unregister_class(CAMERA_OT_render_selected_normal)
    bpy.utils.unregister_class(CAMERA_OT_render_selected)
    bpy.utils.unregister_class(CAMERA_OT_toggle_custom_settings)
    bpy.utils.unregister_class(CAMERA_OT_toggle_frame_range_sync)
    bpy.utils.unregister_class(CAMERA_OT_swap_resolution)
    del bpy.types.Camera.cameraide_settings
    
    # Remove handler for active camera change
    bpy.app.handlers.depsgraph_update_post.remove(on_active_camera_changed)

if __name__ == "__main__":
    register()