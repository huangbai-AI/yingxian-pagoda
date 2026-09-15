import bpy,math,json,random
import numpy as np
from pathlib import Path
from mathutils import Vector
from collections import defaultdict
ROOT=Path(__file__).resolve().parent.parent
s=bpy.context.scene;s.frame_set(1)
assert not s.get('refined_v17')
source=(ROOT/'model/重建模型.py').read_text();buckets={};parts=defaultdict(int)
exec(source[source.index('def geo('):source.index('# Square stepped base')],globals())
# Work only on the first-storey enclosure; upper-storey geometry remains untouched.
original={o.name:len(o.data.vertices) for o in s.objects if o.type=='MESH' and o.parent and o.parent.name not in ['Level_0','Level_1']}
N=1024;rng=np.random.default_rng(1056)
y,x=np.mgrid[0:N,0:N].astype(np.float32)/N
field=np.zeros((N,N),dtype=np.float32)
for f,amp in [(2,.38),(5,.22),(13,.12),(37,.055),(111,.024)]:
 for j in range(4):
  a=rng.uniform(0,6.28);p=rng.uniform(0,6.28)
  field+=np.sin((x*np.cos(a)+y*np.sin(a))*f*6.28+p)*amp/4
fine=rng.normal(0,.022,(N,N));height=field+fine
# Mottled ochre plaster, a little aggregate exposed, darkened near the wall foot.
base=np.array([.46,.285,.19]);rgb=np.ones((N,N,3),np.float32)*base
rgb+=field[:,:,None]*np.array([.23,.18,.14])+fine[:,:,None]*.45
wear=np.clip((field-.065)*4,0,.4);rgb=rgb*(1-wear[:,:,None])+np.array([.51,.435,.33])*wear[:,:,None]
rgb*=1-.18*np.exp(-y[:,:,None]*14)
# Tiny pits give the material a normal response without thick painted-on noise.
def image(name,values,path,colorspace='sRGB'):
 im=bpy.data.images.new(name,width=N,height=N,alpha=True);im.colorspace_settings.name=colorspace
 rgba=np.ones((N,N,4),np.float32);rgba[:,:,:3]=values;im.pixels.foreach_set(rgba.ravel());im.filepath_raw=str(path);im.file_format='PNG';im.save();im.pack();return im
folder=ROOT/'model/材质';folder.mkdir(exist_ok=True)
col=image('首层风化灰泥色',np.clip(rgb,0,1),folder/'首层风化灰泥色.png')
dy,dx=np.gradient(height);norm=np.stack([-dx*3,-dy*3,np.ones_like(dx)],axis=-1);norm/=np.linalg.norm(norm,axis=-1,keepdims=True)
nor=image('首层风化灰泥法线',norm*.5+.5,folder/'首层风化灰泥法线.png','Non-Color')
mat=bpy.data.materials.new('风化土朱墙');mat.use_nodes=True;nodes=mat.node_tree.nodes;links=mat.node_tree.links;bs=nodes.get('Principled BSDF');bs.inputs['Roughness'].default_value=.97
tex=nodes.new('ShaderNodeTexImage');tex.image=col;links.new(tex.outputs['Color'],bs.inputs['Base Color'])
tex=nodes.new('ShaderNodeTexImage');tex.image=nor;normal=nodes.new('ShaderNodeNormalMap');normal.inputs['Strength'].default_value=.55;links.new(tex.outputs['Color'],normal.inputs['Color']);links.new(normal.outputs['Normal'],bs.inputs['Normal'])
for o in s.objects:
 if o.type!='MESH' or '首层墙' not in o.name:continue
 o.data.materials.clear();o.data.materials.append(mat)
 uv=o.data.uv_layers.active or o.data.uv_layers.new()
 # Each wall is an eight-vertex box. Preserve its geometry and give every panel a physical plaster texture.
 for poly in o.data.polygons:
  group=poly.vertices[0]//8;coords=[o.data.vertices[v].co for v in range(group*8,group*8+8)]
  tangent=(coords[1]-coords[0]).normalized();width=(coords[1]-coords[0]).length;z0=min(v.z for v in coords);z1=max(v.z for v in coords)
  for li in poly.loop_indices:
   v=o.data.vertices[o.data.loops[li].vertex_index].co
   uv.data[li].uv=((v-coords[0]).dot(tangent)/max(width,.1)+group*.317,(v.z-z0)/max(z1-z0,.1))
 bevel=o.modifiers.get('墙角磨损') or o.modifiers.new('墙角磨损','BEVEL');bevel.width=.022;bevel.segments=2
# Add connected framing, plinth courses and door joinery, without turning solid walls into open balconies.
for k in range(8):
 angle=(k+.5)*math.pi/4;ang=angle+math.pi/2
 tangent=Vector((math.cos(ang),math.sin(ang),0));out=Vector((math.cos(angle),math.sin(angle),0))
 for j in range(3):
  a=Vector(sidepoint(11.32,k,j/3,0));b=Vector(sidepoint(11.32,k,(j+1)/3,0));c=(a+b)/2;width=(b-a).length-.28;door=k in [1,5] and j==1
  def block(cat,ma,u,z,w,d,h,depth=.17):box(1,cat,ma,c+tangent*u+out*depth+Vector((0,0,z)),(w,d,h),ang)
  for z in [10.00,10.55,16.05]:block('首层墙面收边','古木',0,z,width,.16,.16)
  for u in [-width/2+.035,width/2-.035]:
   block('首层墙面立框','暗木',u,7.4,.085,.17,5.5)
   block('重檐墙面立框','暗木',u,13.35,.085,.16,5.3)
  # Narrow, layered timber frieze below the upper bearing beam.
  for z in [15.35,15.68]:block('重檐额枋压线','古木',0,z,width,.23,.105)
  for u in [-width*.36,width*.36]:block('重檐额枋承垫','古木',u,15.53,.23,.24,.26)
  if not door:
   for row in range(2):
    for n in range(4):
     block('首层墙脚砌石','风化青石',-width/2+(n+.5)*width/4,4.67+row*.27,width/4-.018,.20,.25,.19)
   block('首层墙脚压沿','风化青石',0,5.09,width,.29,.12,.19)
  else:
   block('入口门楣','古木',0,9.72,width+.2,.36,.30,.22)
   block('入口门槛','古木',0,4.63,width,.38,.20,.20)
   for sg in [-1,1]:
    u=sg*width*.39;w=width*.19
    for side in [-1,1]:block('门扇边梃','古木',u+side*w*.42,7,.075,.095,4.85,.15)
    for z in [4.64,5.2,7.15,9.36]:block('门扇横抹','古木',u,z,w,.10,.105,.16)
    for n in [-1,0,1]:block('门扇板缝','古木',u+n*w*.22,7,.018,.03,4.5,.14)
    for z in [5.5,8.8]:block('门扇铁合页','铁刹',u,z,w*.68,.05,.095,.22)
    # A modest forged pull ring at the original door leaf, aligned with its face.
    center=c+tangent*(u-sg*w*.2)+out*.24+Vector((0,0,7.15))
    for n in range(12):
     p=center+tangent*(math.cos(n*math.tau/12)*.075)+Vector((0,0,math.sin(n*math.tau/12)*.075))
     q=center+tangent*(math.cos((n+1)*math.tau/12)*.075)+Vector((0,0,math.sin((n+1)*math.tau/12)*.075))
     rod(1,'门扇铁拉环','铁刹',p,q,.013,6)
# Recessed-looking layered stone bases beneath the existing outer columns.
for r in [14.5,11.4]:
 for k in range(8):
  for t in [0,1/3,2/3]:
   p=Vector(sidepoint(r,k,t,4.2))
   rod(1,'柱础下盘','风化青石',p,p+Vector((0,0,.16)),.54,16,.51)
   rod(1,'柱础覆盆','风化青石',p+Vector((0,0,.32)),p+Vector((0,0,.49)),.46,16,.33)
created=[]
for (i,cat,ma),(verts,faces) in buckets.items():
 me=bpy.data.meshes.new(cat);me.from_pydata(verts,[],faces);me.materials.append(bpy.data.materials[ma]);me.update();uv=me.uv_layers.new(name='TimberUV')
 for f in me.polygons:
  coords=[me.vertices[j].co for j in f.vertices];axis=max([coords[(j+1)%len(coords)]-coords[j] for j in range(len(coords))],key=lambda v:v.length).normalized();cross=f.normal.cross(axis).normalized()
  for li in f.loop_indices:
   v=me.vertices[me.loops[li].vertex_index].co;uv.data[li].uv=(v.dot(cross)*.34,v.dot(axis)*.34)
 o=bpy.data.objects.new(f'L{i}_{cat}_{ma}',me);parent=s.objects[f'Level_{i}'];parent.users_collection[0].objects.link(o);o.parent=parent;o['楼层']=i;o['构件类别']=cat
 bevel=o.modifiers.new('细部磨边','BEVEL');bevel.width=.008;bevel.segments=2;o.modifiers.new('面法线','WEIGHTED_NORMAL');created.append(o.name)
assert original=={o.name:len(o.data.vertices) for o in s.objects if o.type=='MESH' and o.parent and o.parent.name not in ['Level_0','Level_1']}
s['refined_v17']=True
bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'model/应县木塔_首层精修.blend'))
levels=[o for o in s.objects if o.name.startswith('Level_') and o.name!='Level_7'];objects=[o for o in s.objects if o.parent in levels]
bpy.ops.object.select_all(action='DESELECT')
for o in levels+objects:o.hide_set(False);o.select_set(True)
bpy.ops.export_scene.gltf(filepath=str(ROOT/'model/应县木塔_首层精修.glb'),export_format='GLB',use_selection=True,use_active_scene=True,export_apply=True,export_extras=True,export_animations=False,export_cameras=False,export_lights=False,export_yup=True)
report={'added_parts':dict(parts),'new_mesh_groups':created,'upper_geometry_unchanged':True,'scope':'首层重檐实墙、门扇、墙脚与柱础细化；展示性补建，非文物测绘复原'}
(ROOT/'model/首层精修检查.json').write_text(json.dumps(report,ensure_ascii=False,indent=2));print('DONE',report,flush=True)
