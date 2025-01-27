# In operators/__init__.py
from .frame_range import register as register_frame_range, unregister as unregister_frame_range
from .file_output import register as register_file_output, unregister as unregister_file_output
from .render import (register as register_render, 
                    unregister as unregister_render,
                    CAMERA_OT_render_all_viewport,
                    CAMERA_OT_render_all_normal,
                    CAMERA_OT_render_all_normal,
                    CAMERA_OT_render_selected_viewport,
                    CAMERA_OT_render_selected_normal,
                    CameraRenderOperatorBase,)
from .resolution import register as register_resolution, unregister as unregister_resolution

def register():
    register_frame_range()
    register_file_output()
    register_render()
    register_resolution()

def unregister():
    unregister_resolution()
    unregister_render()
    unregister_file_output()
    unregister_frame_range()