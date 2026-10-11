# SPDX-License-Identifier: GPL-3.0-or-later
import math


def apply(mat, shader, cfg, attribute):
    nodes, links = mat.node_tree.nodes, mat.node_tree.links
    key = 'colors_m' if 'colors_m' in cfg else 'colors_scene'
    stops = cfg[key]
    if len(stops) < 2 or any(not math.isfinite(h) for h, _ in stops):
        raise ValueError('Provide at least two finite color-stop heights')
    if any(b[0] <= a[0] for a, b in zip(stops, stops[1:])):
        raise ValueError('Color-stop heights must increase')

    def node(kind, name, location):
        value = nodes.get(name) or nodes.new(kind)
        value.name = name
        value.location = location
        return value

    source = node('ShaderNodeAttribute', 'HeightSource', (-800, 100))
    source.attribute_name = attribute
    absolute = node('ShaderNodeMath', 'HeightAbsolute', (-580, 100))
    absolute.operation = 'ABSOLUTE'
    mapping = node('ShaderNodeMapRange', 'HeightRange', (-370, 100))
    mapping.clamp = True
    low, high = stops[0][0], stops[-1][0]
    for name, value in [('From Min', low), ('From Max', high), ('To Min', 0), ('To Max', 1)]:
        mapping.inputs[name].default_value = value
    ramp = node('ShaderNodeValToRGB', 'HeightColors', (-130, 100))
    ramp.width = 240
    ramp.color_ramp.interpolation = 'LINEAR'
    while len(ramp.color_ramp.elements) > len(stops):
        ramp.color_ramp.elements.remove(ramp.color_ramp.elements[-1])
    while len(ramp.color_ramp.elements) < len(stops):
        ramp.color_ramp.elements.new(0.5)
    for elem, (height, color) in zip(ramp.color_ramp.elements, stops):
        elem.position = (height-low)/(high-low)
        elem.color = color
    links.new(source.outputs['Fac'], absolute.inputs[0])
    links.new(absolute.outputs[0], mapping.inputs['Value'])
    links.new(mapping.outputs['Result'], ramp.inputs[0])
    links.new(ramp.outputs['Color'], shader.inputs['Base Color'])
    for link in list(shader.inputs['Emission Color'].links):
        if link.from_node.name in ('HeightMix', 'HeightColors'):
            links.remove(link)
    shader.inputs['Emission Strength'].default_value = 0
    for name in ('HeightGamma', 'HeightMix', 'ReliefColors', 'ReliefRange'):
        obsolete = nodes.get(name)
        if obsolete:
            upstream = [link.from_node for socket in obsolete.inputs for link in socket.links]
            nodes.remove(obsolete)
            while upstream:
                old = upstream.pop()
                if old.name.startswith('Height') or old.type not in ('MATH', 'ATTRIBUTE'):
                    continue
                if any(socket.is_linked for socket in old.outputs):
                    continue
                upstream.extend(link.from_node for socket in old.inputs for link in socket.links)
                nodes.remove(old)
    shader.location = (180, 100)
    for value in nodes:
        if value.type == 'OUTPUT_MATERIAL': value.location = (720, 100)
        if value.type == 'MIX_SHADER': value.location = (500, 100)
        if value.type == 'BSDF_TRANSPARENT': value.location = (190, -250)
    mat['color_stops_key'] = key


def read(mat):
    nodes = mat.node_tree.nodes
    low = nodes['HeightRange'].inputs['From Min'].default_value
    high = nodes['HeightRange'].inputs['From Max'].default_value
    stops = [(low+e.position*(high-low), tuple(e.color)) for e in nodes['HeightColors'].color_ramp.elements]
    return {mat['color_stops_key']: stops}
