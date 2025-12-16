"""Operators package for Cameraide"""
from . import camera
from . import resolution
from . import resolution_presets
from . import render_snapshot
from . import render_playblast
from . import render_batch


def register():
    camera.register()
    resolution.register()
    resolution_presets.register()
    render_snapshot.register()
    render_playblast.register()
    render_batch.register()


def unregister():
    render_batch.unregister()
    render_playblast.unregister()
    render_snapshot.unregister()
    resolution_presets.unregister()
    resolution.unregister()
    camera.unregister()