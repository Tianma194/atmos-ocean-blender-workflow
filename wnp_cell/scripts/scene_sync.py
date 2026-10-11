# SPDX-License-Identifier: GPL-3.0-or-later
import ast
import math
import os
from pathlib import Path
import bpy

OBJECT_ID = 'workflow_id'
COLOR_ID = 'workflow_color'

def objects(config):
    for group, entries in config['OBJECTS'].items():
        for key, settings in entries.items():
            yield group, key, settings


def resolve(key):
    found = [o for o in bpy.context.scene.objects if o.get(OBJECT_ID) == key]
    if len(found) != 1:
        raise ValueError(f'{key}: expected one identified object, found {len(found)}. Sync/register new objects first.')
    return found[0]


def color_sockets(obj):
    result = {}
    if not hasattr(obj.data, 'materials'):
        return result
    for slot, mat in enumerate(obj.data.materials):
        if not mat or not mat.use_nodes:
            continue
        tagged = [n for n in mat.node_tree.nodes if n.get(COLOR_ID)]
        if len(tagged) > 1:
            raise ValueError(f'{obj.name}: multiple color bindings in {mat.name}')
        if not tagged:
            continue
        node = tagged[0]
        name = 'Color' if node.type == 'PRINCIPLED_VOLUME' else 'Base Color'
        socket = node.inputs.get(name)
        if socket is None or socket.is_linked:
            raise ValueError(f'{obj.name}: managed color in {mat.name} now uses a different node setup; review binding before sync/load.')
        result[str(slot)] = socket
    return result


def rain_sockets(obj):
    result = {}
    for mod in obj.modifiers:
        if mod.type != 'NODES' or not mod.node_group:
            continue
        for item in mod.node_group.interface.items_tree:
            if item.item_type == 'SOCKET' and item.in_out == 'INPUT' and item.name in ('Count','Width','Depth','Height','Length','Radius','Seed'):
                result[item.name.lower()] = (mod, item.identifier)
    return result


def read_object(obj, template, region):
    result = {}
    if 'position' in template:
        result['position'] = tuple(obj.location)
    if 'position_lonlat_height' in template:
        if obj.parent:
            raise ValueError(f'{obj.name}: geographic positioning requires an unparented object')
        x,y,z = obj.location
        ox,oy = region['origin_lonlat']
        result['position_lonlat_height'] = (ox+x/region['xy_scale'], oy+y/(region['xy_scale']*region['y_stretch']), z)
    if obj.rotation_mode not in ('XYZ','XZY','YXZ','YZX','ZXY','ZYX'):
        raise ValueError(f'{obj.name}: quaternion/axis-angle rotation needs an explicit binding; preserved in blend')
    result.update(rotation_deg=tuple(math.degrees(v) for v in obj.rotation_euler), scale=tuple(obj.scale),
                  visible=not obj.hide_get(), viewport=not obj.hide_viewport, render=not obj.hide_render)
    if 'colors' in template:
        sockets = color_sockets(obj)
        for slot in template['colors']:
            if slot not in sockets:
                raise ValueError(f'{obj.name}: missing color binding for slot {slot}')
        result['colors'] = {slot:tuple(sockets[slot].default_value) for slot in template['colors']}
    if 'text' in template:
        result['text'] = obj.data.body
    if 'camera' in template:
        result['camera'] = {k:getattr(obj.data,k) for k in template['camera']}
    if 'light' in template:
        result['light'] = {k:tuple(getattr(obj.data,k)) if k=='color' else getattr(obj.data,k) for k in template['light']}
    if 'rain_color' in template:
        result['rain_color'] = tuple(rain_color(obj).default_value)
    if 'rain' in template:
        sockets = rain_sockets(obj)
        result['rain'] = {k:sockets[k][0][sockets[k][1]] for k in template['rain']}
    return result


def rain_color(obj):
    mats = [n.inputs['Material'].default_value for m in obj.modifiers if m.type == 'NODES' and m.node_group
            for n in m.node_group.nodes if n.type == 'SET_MATERIAL' and not n.inputs['Material'].is_linked]
    mats = [m for m in mats if m and m.use_nodes]
    sockets = [n.inputs['Base Color'] for m in mats for n in m.node_tree.nodes
               if n.type == 'BSDF_PRINCIPLED' and not n.inputs['Base Color'].is_linked]
    if len(sockets) != 1:raise ValueError('Rain material binding changed; review before load/sync')
    return sockets[0]


def read_scene(template):
    s=bpy.context.scene
    result={}
    for category, values in template.items():
        owner = s.render if category=='render' else s.cycles if category=='cycles' else s.view_settings
        result[category]={k:getattr(owner,k) for k in values}
    return result


def snapshot(config):
    result={'OBJECTS':{}, 'SCENE':read_scene(config['SCENE']), 'COLLECTIONS':{}}
    for group,key,settings in objects(config):
        result['OBJECTS'].setdefault(group,{})[key] = read_object(resolve(key),settings,config.get('REGION', {}))
    for key,settings in config['COLLECTIONS'].items():
        found=[c for c in bpy.data.collections if c.get(OBJECT_ID)==key]
        if len(found)!=1:raise ValueError(f'Missing/duplicate collection {key}')
        result['COLLECTIONS'][key]={'viewport':not found[0].hide_viewport,'render':not found[0].hide_render}
    return result


def equal(a,b):
    if isinstance(a,dict) and isinstance(b,dict):return a.keys()==b.keys() and all(equal(a[k],b[k]) for k in a)
    if isinstance(a,(list,tuple)) and isinstance(b,(list,tuple)):return len(a)==len(b) and all(equal(x,y) for x,y in zip(a,b))
    if isinstance(a,(int,float)) and not isinstance(a,bool) and isinstance(b,(int,float)) and not isinstance(b,bool):
        return math.isclose(a,b,rel_tol=1e-7,abs_tol=1e-6)
    return a==b


def apply(config):
    before=snapshot(config)  # Validate bindings before changing anything.
    def finite(value):
        if isinstance(value, dict):
            for v in value.values():finite(v)
        elif isinstance(value,(list,tuple)):
            for v in value:finite(v)
        elif isinstance(value,float) and not math.isfinite(value):raise ValueError('Non-finite config value')
    finite({k:config[k] for k in ('OBJECTS','SCENE')})
    for _,key,settings in objects(config):
        if any(abs(v)<1e-10 for v in settings['scale']):raise ValueError(f'{key}: zero scale')
    for group,key,settings in objects(config):
        obj=resolve(key)
        if 'position' in settings:obj.location=settings['position']
        else:
            lon,lat,z=settings['position_lonlat_height'];r=config.get('REGION', {});ox,oy=r['origin_lonlat']
            obj.location=((lon-ox)*r['xy_scale'],(lat-oy)*r['xy_scale']*r['y_stretch'],z)
        obj.rotation_euler=tuple(math.radians(v) for v in settings['rotation_deg'])
        obj.scale=settings['scale']
        obj.hide_set(not settings['visible']);obj.hide_viewport=not settings['viewport'];obj.hide_render=not settings['render']
        for slot,value in settings.get('colors',{}).items():color_sockets(obj)[slot].default_value=value
        if 'rain_color' in settings:rain_color(obj).default_value=settings['rain_color']
        if 'text' in settings:obj.data.body=settings['text']
        for category in ('camera','light'):
            for prop,value in settings.get(category,{}).items():setattr(obj.data,prop,value)
        for prop,value in settings.get('rain',{}).items():
            mod,socket=rain_sockets(obj)[prop];mod[socket]=value;obj.update_tag()
    for key,settings in config['COLLECTIONS'].items():
        c=next(c for c in bpy.data.collections if c.get(OBJECT_ID)==key)
        c.hide_viewport=not settings['viewport'];c.hide_render=not settings['render']
    s=bpy.context.scene
    for category,values in config['SCENE'].items():
        owner=s.render if category=='render' else s.cycles if category=='cycles' else s.view_settings
        for prop,value in values.items():setattr(owner,prop,value)
    bpy.context.view_layer.update()
    actual=snapshot(config)
    expected={k:config[k] for k in actual}
    if not equal(actual,expected):
        raise ValueError('Applied values differ from config (clamped value, shared material conflict or driven parameter). Inspect before saving.')
    return before


def literal(value):
    if isinstance(value, float):
        text=format(value, '.9g')
        return text if '.' in text or 'e' in text.lower() else text+'.0'
    if isinstance(value, (tuple,list)):
        content=', '.join(literal(v) for v in value)
        if isinstance(value,tuple):return '('+content+(',' if len(value)==1 else '')+')'
        return '['+content+']'
    return repr(value)


def patch_source(source, values):
    tree=ast.parse(source)
    lines=source.splitlines(keepends=True)
    edits=[];changes=[]
    def offset(lineno,col):
        return sum(len(x) for x in lines[:lineno-1])+len(lines[lineno-1].encode()[:col].decode())
    def visit(node,new,path):
        if isinstance(node,ast.Dict) and isinstance(new,dict):
            index={ast.literal_eval(k):v for k,v in zip(node.keys,node.values)}
            if not new.keys()<=index.keys():raise ValueError(f'{path}: config structure changed; register bindings first')
            for key,value in new.items():visit(index[key],value,f'{path}.{key}')
        else:
            old=ast.literal_eval(node)
            if not equal(old,new):
                edits.append((offset(node.lineno,node.col_offset),offset(node.end_lineno,node.end_col_offset),literal(new)))
                changes.append(f'{path}: {old!r} -> {new!r}')
    assignments={n.targets[0].id:n.value for n in tree.body if isinstance(n,ast.Assign) and len(n.targets)==1 and isinstance(n.targets[0],ast.Name)}
    for key,value in values.items():visit(assignments[key],value,key)
    for start,end,value in sorted(edits,reverse=True):source=source[:start]+value+source[end:]
    ast.parse(source)
    return source,changes


def sync(root, config, save=True):
    values=snapshot(config)
    if config.get('ASSET_SCRIPT'):
        import runpy
        adapter=runpy.run_path(str(Path(root)/config['ASSET_SCRIPT']))
        if 'snapshot' in adapter: values.update(adapter['snapshot'](config))
    path=Path(root)/'config.py';original=path.read_text()
    updated,changes=patch_source(original,values)
    known={key for _,key,_ in objects(config)}
    if config.get('ASSET_SCRIPT'):
        known.update(('map_terrain','map_seabed','map_ocean','map_ocean_body','map_humidity'))
    extras=[o.name for o in bpy.context.scene.objects if o.get(OBJECT_ID) not in known]
    tmp=path.with_suffix('.py.tmp')
    try:
        if updated!=original:
            tmp.write_text(updated);os.replace(tmp,path)
        if save:
            from project_save import save as save_project
            save_project(root)
    except Exception:
        path.write_text(original)
        raise
    finally:
        if tmp.exists():tmp.unlink()
    for change in changes:print(change)
    print(f'Synced {len(changes)} parameter changes; authored geometry/nodes retained in main blend.')
    if extras:print('Objects saved in blend but not configured (review/register if desired): '+', '.join(extras))
    return changes
