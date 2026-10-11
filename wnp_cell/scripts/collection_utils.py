# SPDX-License-Identifier: GPL-3.0-or-later
import bpy
import numpy as np

def ensure_collection(parent, name):
    value = next((c for c in parent.children if c.get("content_id") == name), None) or parent.children.get(name)
    if value is None:
        value = bpy.data.collections.new(name)
        parent.children.link(value)
    value["content_id"] = name
    return value


def replace_mesh(name, vertices, faces, owner):
    obj = next((o for o in owner.objects if o.get("content_id") == name), None) or owner.objects.get(name)
    mesh = bpy.data.meshes.new(name + 'Mesh')
    if obj is None:
        obj = bpy.data.objects.new(name, mesh)
        owner.objects.link(obj)
    else:
        old = obj.data
        for material in old.materials:
            mesh.materials.append(material)
        obj.data = mesh
        if old.users == 0:
            bpy.data.meshes.remove(old)
    obj["content_id"] = name
    obj.location = (0, 0, 0)
    obj.rotation_euler = (0, 0, 0)
    obj.scale = (1, 1, 1)
    mesh.vertices.add(len(vertices))
    mesh.vertices.foreach_set('co', np.asarray(vertices, dtype=np.float32).ravel())
    faces = np.asarray(faces, dtype=np.int32)
    mesh.loops.add(faces.size)
    mesh.loops.foreach_set('vertex_index', faces.ravel())
    mesh.polygons.add(len(faces))
    mesh.polygons.foreach_set('loop_start', np.arange(len(faces), dtype=np.int32) * faces.shape[1])
    mesh.polygons.foreach_set('loop_total', np.full(len(faces), faces.shape[1], dtype=np.int32))
    mesh.update()
    return obj
