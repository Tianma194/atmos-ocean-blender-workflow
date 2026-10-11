# SPDX-License-Identifier: GPL-3.0-or-later
import hashlib
import os
import json
from pathlib import Path
import bpy
import numpy as np
from png_layout import read_layout, image_bounds
from collection_utils import replace_mesh
from collection_basemap import build_basemap, relief_material

def validate(config):
    paths = {key: (config['ROOT'] / name).resolve() for key, name in config['ASSETS'].items()}
    for path in paths.values():
        if not path.is_file():
            raise FileNotFoundError(path)
    layout = read_layout(paths['humidity'])
    region = config['REGION']
    if not np.allclose(layout['extent'], region['extent']):
        raise ValueError('PNG/config extent mismatch')
    with np.load(paths['terrain']) as data:
        if not np.allclose([data['lon'][0], data['lon'][-1], data['lat'][0], data['lat'][-1]], region['extent']):
            raise ValueError('Terrain/config extent mismatch')
    t = config['TERRAIN']
    o = config['OCEAN']
    h = config['ATMOSPHERE']['humidity']
    if not isinstance(t['grid_stride'], int) or t['grid_stride'] < 1:
        raise ValueError('grid_stride must be a positive integer')
    if min(t['land']['height_scale'], t['seabed']['depth_scale']) <= 0:
        raise ValueError('Relief scales must be positive')
    if not 0 <= o['opacity'] <= 1 or not 0 <= h['opacity'] <= 1:
        raise ValueError('Opacity must be in [0, 1]')
    if min(o['waves']['wavelength_scene'], o['waves']['shore_fade_depth_m']) <= 0:
        raise ValueError('Wave length and shore fade depth must be positive')
    for style in ('land', 'seabed'):
        stops = t[style]['colors_m']
        if len(stops) < 2 or stops[-1][0] <= 0 or any((a[0] >= b[0] for a, b in zip(stops, stops[1:]))):
            raise ValueError('Relief color heights must increase')
    return (paths, layout)

def collection(key, name, parent):
    found = next((c for c in bpy.data.collections if c.get('workflow_id') == key), None)
    if found is None:
        found = bpy.data.collections.new(name)
        found['workflow_id'] = key
        parent.children.link(found)
    return found

def mesh_object(key, name, owner):
    found = next((o for o in bpy.context.scene.objects if o.get('workflow_id') == key), None)
    if found is None:
        found = bpy.data.objects.new(name, bpy.data.meshes.new(name + 'Mesh'))
        found['workflow_id'] = key
        owner.objects.link(found)
    return found

def visible(obj, enabled):
    obj.hide_viewport = not enabled
    obj.hide_render = not enabled

def ocean_material(cfg):
    mat = bpy.data.materials.get('Ocean Surface') or bpy.data.materials.new('Ocean Surface')
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    if not nodes.get('OceanOpacity'):
        nodes.clear()
        shader = nodes.new('ShaderNodeBsdfPrincipled')
        shader.name = 'OceanShader'
        transparent = nodes.new('ShaderNodeBsdfTransparent')
        mix = nodes.new('ShaderNodeMixShader')
        mix.name = 'OceanOpacity'
        output = nodes.new('ShaderNodeOutputMaterial')
        links.new(transparent.outputs[0], mix.inputs[1])
        links.new(shader.outputs[0], mix.inputs[2])
        links.new(mix.outputs[0], output.inputs['Surface'])
    shader = nodes['OceanShader']
    for socket, key in [('Roughness', 'roughness'), ('IOR', 'ior')]:
        shader.inputs[socket].default_value = cfg[key]
    from height_colors import apply
    apply(mat, shader, cfg, 'source_elevation')
    nodes['OceanOpacity'].inputs[0].default_value = cfg['opacity']
    return mat

def update_ocean(obj, seabed, cfg, sea_level):
    points = np.empty((len(seabed.data.vertices), 3), dtype=np.float32)
    seabed.data.vertices.foreach_get('co', points.ravel())
    depth = np.empty(len(points))
    seabed.data.attributes['source_elevation'].data.foreach_get('value', depth)
    waves = cfg['waves']
    angle = np.deg2rad(waves['direction_deg'])
    along = points[:, 0] * np.cos(angle) + points[:, 1] * np.sin(angle)
    cross = -points[:, 0] * np.sin(angle) + points[:, 1] * np.cos(angle)
    phase = 2 * np.pi * along / waves['wavelength_scene'] + waves['phase']
    fade = np.clip(-depth / waves['shore_fade_depth_m'], 0, 1)
    points[:, 2] = sea_level + cfg['height_offset_scene'] + waves['amplitude_scene'] * fade * (0.75 * np.sin(phase) + 0.25 * np.sin(phase * 1.7 + cross * 3))
    indices = np.empty(len(seabed.data.loops), dtype=np.int32)
    seabed.data.loops.foreach_get('vertex_index', indices)
    replace_mesh(obj.name, points, indices.reshape(-1, 3), obj.users_collection[0])
    obj.data.polygons.foreach_set('use_smooth', np.ones(len(indices) // 3, dtype=bool))
    visible(obj, cfg['enabled'])

def update_humidity(obj, paths, layout, config):
    cfg = config['ATMOSPHERE']['humidity']
    r = config['REGION']
    w, e, s, n = r['extent']
    ox, oy = r['origin_lonlat']
    scale = r['xy_scale']
    stretch = r['y_stretch']
    geo = dict(x0=(w - ox) * scale, x1=(e - ox) * scale, y0=(s - oy) * scale * stretch, y1=(n - oy) * scale * stretch)
    x0, x1, y0, y1 = image_bounds(geo, layout['axes_rect'])
    if len(obj.data.vertices) != 4:
        raise ValueError('Humidity canvas needs four vertices')
    for vertex, co in zip(obj.data.vertices, [(x0, y0, 0), (x1, y0, 0), (x1, y1, 0), (x0, y1, 0)]):
        vertex.co = co
    obj.location.z = config['TERRAIN']['sea_level_scene'] + cfg['height_offset_scene']
    uv = obj.data.uv_layers.get('ScientificCanvasUV') or obj.data.uv_layers.new(name='ScientificCanvasUV')
    for loop in obj.data.loops:
        uv.data[loop.index].uv = [(0, 0), (1, 0), (1, 1), (0, 1)][loop.vertex_index]
    visible(obj, cfg['enabled'])
    if not cfg['update_materials']:
        return
    mat = bpy.data.materials.get('Humidity Overlay') or bpy.data.materials.new('Humidity Overlay')
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    if not nodes.get('HumidityTexture'):
        nodes.clear()
        tex = nodes.new('ShaderNodeTexImage')
        tex.name = 'HumidityTexture'
        tex['workflow_map_texture'] = True
        uvnode = nodes.new('ShaderNodeUVMap')
        uvnode.uv_map = 'ScientificCanvasUV'
        links.new(uvnode.outputs[0], tex.inputs['Vector'])
        emission = nodes.new('ShaderNodeEmission')
        emission.name = 'HumidityEmission'
        transparent = nodes.new('ShaderNodeBsdfTransparent')
        opacity = nodes.new('ShaderNodeMath')
        opacity.operation = 'MULTIPLY'
        opacity.name = 'HumidityOpacity'
        mix = nodes.new('ShaderNodeMixShader')
        output = nodes.new('ShaderNodeOutputMaterial')
        links.new(tex.outputs['Color'], emission.inputs['Color'])
        links.new(tex.outputs['Alpha'], opacity.inputs[0])
        links.new(opacity.outputs[0], mix.inputs[0])
        links.new(transparent.outputs[0], mix.inputs[1])
        links.new(emission.outputs[0], mix.inputs[2])
        links.new(mix.outputs[0], output.inputs['Surface'])
    tex = nodes['HumidityTexture']
    if cfg['update_texture'] or tex.image is None:
        tex.image = bpy.data.images.load(str(paths['humidity']), check_existing=True)
        tex.image.colorspace_settings.name = 'sRGB'
        tex.image.filepath = '//' + os.path.relpath(paths['humidity'], config['ROOT'])
    nodes['HumidityOpacity'].inputs[1].default_value = cfg['opacity']
    nodes['HumidityEmission'].inputs['Strength'].default_value = cfg['emission_strength']
    obj.data.materials.clear()
    obj.data.materials.append(mat)
    visible(obj, cfg['enabled'])
    obj.data.update()

def refresh(config):
    from scene_sync import resolve
    paths, layout = validate(config)
    root = next((c for c in bpy.data.collections if c.get('workflow_id') == 'scene_content'))
    map_col = next((c for c in bpy.data.collections if c.get('workflow_id') == 'map'))
    ocean_col = collection('ocean', 'Ocean', map_col)
    air = collection('atmosphere', 'Atmosphere', root)
    for key in ('specific_humidity', 'wnp_cell', 'qbwo_wet', 'qbwo_dry', 'background_flow'):
        child = next((c for c in bpy.data.collections if c.get('workflow_id') == key))
        if child.name not in air.children:
            for parent in bpy.data.collections:
                if parent != air and child.name in parent.children:
                    parent.children.unlink(child)
            air.children.link(child)
    air.hide_viewport = not config['ATMOSPHERE']['enabled']
    air.hide_render = air.hide_viewport
    land = resolve('map_terrain')
    seabed = mesh_object('map_seabed', 'Seabed', ocean_col)
    surface = mesh_object('map_ocean', 'Ocean Surface', ocean_col)
    t = config['TERRAIN']
    geometry = (config['REGION'], t['grid_stride'], t['sea_level_scene'], t['land']['height_scale'], t['land']['smoothing'], t['seabed']['depth_scale'], t['seabed']['smoothing'])
    signature = hashlib.sha256(paths['terrain'].read_bytes() + json.dumps(geometry, sort_keys=True).encode()).hexdigest()
    if t['update_geometry'] and (land.get('workflow_generated_source') != signature or not len(seabed.data.vertices)):
        build_basemap(config, land, seabed)
        land['workflow_generated_source'] = signature
    for obj, style in ((land, 'land'), (seabed, 'seabed')):
        if t['update_materials']:
            mat = relief_material('Terrain ' + style, t[style])
            obj.data.materials.clear()
            obj.data.materials.append(mat)
        visible(obj, t[style]['enabled'])
    ocean_geometry = (land.get('workflow_generated_source'), config['OCEAN']['height_offset_scene'], config['OCEAN']['waves'], t['sea_level_scene'])
    ocean_signature = hashlib.sha256(json.dumps(ocean_geometry, sort_keys=True).encode()).hexdigest()
    if config['OCEAN']['update_geometry'] and (surface.get('workflow_generated_source') != ocean_signature or not len(surface.data.vertices)):
        update_ocean(surface, seabed, config['OCEAN'], t['sea_level_scene'])
        surface['workflow_generated_source'] = ocean_signature
    attr = surface.data.attributes.get('source_elevation') or surface.data.attributes.new('source_elevation', 'FLOAT', 'POINT')
    depths = np.empty(len(seabed.data.vertices))
    seabed.data.attributes['source_elevation'].data.foreach_get('value', depths)
    if len(surface.data.vertices) == len(depths):
        attr.data.foreach_set('value', depths)
    if config['OCEAN']['update_materials']:
        surface.data.materials.clear()
        surface.data.materials.append(ocean_material(config['OCEAN']))
    visible(surface, config['OCEAN']['enabled'])
    from collection_ocean_body import update as update_body
    body = mesh_object('map_ocean_body', 'Ocean Body', ocean_col)
    update_body(body, seabed, config)
    update_humidity(resolve('map_humidity'), paths, layout, config)
    resolve('wet_cloud').data.filepath = '//' + os.path.relpath(paths['wet_cloud'], config['ROOT'])
    bpy.context.view_layer.update()

def snapshot(config):
    from scene_sync import resolve
    values = {'TERRAIN': {}, 'OCEAN': {}, 'ATMOSPHERE': {}}
    from height_colors import read
    for key, style in (('map_terrain', 'land'), ('map_seabed', 'seabed')):
        if not config['TERRAIN']['update_materials']:
            continue
        obj = resolve(key)
        nodes = obj.data.materials[0].node_tree.nodes
        from height_colors import read
        values['TERRAIN'][style] = {'enabled': not obj.hide_render, 'roughness': nodes['ReliefSurface'].inputs['Roughness'].default_value, **read(obj.data.materials[0])}
    if config['OCEAN']['update_materials']:
        obj = resolve('map_ocean')
        nodes = obj.data.materials[0].node_tree.nodes
        values['OCEAN'] = {'enabled': not obj.hide_render, 'opacity': nodes['OceanOpacity'].inputs[0].default_value, 'roughness': nodes['OceanShader'].inputs['Roughness'].default_value, 'ior': nodes['OceanShader'].inputs['IOR'].default_value}
        values['OCEAN'].update(read(obj.data.materials[0]))
        from collection_ocean_body import snapshot as body_snapshot
        values['OCEAN']['body'] = body_snapshot(resolve('map_ocean_body'))
    obj = resolve('map_humidity')
    air = next((c for c in bpy.data.collections if c.get('workflow_id') == 'atmosphere'))
    if config['ATMOSPHERE']['humidity']['update_materials']:
        nodes = obj.data.materials[0].node_tree.nodes
        values['ATMOSPHERE'] = {'enabled': not air.hide_render, 'humidity': {'enabled': not obj.hide_render, 'height_offset_scene': obj.location.z - config['TERRAIN']['sea_level_scene'], 'opacity': nodes['HumidityOpacity'].inputs[1].default_value, 'emission_strength': nodes['HumidityEmission'].inputs['Strength'].default_value}}
    return values
