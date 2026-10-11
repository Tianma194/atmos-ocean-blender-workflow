# SPDX-License-Identifier: GPL-3.0-or-later
import hashlib
import json
import bpy
import numpy as np
from collection_utils import replace_mesh

def material(name, cfg):
    mat = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    mat.use_nodes = True
    nodes, links = (mat.node_tree.nodes, mat.node_tree.links)
    if not nodes.get('BodyOpacity'):
        nodes.clear()
        shader = nodes.new('ShaderNodeBsdfPrincipled')
        shader.name = 'BodyShader'
        transparent = nodes.new('ShaderNodeBsdfTransparent')
        mix = nodes.new('ShaderNodeMixShader')
        mix.name = 'BodyOpacity'
        output = nodes.new('ShaderNodeOutputMaterial')
        links.new(transparent.outputs[0], mix.inputs[1])
        links.new(shader.outputs[0], mix.inputs[2])
        links.new(mix.outputs[0], output.inputs['Surface'])
    if 'color' in cfg:
        nodes['BodyShader'].inputs['Base Color'].default_value = cfg['color']
    nodes['BodyShader'].inputs['Roughness'].default_value = cfg['roughness']
    nodes['BodyShader'].inputs['Emission Strength'].default_value = 0
    if 'colors_scene' in cfg:
        from height_colors import apply
        apply(mat, nodes['BodyShader'], cfg, 'water_depth')
    nodes['BodyOpacity'].inputs[0].default_value = cfg['opacity']
    return mat

def update(obj, seabed, config):
    cfg = config['OCEAN']['body']
    r = config['REGION']
    if cfg['min_depth_scene'] <= 0 or cfg['bottom_clearance_scene'] < 0:
        raise ValueError('Body depth must be positive and clearance nonnegative')
    for key in ('walls', 'bottom'):
        if not 0 <= cfg[key]['opacity'] <= 1:
            raise ValueError('Body opacity must be in [0, 1]')
    w, e, s, n = r['extent']
    ox, oy = r['origin_lonlat']
    scale = r['xy_scale']
    stretch = r['y_stretch']
    x0, x1 = ((w - ox) * scale, (e - ox) * scale)
    y0, y1 = ((s - oy) * scale * stretch, (n - oy) * scale * stretch)
    top = config['TERRAIN']['sea_level_scene'] + config['OCEAN']['height_offset_scene']
    bottom = top - cfg['min_depth_scene']
    if cfg['fit_seabed'] and len(seabed.data.vertices):
        points = np.empty((len(seabed.data.vertices), 3))
        seabed.data.vertices.foreach_get('co', points.ravel())
        bottom = min(bottom, float(points[:, 2].min()) - cfg['bottom_clearance_scene'])
    signature = hashlib.sha256(json.dumps((x0, x1, y0, y1, top, bottom)).encode()).hexdigest()
    rebuild = config['OCEAN']['update_geometry'] and obj.get('workflow_generated_source') != signature
    if rebuild:
        vertices = [(x0, y0, bottom), (x1, y0, bottom), (x1, y1, bottom), (x0, y1, bottom), (x0, y0, top), (x1, y0, top), (x1, y1, top), (x0, y1, top)]
        faces = [(0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7), (3, 2, 1, 0)]
        replace_mesh(obj.name, vertices, faces, obj.users_collection[0])
        obj['workflow_generated_source'] = signature
        obj['display_depth'] = top - bottom
    attr = obj.data.attributes.get('water_depth') or obj.data.attributes.new('water_depth', 'FLOAT', 'POINT')
    attr.data.foreach_set('value', [max(0, top - v.co.z) for v in obj.data.vertices])
    if config['OCEAN']['update_materials']:
        for index, key in enumerate(('walls', 'bottom')):
            mat = material('Ocean Body ' + key, cfg[key])
            if len(obj.data.materials) <= index:
                obj.data.materials.append(mat)
            else:
                obj.data.materials[index] = mat
    if rebuild:
        obj.data.polygons[4].material_index = 1
    obj.hide_viewport = not (config['OCEAN']['enabled'] and cfg['enabled'])
    obj.hide_render = obj.hide_viewport

def snapshot(obj):
    result = {}
    for index, key in enumerate(('walls', 'bottom')):
        nodes = obj.data.materials[index].node_tree.nodes
        result[key] = {'color': tuple(nodes['BodyShader'].inputs['Base Color'].default_value), 'roughness': nodes['BodyShader'].inputs['Roughness'].default_value, 'opacity': nodes['BodyOpacity'].inputs[0].default_value}
        if nodes.get('HeightColors'):
            from height_colors import read
            result[key].pop('color', None)
            result[key].update(read(obj.data.materials[index]))
    return result
