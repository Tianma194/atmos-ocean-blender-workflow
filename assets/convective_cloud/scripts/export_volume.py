# SPDX-License-Identifier: GPL-3.0-or-later
import bpy,sys,os,tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
source=ROOT/'cloud.blend'
assert bpy.app.background,'Use a disposable background Blender session'
assert Path(bpy.data.filepath).resolve()==source.resolve(),'Open the library source before exporting'
args=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else []
output=Path(args[args.index('--output')+1]).resolve() if '--output' in args else ROOT/'cache/cloud.vdb'
bpy.context.window.scene=bpy.data.scenes['Editable Cloud']
host=bpy.data.objects['Full cloud / Block skeleton']
def identifiers(mod):return {s.name:s.identifier for s in mod.node_group.interface.items_tree if getattr(s,'in_out',None)=='INPUT'}
main=host.modifiers['Main billow structure'];volume=host.modifiers['Structure volume preview']
main[identifiers(main)['Guide only']]=False;volume[identifiers(volume)['Volume preview']]=True
host.update_tag();bpy.context.view_layer.update()
ev=host.evaluated_get(bpy.context.evaluated_depsgraph_get());geometry=ev.evaluated_geometry();result=geometry.volume
assert result is not None and 'density' in result.grids
output.parent.mkdir(parents=True,exist_ok=True)
fd,name=tempfile.mkstemp(suffix='.vdb',prefix='.export_',dir=output.parent);os.close(fd)
try:
    result.grids.save(name)
    test=bpy.data.volumes.new('Export validation');test.filepath=name;test.grids.load()
    assert 'density' in test.grids and not test.grids.error_message
    bpy.data.volumes.remove(test)
    os.replace(name,output)
finally:
    if Path(name).exists():Path(name).unlink()
print('Volume exported:', output, flush=True)
