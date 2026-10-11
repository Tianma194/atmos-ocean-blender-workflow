# SPDX-License-Identifier: GPL-3.0-or-later
from pathlib import Path
import os
import bpy


def prepare(root):
    root = Path(root).resolve()
    if Path(bpy.data.filepath).resolve().parent != root:
        raise RuntimeError('Save only the currently open case.')
    for blocks in (bpy.data.images, bpy.data.volumes):
        for block in blocks:
            if not block.filepath or getattr(block, 'packed_file', None):
                continue
            path = Path(bpy.path.abspath(block.filepath)).resolve()
            if not path.is_relative_to(root) or not path.is_file():
                raise FileNotFoundError('External asset must exist inside the project: ' + str(path))
            block.filepath = '//' + os.path.relpath(path, root)
    for name in ('load_scene.py', 'sync_scene.py', 'save_scene.py'):
        text = bpy.data.texts.get(name) or bpy.data.texts.new(name)
        text.clear()
        text.write((root / name).read_text())
        text.filepath = '//' + name
    text = bpy.data.texts.get('config.py') or bpy.data.texts.new('config.py')
    text.clear()
    text.write((root / 'config.py').read_text())
    text.filepath = '//config.py'
    bpy.context.scene.render.filepath = '//renders/scene.png'
    return root


def save(root):
    prepare(root)
    bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath)
