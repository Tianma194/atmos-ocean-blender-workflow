# SPDX-License-Identifier: GPL-3.0-or-later
import bpy
from pathlib import Path
R=Path(__file__).resolve().parent
P='Full cloud / '
host=bpy.data.objects[P+'Block skeleton']
m=host.modifiers['Structure volume preview'];g=m.node_group

def socket(name,default,minimum,maximum):
    existing=next((s for s in g.interface.items_tree if s.name==name and getattr(s,'in_out',None)=='INPUT'),None)
    s=existing or g.interface.new_socket(name=name,in_out='INPUT',socket_type='NodeSocketFloat')
    s.default_value=default;s.min_value=minimum;s.max_value=maximum
    if existing is None:m[s.identifier]=default
    return s
socket('Detail strength',1.,0.,2.)
socket('Detail scale',1.,.4,3.)
socket('Fine detail',.7,0.,2.)
g.nodes.clear()
def node(typ,name):
    n=g.nodes.new(typ);n.name=name;n.label=name;return n

def wire(v,s):
    if isinstance(v,bpy.types.NodeSocket):g.links.new(v,s)
    else:s.default_value=v

def math(op,a,b=None,name=None):
    n=node('ShaderNodeMath',name or op);n.operation=op;wire(a,n.inputs[0])
    if b is not None:wire(b,n.inputs[1])
    return n.outputs[0]

def vec(op,a,b=None,name=None):
    n=node('ShaderNodeVectorMath',name or op);n.operation=op;wire(a,n.inputs[0])
    if b is not None:wire(b,n.inputs['Scale'] if op=='SCALE' else n.inputs[1])
    return n.outputs[0]

def noise(pos,scale,detail,name):
    n=node('ShaderNodeTexNoise',name);n.noise_dimensions='3D';n.inputs['Detail'].default_value=detail;n.inputs['Roughness'].default_value=.6
    wire(pos,n.inputs['Vector']);wire(scale,n.inputs['Scale']);return n
inp=node('NodeGroupInput','Editable cloud controls');out=node('NodeGroupOutput','Result')
position=node('GeometryNodeInputPosition','Local position').outputs[0]
strength=inp.outputs['Detail strength'];scale=inp.outputs['Detail scale']
fine=math('MULTIPLY',inp.outputs['Fine detail'],strength,'Fine amplitude')
sdf=node('GeometryNodeMeshToSDFGrid','Distance from editable scaffold')
wire(inp.outputs['Geometry'],sdf.inputs['Mesh']);sdf.inputs['Voxel Size'].default_value=.055;sdf.inputs['Band Width'].default_value=12
p=vec('MULTIPLY',position,(1.,1.,1.7),'Slightly flattened rolls')
warp=noise(p,math('MULTIPLY',scale,2.7),2.,'Fold distortion')
warp_vec=vec('SUBTRACT',warp.outputs['Color'],(.5,.5,.5))
query=vec('ADD',position,vec('SCALE',warp_vec,math('MULTIPLY',strength,.68)),'Warped scaffold sampling')
sample=node('GeometryNodeSampleGrid','Sample own signed distance');sample.data_type='FLOAT';wire(sdf.outputs[0],sample.inputs['Grid']);wire(query,sample.inputs['Position'])
vor=node('ShaderNodeTexVoronoi','Medium cauliflower rolls');vor.feature='SMOOTH_F1';vor.inputs['Smoothness'].default_value=.28
wire(vec('ADD',p,vec('SCALE',warp_vec,.24)),vor.inputs['Vector']);wire(math('MULTIPLY',scale,3.3),vor.inputs['Scale'])
rolls=math('MULTIPLY',math('SUBTRACT',vor.outputs['Distance'],.50),math('MULTIPLY',strength,.24))
small=noise(p,math('MULTIPLY',scale,15.),2.5,'Small turbulent folds')
ripple=math('MULTIPLY',math('SUBTRACT',small.outputs['Fac'],.50),math('MULTIPLY',fine,.19))
distance=math('ADD',math('ADD',sample.outputs[0],rolls),ripple,'Rolled surface distance')
ramp=node('ShaderNodeMapRange','Soft cloud boundary');ramp.interpolation_type='SMOOTHERSTEP';ramp.clamp=True
wire(distance,ramp.inputs['Value']);ramp.inputs['From Min'].default_value=-.075;ramp.inputs['From Max'].default_value=.012;ramp.inputs['To Min'].default_value=1.;ramp.inputs['To Max'].default_value=0.
modulation=math('ADD',math('MULTIPLY',math('SUBTRACT',small.outputs['Fac'],.5),math('MULTIPLY',strength,.85)),1.,'Uneven cloud density')
outer=node('ShaderNodeMapRange','Thin irregular edge wisps');outer.interpolation_type='SMOOTHERSTEP';outer.clamp=True
wire(distance,outer.inputs['Value']);outer.inputs['From Min'].default_value=-.03;outer.inputs['From Max'].default_value=.16;outer.inputs['To Min'].default_value=1.;outer.inputs['To Max'].default_value=0.
patch=math('POWER',math('MAXIMUM',math('MULTIPLY',math('SUBTRACT',small.outputs['Fac'],.40),3.),0.),2.)
wisps=math('MULTIPLY',math('MULTIPLY',outer.outputs[0],patch),math('MULTIPLY',strength,.13))
density=math('MULTIPLY',math('ADD',math('MULTIPLY',ramp.outputs[0],modulation),wisps),inp.outputs['Density multiplier'],'Scattering density')
bounds=node('GeometryNodeBoundBox','Adaptive bounds');wire(inp.outputs['Geometry'],bounds.inputs['Geometry'])
lo=vec('ADD',bounds.outputs['Min'],(-.55,-.55,-.55));hi=vec('ADD',bounds.outputs['Max'],(.55,.55,.55))
extent=vec('SUBTRACT',hi,lo);split=node('ShaderNodeSeparateXYZ','Dimensions');wire(extent,split.inputs[0])
volume=node('GeometryNodeVolumeCube','Native density volume');wire(density,volume.inputs['Density']);wire(lo,volume.inputs['Min']);wire(hi,volume.inputs['Max'])
for axis in 'XYZ':
    resolution=math('MAXIMUM',math('CEIL',math('DIVIDE',split.outputs[axis],inp.outputs['Voxel size'])),2.)
    wire(resolution,volume.inputs['Resolution '+axis])
material=node('GeometryNodeSetMaterial','Local editable scattering');material.inputs['Material'].default_value=bpy.data.materials[P+'Structure scattering'];wire(volume.outputs[0],material.inputs[0])
switch=node('GeometryNodeSwitch','Volume or scaffold');switch.input_type='GEOMETRY';wire(inp.outputs['Volume preview'],switch.inputs['Switch']);wire(inp.outputs['Geometry'],switch.inputs['False']);wire(material.outputs[0],switch.inputs['True']);wire(switch.outputs[0],out.inputs['Geometry'])
for i,n in enumerate(g.nodes):n.location=((i//8)*230,-(i%8)*165)
inp.location=(-420,100);out.location=(1850,100)
ids={s.name:s.identifier for s in g.interface.items_tree if getattr(s,'in_out',None)=='INPUT'}
m[ids['Volume preview']]=True;m[ids['Voxel size']]=.04
for interface in g.interface.items_tree:
    if getattr(interface,'in_out',None)=='INPUT' and interface.name in ('Volume preview','Voxel size'):
        interface.default_value=True if interface.name=='Volume preview' else .04
host['Detail revision']=2
host['Volume preview']='Native signed distance and multiscale density from the retained editable scaffold; no reference VDB sampled'
t=bpy.data.texts.get('refine_density.py') or bpy.data.texts.new('refine_density.py');t.clear();t.write(Path(__file__).read_text());t.use_fake_user=True
host.update_tag();bpy.context.view_layer.update()
print('NATIVE_DETAIL_READY',len(g.nodes),'nodes',flush=True)
