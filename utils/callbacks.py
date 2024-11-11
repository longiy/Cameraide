import bpy

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

def on_active_camera_changed(scene):
    if scene.camera and scene.camera.data.cameraide_settings.use_custom_settings:
        settings = scene.camera.data.cameraide_settings
        if settings.sync_frame_range:
            scene.frame_start = settings.frame_start
            scene.frame_end = settings.frame_end
    update_viewport_resolution(bpy.context)

def register():
    bpy.app.handlers.depsgraph_update_post.append(on_active_camera_changed)

def unregister():
    bpy.app.handlers.depsgraph_update_post.remove(on_active_camera_changed)