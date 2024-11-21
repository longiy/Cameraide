# In panels/__init__.py
from .main_panel import register as register_main_panel, unregister as unregister_main_panel
from .sidebar_panel import register as register_sidebar_panel, unregister as unregister_sidebar_panel

def register():
    register_main_panel()
    register_sidebar_panel()

def unregister():
    unregister_sidebar_panel()
    unregister_main_panel()