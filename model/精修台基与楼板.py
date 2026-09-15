import bpy,math,random,json
from pathlib import Path
from mathutils import Vector
from collections import defaultdict
ROOT=Path(__file__).resolve().parent.parent;s=bpy.context.scene;s.frame_set(1)
assert not s.get('refined_v11')
source=(ROOT/'model/重建模型.py').read_text();buckets={};parts=defaultdict(int)
exec(source[source.index('def geo('):source.index('# Square stepped base')],globals())
random.seed(1056)
# Stone balustrades rest on the existing upper plinth, leaving both stair openings clear.
for k in range(8):
 a=Vector(point(16.82,k*math.pi/4,4.2));b=Vector(point(16.82,(k+1)*math.pi/4,4.2));t=(b-a).normalized()
 for j in range(6):
  p=a.lerp(b,j/6)
  if abs(p.x)<3.8 and abs(p.y)>14:continue
  box(0,'石栏柱脚','风化青石',p+Vector((0,0,.10)),(.48,.48,.20))
  rod(0,'石栏望柱','风化青石',p+Vector((0,0,.20)),p+Vector((0,0,1.36)),.17,8,.14)
  box(0,'石栏柱帽','风化青石',p+Vector((0,0,1.37)),(.39,.39,.16))
  rod(0,'石栏莲头','风化青石',p+Vector((0,0,1.45)),p+Vector((0,0,1.70)),.21,12,.045)
  q=a.lerp(b,(j+1)/6);mid=(p+q)/2
  if abs(mid.x)<3.8 and abs(mid.y)>14:continue
  for z in [.24,1.03]:beam(0,'石栏压沿','风化青石',p+Vector((0,0,z)),q+Vector((0,0,z)),.18,.16)
  beam(0,'石栏板','风化青石',p+t*.20+Vector((0,0,.57)),q-t*.20+Vector((0,0,.57)),.12,.48)
  # Recessed panel framed by a raised border, visible from the courtyard.
  for z in [.38,.77]:beam(0,'石栏浮框','风化青石',p+t*.24+Vector((0,0,z)),q-t*.24+Vector((0,0,z)),.17,.045)
# Individually coursed stones replace the previously drawn mortar lines.
for o in list(s.objects):
 if 'L0_石砌缝' in o.name:bpy.data.objects.remove(o,do_unlink=True)
for k in range(8):
 a=Vector(point(17.02,k*math.pi/4,0));b=Vector(point(17.02,(k+1)*math.pi/4,0));t=(b-a).normalized();length=(b-a).length
 for row in range(5):
  offset=-.63 if row%2 else 0
  x=offset
  while x<length:
   start=max(0,x)+.015;end=min(length,x+1.26)-.015
   if end>start:beam(0,'砌石面层','风化青石',a+t*start+Vector((0,0,1.8+row*.43)),a+t*end+Vector((0,0,1.8+row*.43)),.105,.404)
   x+=1.26
# Individual plank volumes clipped to the octagonal floor, preserving the stair opening.
def clip(poly,axis,value,sign):
 out=[]
 for a,b in zip(poly,poly[1:]+poly[:1]):
  da=(a[axis]-value)*sign;db=(b[axis]-value)*sign
  if da>=-1e-8:out.append(a)
  if (da>=0)!=(db>=0):
   f=da/(da-db);out.append(tuple(a[i]+f*(b[i]-a[i]) for i in range(2)))
 return out
plank_count=0
for level,r,z in [(2,12.2,21.2),(3,11.6,30.5),(4,10.9,39.6),(5,10.4,48.7)]:
 for o in list(s.objects):
  if o.name.startswith(f'L{level}_楼板_') or o.name.startswith(f'L{level}_板缝_'):bpy.data.objects.remove(o,do_unlink=True)
 for k in range(8):
  poly=[point(rad,j*math.pi/4,0)[:2] for rad,j in [(r,k),(r,k+1),(2.3,k+1),(2.3,k)]]
  for row in range(-27,28):
   for col in range(-5,6):
    lo=col*3.2+(row%3)*1.06;hi=lo+3.185
    pp=poly
    for axis,value,sign in [(0,lo,1),(0,hi,-1),(1,row*.46+.012,1),(1,(row+1)*.46-.012,-1)]:
     pp=clip(pp,axis,value,sign) if pp else []
    if len(pp)<3:continue
    area=abs(sum(a[0]*b[1]-b[0]*a[1] for a,b in zip(pp,pp[1:]+pp[:1])))/2
    if area<.003:continue
    n=len(pp);vs=[(x,y,zz) for zz in [z,z+.28] for x,y in pp];fs=[tuple(reversed(range(n))),tuple(range(n,n*2))]+[(j,(j+1)%n,(j+1)%n+n,j+n) for j in range(n)]
    geo(level,'实铺木地板','古木',vs,fs);plank_count+=1
# Small secondary halls behind the tower give the courtyard genuine parallax and shadows.
for cx in [-35,35]:
 cy=30
 box(0,'配殿基座','风化青石',(cx,cy,.4),(20,11,.8))
 box(0,'配殿墙身','暗木',(cx,cy,2.6),(18,8,3.6))
 for x in range(-8,9,2):
  rod(0,'配殿廊柱','朱漆',(cx+x,cy-4.8,.8),(cx+x,cy-4.8,5.0),.19,12)
 for y in [-4.8,4.8]:beam(0,'配殿檐枋','古木',(cx-10,cy+y,4.8),(cx+10,cy+y,4.8),.35,.42)
 for sign in [-1,1]:
  for ix in range(71):
   x=cx-10.5+ix*.30
   for j in range(12):
    u=j/12;v=(j+1)/12
    def p(t):return (x,cy+sign*t*6,6.8-2.4*t+.5*t**5)
    rod(0,'配殿筒瓦','青灰瓦',p(u),p(v),.12,6)
  vs=[(cx+dx,cy+sign*t*6,6.7-2.4*t+.5*t**5) for dx in [-10.8,10.8] for t in [j/12 for j in range(13)]]
  geo(0,'配殿屋面','青灰瓦',vs,[(j,j+1,j+14,j+13) for j in range(12)])
 rod(0,'配殿正脊','瓦脊',(cx-10.8,cy,6.84),(cx+10.8,cy,6.84),.21,8)
# Material and bevels are editable; export includes evaluated bevel geometry.
stone=bpy.data.materials.new('风化青石');stone.use_nodes=True;bs=stone.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=(.20,.215,.20,1);bs.inputs['Roughness'].default_value=.93
noise=stone.node_tree.nodes.new('ShaderNodeTexNoise');noise.inputs['Scale'].default_value=36
bump=stone.node_tree.nodes.new('ShaderNodeBump');bump.inputs['Strength'].default_value=.3;bump.inputs['Distance'].default_value=.018;stone.node_tree.links.new(noise.outputs['Fac'],bump.inputs['Height']);stone.node_tree.links.new(bump.outputs['Normal'],bs.inputs['Normal'])
created=[]
for (i,cat,ma),(verts,faces) in buckets.items():
 me=bpy.data.meshes.new(cat);me.from_pydata(verts,[],faces);me.materials.append(bpy.data.materials[ma]);me.update();uv=me.uv_layers.new(name='TimberUV')
 for f in me.polygons:
  coords=[me.vertices[j].co for j in f.vertices];axis=max([coords[(j+1)%len(coords)]-coords[j] for j in range(len(coords))],key=lambda x:x.length).normalized();cross=f.normal.cross(axis).normalized()
  for li in f.loop_indices:
   v=me.vertices[me.loops[li].vertex_index].co
   uv.data[li].uv=(v.y*.34,v.x*.34) if '木地板' in cat and abs(f.normal.z)>.9 else (v.dot(cross)*.34,v.dot(axis)*.34)
 o=bpy.data.objects.new(f'L{i}_{cat}_{ma}',me);parent=s.objects[f'Level_{i}'];parent.users_collection[0].objects.link(o);o.parent=parent;o['楼层']=i;o['构件类别']=cat
 if '筒瓦' not in cat and '屋面' not in cat:
  bevel=o.modifiers.new('磨损倒角','BEVEL');bevel.width=.008 if '木地板' in cat else .024;bevel.segments=2;o.modifiers.new('面法线','WEIGHTED_NORMAL')
 created.append(o.name)
s['refined_v11']=True
levels=[o for o in s.objects if o.name.startswith('Level_') and o.name!='Level_7'];objects=[o for o in s.objects if o.parent in levels]
bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'model/应县木塔_环境精修.blend'))
bpy.ops.object.select_all(action='DESELECT')
for o in levels+objects:o.hide_set(False);o.select_set(True)
bpy.ops.export_scene.gltf(filepath=str(ROOT/'model/应县木塔_环境精修.glb'),export_format='GLB',use_selection=True,use_active_scene=True,export_apply=True,export_extras=True,export_animations=False,export_cameras=False,export_lights=False,export_yup=True)
report={'planks':plank_count,'new_mesh_groups':created,'levels':len(levels),'source':'应县木塔.blend（第六版完整斗栱修复已保留）','scope':'补建石栏、砌石、实铺木地板和氛围配殿；非寺院测绘复原'}
(ROOT/'model/环境精修检查.json').write_text(json.dumps(report,ensure_ascii=False,indent=2));print('DONE',report,flush=True)
