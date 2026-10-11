# SPDX-License-Identifier: GPL-3.0-or-later
import ast
import struct


def read_layout(path):
    result = {}
    with open(path,'rb') as handle:
        if handle.read(8) != b'\x89PNG\r\n\x1a\n':
            raise ValueError(f'Not a PNG: {path}')
        while True:
            header = handle.read(8)
            if len(header) != 8:
                break
            size,kind = struct.unpack('>I4s',header)
            payload = handle.read(size)
            handle.read(4)  # Chunk checksum; Blender also decodes the image itself.
            if kind == b'IHDR':
                result['size'] = struct.unpack('>II',payload[:8])
            elif kind == b'tEXt':
                key,_,value = payload.partition(b'\0')
                prefix = next((p for p in (b'workflow_', b'fig3_') if key.startswith(p)), None)
                if prefix:
                    result[key[len(prefix):].decode('latin1')] = ast.literal_eval(value.decode('latin1'))
            elif kind == b'IEND':
                break
    return result


def image_bounds(geo, rect):
    left,bottom,width,height = rect
    if width <= 0 or height <= 0:
        raise ValueError('Invalid scientific plotting rectangle')
    dx = (geo['x1']-geo['x0'])/width
    dy = (geo['y1']-geo['y0'])/height
    x0 = geo['x0']-left*dx
    y0 = geo['y0']-bottom*dy
    return x0,x0+dx,y0,y0+dy
