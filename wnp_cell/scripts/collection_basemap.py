# SPDX-License-Identifier: GPL-3.0-or-later
import bpy
import numpy as np
from collection_utils import replace_mesh
from terrain_smoothing import smooth_elevation

def split_coast(vertices, heights, faces):
    values = heights[faces]
    land = faces[(values >= 0).all(axis=1)].tolist()
    sea = faces[(values <= 0).all(axis=1) & (values < 0).any(axis=1)].tolist()
    crossing = faces[(values < 0).any(axis=1) & (values > 0).any(axis=1)]
    points = vertices.tolist()
    levels = heights.tolist()
    edge_points = {}
    for triangle in crossing:
        for sign, target in ((1, land), (-1, sea)):
            polygon = []
            for first, second in zip(triangle, np.roll(triangle, -1)):
                h1, h2 = (heights[first], heights[second])
                if sign * h1 >= 0:
                    polygon.append(int(first))
                if h1 * h2 < 0:
                    edge = tuple(sorted((int(first), int(second))))
                    if edge not in edge_points:
                        t = h1 / (h1 - h2)
                        point = vertices[first] + t * (vertices[second] - vertices[first])
                        point[2] = 0.0
                        edge_points[edge] = len(points)
                        points.append(point.tolist())
                        levels.append(0.0)
                    polygon.append(edge_points[edge])
            for i in range(1, len(polygon) - 1):
                target.append((polygon[0], polygon[i], polygon[i + 1]))
    return (np.asarray(points), np.asarray(levels), (np.asarray(land), np.asarray(sea)))

def relief_material(name, cfg):
    mat = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    mat.use_nodes = True
    nodes, links = (mat.node_tree.nodes, mat.node_tree.links)
    if not nodes.get('ReliefSurface'):
        shader = nodes.new('ShaderNodeBsdfPrincipled')
        shader.name = 'ReliefSurface'
        output = nodes.get('Material Output') or nodes.new('ShaderNodeOutputMaterial')
        links.new(shader.outputs[0], output.inputs['Surface'])
    from height_colors import apply
    apply(mat, nodes['ReliefSurface'], cfg, 'source_elevation')
    nodes['ReliefSurface'].inputs['Roughness'].default_value = cfg['roughness']
    return mat

def build_basemap(config, land, seabed):
    cfg = config['TERRAIN']
    region = config['REGION']
    stride = cfg['grid_stride']
    with np.load(config['ROOT'] / config['ASSETS']['terrain']) as data:
        shape = data['elevation'].shape
        rows = np.unique(np.r_[np.arange(0, shape[0], stride), shape[0] - 1])
        cols = np.unique(np.r_[np.arange(0, shape[1], stride), shape[1] - 1])
        ix = np.ix_(rows, cols)
        h, lon, lat = (data[k][ix] for k in ('elevation', 'node_lon', 'node_lat'))
    land_h, _ = smooth_elevation(h, cfg['land']['smoothing'])
    sea_h, _ = smooth_elevation(-h, cfg['seabed']['smoothing'])
    z = np.where(h >= 0, land_h * cfg['land']['height_scale'], -sea_h * cfg['seabed']['depth_scale'])
    x = (lon - region['origin_lonlat'][0]) * region['xy_scale']
    y = (lat - region['origin_lonlat'][1]) * region['xy_scale'] * region['y_stretch']
    vertices = np.column_stack((x.ravel(), y.ravel(), z.ravel()))
    ids = np.arange(h.size).reshape(h.shape)
    a, b, c, d = (v.ravel() for v in (ids[:-1, :-1], ids[:-1, 1:], ids[1:, :-1], ids[1:, 1:]))
    faces = np.concatenate((np.column_stack((a, b, d)), np.column_stack((a, d, c))))
    faces = faces[np.isfinite(h.ravel()[faces]).all(axis=1)]
    points, levels, parts = split_coast(vertices, h.ravel(), faces)
    points[:, 2] += cfg['sea_level_scene']
    for obj, triangles, style in zip((land, seabed), parts, ('land', 'seabed')):
        used, inverse = np.unique(triangles, return_inverse=True)
        replace_mesh(obj.name, points[used], inverse.reshape(-1, 3), obj.users_collection[0])
        attr = obj.data.attributes.new('source_elevation', 'FLOAT', 'POINT')
        attr.data.foreach_set('value', levels[used])
        obj.data.polygons.foreach_set('use_smooth', np.ones(len(triangles), dtype=bool))
    print('Land and seabed updated')
