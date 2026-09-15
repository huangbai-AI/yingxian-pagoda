import bpy,bmesh,os,math,json
from mathutils import Vector
from collections import defaultdict
BASE=os.path.dirname(os.path.dirname(os.path.abspath(__file__)));s=bpy.context.scene;s.frame_set(1)
if s.get('bracket_repaired_v6'):raise RuntimeError('本场景已完成斗栱完整性修复，无需重复执行。')
source=open(BASE+'/model/重建模型.py').read();buckets={};parts=defaultdict(int);exec(source[source.index('def geo('):source.index('# Square stepped base')],globals())
for k in range(8):
 for t in [0,1/3,2/3]:bracket(3,sidepoint(10.9,k,t,35.2),(k+.5)*math.pi/4,.72)
parent=s.objects['Level_3'];cats=['斗栱坐斗','斗栱栱身','斗栱升斗','昂嘴','斗栱顶枋']
for o in list(s.objects):
 if o.parent==parent and any(c in o.name for c in cats):bpy.data.objects.remove(o,do_unlink=True)
accepted=0;rejected=0;component_count=0
for (i,cat,ma),(verts,faces) in buckets.items():
 # Work on each closed solid separately: the old grouped Boolean damaged intersecting solids.
 adj=[set() for v in verts]
 for f in faces:
  for a,b in zip(f,f[1:]+f[:1]):adj[a].add(b);adj[b].add(a)
 seen=set();components=[];face_by_vertex=defaultdict(list)
 for f in faces:face_by_vertex[f[0]].append(f)
 for start in range(len(verts)):
  if start in seen:continue
  ids=[];stack=[start];seen.add(start)
  while stack:
   a=stack.pop();ids.append(a)
   for b in adj[a]:
    if b not in seen:seen.add(b);stack.append(b)
  components.append(ids)
 finalv=[];finalf=[]
 for ids in components:
  component_count+=1;mapping={old:j for j,old in enumerate(ids)};vv=[verts[j] for j in ids];ff=[tuple(mapping[q] for q in f) for j in ids for f in face_by_vertex[j]]
  center=sum((Vector(v) for v in vv),Vector())/len(vv)
  if abs(center.x)<1.7 and center.y<-10 and cat in ['斗栱坐斗','斗栱升斗','斗栱顶枋']:
   mesh=bpy.data.meshes.new('完整木块');mesh.from_pydata(vv,[],ff);mesh.update();obj=bpy.data.objects.new('单独加工木块',mesh);s.collection.objects.link(obj)
   face=max([f for f in mesh.polygons if f.normal.y<-.25],key=lambda f:f.area,default=None)
   if face and face.area>.025:
    coords=[mesh.vertices[j].co for j in face.vertices];edges=[coords[(j+1)%len(coords)]-coords[j] for j in range(len(coords))];axis=max(edges,key=lambda e:e.length).normalized();normal=face.normal.normalized();cross=normal.cross(axis).normalized();c=face.center;length=min(.22,max(e.length for e in edges)*.34);width=.006;depth=.007
    cv=[tuple(c+axis*x*length+cross*y*width+normal*z) for z in [-depth,.012] for x,y in [(-.5,0),(-.32,-1),(.35,-.6),(.5,0),(.32,1),(-.35,.6)]]
    cf=[tuple(reversed(range(6))),tuple(range(6,12))]+[(a,(a+1)%6,(a+1)%6+6,a+6) for a in range(6)]
    cm=bpy.data.meshes.new('浅凹槽');cm.from_pydata(cv,[],cf);cm.update();co=bpy.data.objects.new('浅凹槽刀具',cm);s.collection.objects.link(co)
    mod=obj.modifiers.new('单件浅槽','BOOLEAN');mod.operation='DIFFERENCE';mod.solver='EXACT';mod.object=co;bpy.context.view_layer.objects.active=obj
    try:
     bpy.ops.object.modifier_apply(modifier=mod.name);newv=[tuple(v.co) for v in obj.data.vertices];newf=[tuple(f.vertices) for f in obj.data.polygons]
     # Keep only verified results that preserve the complete block's outer envelope and volume.
     bm=bmesh.new();bm.from_mesh(obj.data);newvol=abs(bm.calc_volume(signed=True));bm.free()
     om=bpy.data.meshes.new('核对原块');om.from_pydata(vv,[],ff);bm=bmesh.new();bm.from_mesh(om);oldvol=abs(bm.calc_volume(signed=True));bm.free();bpy.data.meshes.remove(om)
     delta=max(abs(min(v[a] for v in newv)-min(v[a] for v in vv)) for a in range(3)) if newv else 999
     delta=max(delta,max(abs(max(v[a] for v in newv)-max(v[a] for v in vv)) for a in range(3))) if newv else 999
     if delta<.0001 and oldvol*.985<newvol<=oldvol*1.001:vv,ff=newv,newf;accepted+=1
     else:rejected+=1
    except Exception as e:rejected+=1;print('REJECT',str(e),flush=True)
    bpy.data.objects.remove(co,do_unlink=True)
   bpy.data.objects.remove(obj,do_unlink=True)
  offset=len(finalv);finalv+=vv;finalf.extend(tuple(j+offset for j in f) for f in ff)
 me=bpy.data.meshes.new(cat+'_完整');me.from_pydata(finalv,[],finalf);me.materials.append(bpy.data.materials[ma]);me.update();uv=me.uv_layers.new(name='TimberUV')
 for face in me.polygons:
  coords=[me.vertices[j].co for j in face.vertices];edges=[coords[(j+1)%len(coords)]-coords[j] for j in range(len(coords))];axis=max(edges,key=lambda e:e.length).normalized();cross=face.normal.cross(axis).normalized()
  for li in face.loop_indices:
   v=me.vertices[me.loops[li].vertex_index].co;uv.data[li].uv=(v.dot(cross)*.34,v.dot(axis)*.34)
 o=bpy.data.objects.new('L3_'+cat+'_'+ma+'_完整校正',me);parent.users_collection[0].objects.link(o);o.parent=parent;o['构件类别']=cat;o['楼层']=3
 bevel=o.modifiers.new('木缘细磨','BEVEL');bevel.width=.014;bevel.segments=3;o.modifiers.new('平整木面','WEIGHTED_NORMAL')
 for f in [1,101,201,301,401,501]:o.hide_render=False;o.keyframe_insert('hide_render',frame=f)
s['bracket_repaired_v6']=True;s['verified_shallow_grooves']=accepted;s.frame_set(2);s.frame_set(1)
report={'restored_closed_components':component_count,'verified_shallow_grooves':accepted,'rejected_grooves':rejected,'preserved_block_volume_ratio_min':.985,'envelope_tolerance_m':.0001}
open(BASE+'/结构修正/斗栱完整性检查.json','w').write(json.dumps(report,ensure_ascii=False,indent=2));print('REPAIRED',report,flush=True)
bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=BASE+'/model/应县木塔_六幕光影.blend')
levels=[o for o in s.objects if o.name.startswith('Level_') and o.name!='Level_7'];objects=[o for o in s.objects if o.parent in levels]
bpy.ops.object.select_all(action='DESELECT')
for o in levels+objects:o.hide_set(False);o.select_set(True)
bpy.ops.export_scene.gltf(filepath=BASE+'/model/应县木塔_通用.glb',export_format='GLB',use_selection=True,use_active_scene=True,export_apply=True,export_extras=True,export_animations=False,export_cameras=False,export_lights=False,export_yup=True)
