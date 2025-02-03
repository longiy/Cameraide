# In panels/__init__.py
from .sidebar_panel import register as register_sidebar_panel, unregister as unregister_sidebar_panel

def register():

    register_sidebar_panel()

def unregister():
    unregister_sidebar_panel()
