# SPDX-License-Identifier: GPL-3.0-or-later
from pathlib import Path
import importlib
import sys
import bpy

if not bpy.data.filepath:
    raise RuntimeError('Open a case scene before running this script.')
library = Path(bpy.data.filepath).resolve().parent / 'scripts'
sys.dont_write_bytecode = True
if str(library) in sys.path:
    sys.path.remove(str(library))
sys.path.insert(0, str(library))
old = sys.modules.get('project_context')
if old and Path(old.__file__).resolve().parent != library:
    del sys.modules['project_context']
import project_context
importlib.reload(project_context)
root, config = project_context.open_case()

import runpy
import scene_sync

assets = None
if config.get('ASSET_SCRIPT'):
    path = (root / config['ASSET_SCRIPT']).resolve()
    if not path.is_relative_to(root):
        raise ValueError('ASSET_SCRIPT must belong to this case.')
    assets = runpy.run_path(str(path))
    assets['validate'](config)
scene_sync.snapshot(config)
scene_sync.apply(config)
if assets:
    assets['refresh'](config)
print('Case configuration applied. Save when ready.')
