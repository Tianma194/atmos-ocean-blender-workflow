# SPDX-License-Identifier: GPL-3.0-or-later
from pathlib import Path
import importlib
import runpy
import sys
import bpy


def open_case():
    if not bpy.data.filepath:
        raise RuntimeError('Open a saved case scene first.')
    root = Path(bpy.data.filepath).resolve().parent
    if not (root / 'config.py').is_file():
        raise FileNotFoundError('The open scene needs a config.py beside it.')
    library = root / 'scripts'
    if library.resolve() != Path(__file__).resolve().parent:
        raise RuntimeError('Run the scripts belonging to the open project.')
    for name in ('project_save', 'scene_sync'):
        old = sys.modules.get(name)
        if old and Path(old.__file__).resolve().parent != library:
            del sys.modules[name]
        importlib.reload(importlib.import_module(name))
    config = runpy.run_path(str(root / 'config.py'))
    config['ROOT'] = root
    if bpy.context.scene.name != config['SCENE_NAME']:
        raise RuntimeError('Select the configured scene: ' + config['SCENE_NAME'])
    return root, config
