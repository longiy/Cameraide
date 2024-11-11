import bpy

def update_viewport_resolution(context):
    """Update the viewport resolution based on active camera settings"""
    if context.scene.camera and context.scene.camera.data.cameraide_settings.use_custom_settings:
        settings = context.scene.camera.data.cameraide_settings
        # Update render resolution settings
        context.scene.render.resolution_x = settings.resolution_x
        context.scene.render.resolution_y = settings.resolution_y
        context.scene.render.resolution_percentage = settings.resolution_percentage
        
        # Force viewport update
        for area in context.screen.areas:
            if area.type == 'VIEW_3D':
                for region in area.regions:
                    if region.type == 'WINDOW':
                        region.tag_redraw()

def on_active_camera_changed(scene):
    if scene.camera and scene.camera.data.cameraide_settings.use_custom_settings:
        settings = scene.camera.data.cameraide_settings
        if settings.sync_frame_range:
            # Force update both values to ensure sync
            scene.frame_start = settings.frame_start
            scene.frame_end = settings.frame_end
            
            # Add a small delay before updating viewports
            def delayed_update():
                for area in bpy.context.screen.areas:
                    if area.type == 'VIEW_3D':
                        area.tag_redraw()
            
            bpy.app.timers.register(delayed_update, first_interval=0.1)
    
    update_viewport_resolution(bpy.context)

def on_frame_change(scene):
    if scene.camera and scene.camera.data.cameraide_settings.use_custom_settings:
        settings = scene.camera.data.cameraide_settings
        if settings.sync_frame_range:
            if scene.frame_start != settings.frame_start:
                settings.frame_start = scene.frame_start
            if scene.frame_end != settings.frame_end:
                settings.frame_end = scene.frame_end

def register():
    bpy.app.handlers.depsgraph_update_post.append(on_active_camera_changed)
    bpy.app.handlers.frame_change_post.append(on_frame_change)

def unregister():
    bpy.app.handlers.depsgraph_update_post.remove(on_active_camera_changed)
    bpy.app.handlers.frame_change_post.remove(on_frame_change)

__all__ = ['update_viewport_resolution', 'on_active_camera_changed', 'on_frame_change']