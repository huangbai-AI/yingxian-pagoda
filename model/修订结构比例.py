"""v18: photo-informed proportions and differentiated bracket assemblies.
Not a measured conservation model. The web keeps the traditional 67.31 m envelope;
the published surveyed storey ratios are used as references, not mixed as exact dimensions.
"""
import bpy,bmesh,math,json
from pathlib import Path
from mathutils import Vector
from collections import defaultdict
BASE=Path(__file__).resolve().parents[1]; s=bpy.context.scene;s.frame_set(1)
if s.get('structure_v18'):raise RuntimeError('Already revised')
parents={i:s.objects['Level_'+str(i)] for i in range(7)}
for p in parents.values():
 assert p.location.length<.0001 and max(abs(x-1) for x in p.scale)<.0001,p.name
source=(BASE/'model/重建模型.py').read_text();buckets={};parts=defaultdict(int)
exec(source[source.index('def geo('):source.index('# Square stepped base')],globals())
# Every contact uses this same monotone mapping: no independent floating storey offsets.
HEIGHTS=[(0,0),(4.42,4.42),(10.5,10.5),(13.75,13.2),(16.3,14.1),(21.48,19.202),(30.78,28.150),(39.88,37.25),(48.98,46.35),(59.0,55.571),(67.31,67.31),(100,100)]
def height(z):
 for (a,b),(c,d) in zip(HEIGHTS,HEIGHTS[1:]):
  if z<=c:return b+(z-a)/(c-a)*(d-b)
 return z
# A straight octagonal radial fit broadens the tall first-storey enclosure without moving its outer aisle.
def widen(x,y,z):
 r=max(x*math.cos((k+.5)*math.pi/4)+y*math.sin((k+.5)*math.pi/4) for k in range(8))/math.cos(math.pi/8)
 knots=[(0,0),(6.4,6.4),(11.4,12.0),(14.5,14.5),(30,30)]
 for (a,b),(c,d) in zip(knots,knots[1:]):
  if r<=c:
   nr=b+(r-a)*(d-b)/(c-a)
   # Taper back to the unchanged second-floor ring: shared interfaces must not spread.
   weight=max(0,min(1,(19.3-z)/3.0));nr=r+(nr-r)*weight
   return (x*nr/r,y*nr/r) if r>.0001 else (x,y)
 return x,y
removed=[]
for o in list(s.objects):
 if o.type!='MESH' or o.parent not in [parents[i] for i in range(1,6)]:continue
 if any(k in o.name for k in ['斗栱','昂嘴','平座坐斗','平座华栱','平座横栱','平座升斗','栏杆花格']):
  removed.append(o.name);bpy.data.objects.remove(o,do_unlink=True)

def dou(i,p,ang,size=.7,h=.25,cat='斗栱承斗',ma='古木'):
 # Sloped cheek block, broad at top; continuous closed volume.
 vs=[]
 for z,r in [(0,size*.36),(h*.48,size*.5),(h,size*.5)]:
  for x,y in [(-r,-r),(r,-r),(r,r),(-r,r)]:vs.append((p[0]+x*math.cos(ang)-y*math.sin(ang),p[1]+x*math.sin(ang)+y*math.cos(ang),p[2]+z))
 fs=[(3,2,1,0),(8,9,10,11)]+[(j*4+k,j*4+(k+1)%4,(j+1)*4+(k+1)%4,(j+1)*4+k) for j in range(2) for k in range(4)]
 geo(i,cat,ma,vs,fs)

def gong(i,c,ang,half,w,h,cat):
 # Flat bearing top, substantial centre, stepped/rounded underside at the ends.
 outline=[(-half,.16*h),(-half,.72*h),(-half*.93,h),(half*.93,h),(half,.72*h),(half,.16*h),
 (half*.84,.12*h),(half*.72,-.10*h),(half*.60,-.34*h),(half*.42,-.48*h),(-half*.42,-.48*h),(-half*.60,-.34*h),(-half*.72,-.10*h),(-half*.84,.12*h)]
 axis=Vector((math.cos(ang),math.sin(ang),0));side=Vector((-axis.y,axis.x,0));origin=Vector(c)
 vs=[tuple(origin+axis*u+side*v+Vector((0,0,z))) for v in [-w/2,w/2] for u,z in outline];n=len(outline)
 fs=[tuple(reversed(range(n))),tuple(range(n,n*2))]+[(j,(j+1)%n,(j+1)%n+n,j+n) for j in range(n)]
 geo(i,cat,'浅木',vs,fs)

def assembly(i,p,ang,sc=1,kind='柱头'):
 origin=Vector(p);rad=Vector((math.cos(ang),math.sin(ang),0));tan=Vector((-rad.y,rad.x,0))
 def at(x=0,y=0,z=0):return origin+sc*(rad*x+tan*y+Vector((0,0,z)))
 cat='斗栱'+kind
 dou(i,at(z=-.08),ang,.84*sc,.34*sc,cat+'坐斗')
 for tier in range(3):
  x=.25*tier;z=.31+.46*tier;span=.72+.25*tier
  gong(i,at(x,0,z),ang+math.pi/2,span*sc,.33*sc,.27*sc,cat+'横栱')
  gong(i,at(x+.15,0,z+.035),ang,(.72+.20*tier)*sc,.34*sc,.27*sc,cat+'华栱')
  dou(i,at(x+.14,0,z+.27),ang,.43*sc,.25*sc,cat+'交承斗')
  for sign in [-1,1]:dou(i,at(x,sign*span*.81,z+.27),ang,.36*sc,.22*sc,cat+'散斗')
  if kind=='转角' and tier>0:
   for da in [-math.pi/8,math.pi/8]:
    axis=Vector((math.cos(ang+da),math.sin(ang+da),0))
    cc=at(z=z+.035)+axis*(.40*sc)
    gong(i,cc,ang+da,(.80+tier*.20)*sc,.31*sc,.27*sc,cat+'斜栱')
    end=cc+axis*((.64+tier*.15)*sc)+Vector((0,0,.27*sc))
    dou(i,end,ang+da,.38*sc,.21*sc,cat+'斜承斗')
 if kind=='柱间':
  # Intermediate inclined branches are visibly different from the column-head set.
  for da in [-math.pi/6,math.pi/6]:
   axis=Vector((math.cos(ang+da),math.sin(ang+da),0))
   beam(i,cat+'斜昂','古木',at(z=1.43)-axis*.45*sc,at(z=.85)+axis*1.72*sc,.30*sc,.35*sc)
 else:beam(i,cat+'昂嘴','古木',at(-.60,0,1.45),at(1.85,0,.68),.34*sc,.38*sc)
 box(i,cat+'顶枋','古木',at(.59,0,1.79),(.64*sc,2.85*sc,.28*sc),ang)
 # Receiving cheek blocks at two arm tips; the open slot is built from closed solids.
 for y in [-.24,.24]:box(i,cat+'斗耳','古木',at(.20,y,.31),(.59*sc,.12*sc,.14*sc),ang)

spec=[(1,14.5,10.5,.85),(1,11.4,16.3,.85),(2,11.5,26,.78),(3,10.9,35.2,.78),(4,10.2,44.2,.76),(5,9.7,53.4,.74)]
for i,r,z,sc in spec:
 for k in range(8):
  assembly(i,point(r,k*math.pi/4,z),k*math.pi/4,sc,'转角')
  for t in [1/3,2/3]:assembly(i,sidepoint(r,k,t,z),(k+.5)*math.pi/4,sc,'柱头')
  for t in [1/6,.5,5/6]:
   p=Vector(sidepoint(r,k,t,z-.18));a=(k+.5)*math.pi/4
   # Short saddle rests on the existing continuous column-head ring.
   box(i,'斗栱柱间驼峰','古木',p+Vector((0,0,.10)),(.55,.68,.20),a)
   assembly(i,p+Vector((0,0,.14)),a,sc*.84,'柱间')

for i,r,floor,top in [(2,11.5,21.2,26),(3,10.9,30.5,35.2),(4,10.2,39.6,44.2),(5,9.7,48.7,53.4)]:
 for k in range(8):
  for t in [0,1/3,2/3]:
   a=(k if t==0 else k+.5)*math.pi/4;p=Vector(sidepoint(r-.2,k,t,floor-.98));rad=Vector((math.cos(a),math.sin(a),0));tan=Vector((-rad.y,rad.x,0))
   dou(i,p,a,.57,.22,'平座承斗')
   for n in range(3):
    c=p+rad*(.12+n*.18)+Vector((0,0,.20+n*.24));
    gong(i,c,a,.59+n*.13,.26,.18,'平座承托华栱');gong(i,c+Vector((0,0,.03)),a+math.pi/2,.60+n*.16,.26,.18,'平座承托横栱')
    for sign in [-1,1]:dou(i,c+tan*sign*(.45+n*.12)+Vector((0,0,.21)),a,.27,.12,'平座承托散斗')
   # Top load path meets the underside of the retained deck and its edge beam.
   beam(i,'平座承托短枋','古木',p+rad*.30+Vector((0,0,.88)),p+rad*.77+Vector((0,0,.88)),.34,.20)
  # Solid horizontal waist boards match the balcony silhouette in the photographs.
  beam(i,'栏杆腰板','古木',point(r+.55,k*math.pi/4,floor+.76),point(r+.55,(k+1)*math.pi/4,floor+.76),.105,.24)

checks=[]
for (i,cat,ma),(vs,fs) in buckets.items():
 me=bpy.data.meshes.new(cat+'_v18');me.from_pydata(vs,[],fs);me.materials.append(bpy.data.materials[ma]);me.update()
 bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bad=sum(not e.is_manifold for e in bm.edges);assert bad==0,(cat,bad);bm.to_mesh(me);bm.free()
 uv=me.uv_layers.new(name='TimberUV')
 for face in me.polygons:
  coords=[me.vertices[j].co for j in face.vertices];edges=[coords[(j+1)%len(coords)]-coords[j] for j in range(len(coords))];axis=max(edges,key=lambda v:v.length).normalized();cross=face.normal.cross(axis).normalized()
  for li in face.loop_indices:
   v=me.vertices[me.loops[li].vertex_index].co;uv.data[li].uv=(v.dot(cross)*.34,v.dot(axis)*.34)
 obj=bpy.data.objects.new(f'L{i}_{cat}_{ma}_v18',me);parents[i].users_collection[0].objects.link(obj);obj.parent=parents[i];obj['构件类别']=cat;obj['楼层']=i
 be=obj.modifiers.new('木缘倒圆','BEVEL');be.width=.012;be.segments=2
 obj.modifiers.new('平整木面','WEIGHTED_NORMAL');checks.append({'name':obj.name,'non_manifold_edges':bad,'faces':len(fs)})
# Warp shared world-space coordinates, including all original rafters, deck planks and contact members.
changed=0
for o in s.objects:
 if o.type!='MESH' or o.parent not in list(parents.values()):continue
 level=int(o.parent.name.split('_')[1]);assert o.location.length<.0001,o.name
 for v in o.data.vertices:
  x,y,z=v.co
  if level==1:x,y=widen(x,y,z)
  v.co=(x,y,height(z))
 o.data.update();changed+=1
s['structure_v18']=True;s['结构依据']='用户四张实拍 + 王南等2021层段比例；非测绘复原'
s.render.use_border=False;s.render.use_crop_to_border=False
# Explicit structural report: topology checks do not imply full architectural authenticity.
report={'version':18,'geometry_objects':changed,'removed_objects':removed,'height_mapping':HEIGHTS,'new_components':dict(parts),'new_mesh_checks':checks,'limits':'分段比例参照与构件类别示意修订，未取得完整测绘构件尺寸；非54种斗栱考据复原。'}
(BASE/'结构修正').mkdir(exist_ok=True);(BASE/'结构修正/结构比例_v18.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(BASE/'model/应县木塔_结构比例修订.blend'))
bpy.ops.object.select_all(action='DESELECT')
for o in s.objects:
 if o in parents.values() or o.parent in parents.values():o.hide_set(False);o.select_set(True)
bpy.ops.export_scene.gltf(filepath=str(BASE/'model/应县木塔_结构比例修订.glb'),export_format='GLB',use_selection=True,use_active_scene=True,export_apply=True,export_extras=True,export_animations=False,export_cameras=False,export_lights=False,export_yup=True)
print('V18_COMPLETE',changed,len(checks),flush=True)
