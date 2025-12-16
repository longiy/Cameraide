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
            
            from ..utils.camera_names import update_camera_name
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
            
            from ..utils.camera_names import update_camera_name
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
        if not camera_obj or camera_obj.type != 'CAMERA':
            return {'CANCELLED'}
        
        # Enable all parent collections to make object selectable
        self._enable_parent_collections(camera_obj, context)
        
        # Now select the camera
        bpy.ops.object.select_all(action='DESELECT')
        camera_obj.select_set(True)
        context.view_layer.objects.active = camera_obj
        context.scene.camera = camera_obj
        
        return {'FINISHED'}
    
    def _enable_parent_collections(self, obj, context):
        """Enable all parent collections of an object"""
        view_layer = context.view_layer
        
        # Find all parent collections
        def find_collections(obj, collections=None):
            if collections is None:
                collections = []
            for collection in bpy.data.collections:
                if obj.name in collection.objects:
                    collections.append(collection)
            return collections
        
        parent_collections = find_collections(obj)
        
        # Enable in view layer
        for collection in parent_collections:
            # Find the layer collection
            layer_collection = self._find_layer_collection(view_layer.layer_collection, collection)
            if layer_collection:
                layer_collection.exclude = False
                # Also enable viewport visibility
                collection.hide_viewport = False
    
    def _find_layer_collection(self, layer_collection, collection):
        """Recursively find layer collection by collection"""
        if layer_collection.collection == collection:
            return layer_collection
        for child in layer_collection.children:
            result = self._find_layer_collection(child, collection)
            if result:
                return result
        return None