import bpy
from bpy.types import Operator


class CAMERAIDE_OT_remove_camera(Operator):
    """Remove camera from Cameraide (disable custom settings)"""
    bl_idname = "cameraide.remove_camera"
    bl_label = "Remove Camera"
    bl_options = {'REGISTER', 'UNDO'}
    
    camera_name: bpy.props.StringProperty()
    
    def execute(self, context):
        camera_obj = context.scene.objects.get(self.camera_name)
        if camera_obj and camera_obj.type == 'CAMERA':
            camera_obj.data.cameraide_settings.use_custom_settings = False
            
            from ..utils.callbacks import update_camera_name
            update_camera_name(camera_obj, False)
            
        return {'FINISHED'}


class CAMERAIDE_OT_add_camera(Operator):
    """Add camera to Cameraide (enable custom settings)"""
    bl_idname = "cameraide.add_camera"
    bl_label = "Add Camera"
    bl_options = {'REGISTER', 'UNDO'}
    
    camera_name: bpy.props.StringProperty()
    
    def execute(self, context):
        camera_obj = context.scene.objects.get(self.camera_name)
        if camera_obj and camera_obj.type == 'CAMERA':
            camera_obj.data.cameraide_settings.use_custom_settings = True
            
            from ..utils.callbacks import update_camera_name
            update_camera_name(camera_obj, True)
            
        return {'FINISHED'}


class CAMERAIDE_OT_select_camera(Operator):
    """Select and make camera active"""
    bl_idname = "cameraide.select_camera"
    bl_label = "Select Camera"
    bl_options = {'REGISTER', 'UNDO'}
    
    camera_name: bpy.props.StringProperty()
    
    def execute(self, context):
        camera_obj = context.scene.objects.get(self.camera_name)
        if camera_obj and camera_obj.type == 'CAMERA':
            bpy.ops.object.select_all(action='DESELECT')
            camera_obj.select_set(True)
            context.view_layer.objects.active = camera_obj
            context.scene.camera = camera_obj
            
        return {'FINISHED'}