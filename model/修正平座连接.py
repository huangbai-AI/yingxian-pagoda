import bpy,bmesh,math,os,json,re
from mathutils import Vector
from collections import defaultdict
BASE=os.path.dirname(os.path.dirname(os.path.abspath(__file__)));s=bpy.context.scene;s.frame_set(1)
if s.get('assembly_corrected_v6'):raise RuntimeError('本场景已修正平座连接，请使用未修正副本。')
os.makedirs(BASE+'/结构修正',exist_ok=True)
# Load only geometry helper definitions from the original generator.
source=open(BASE+'/model/重建模型.py').read();start=source.index('def geo(');end=source.index('# Square stepped base')
buckets={};parts=defaultdict(int);exec(source[start:end],globals())
parents={i:s.objects.get('Level_'+str(i)) for i in range(7)}
report=[]
for i,r,floor,top in [(2,11.5,21.2,26),(3,10.9,30.5,35.2),(4,10.2,39.6,44.2),(5,9.7,48.7,53.4)]:
 removed=0
 for o in list(s.objects):
  if o.type!='MESH' or o.parent!=parents[i] or not any(t in o.name for t in ['斗栱','昂嘴']):continue
  bm=bmesh.new();bm.from_mesh(o.data);verts=[v for v in bm.verts if v.co.z<floor-.3];removed+=len(verts);bmesh.ops.delete(bm,geom=verts,context='VERTS');bm.to_mesh(o.data);bm.free();o.data.update()
 # A continuous sill supports each seat; radial beams join the inner load-bearing ring.
 ring_beams(i,r-.2,floor-1.12,.45,.28,'平座承梁','古木')
 ring_beams(i,r+.42,floor-.16,.33,.32,'平座托檐枋','古木')
 for k in range(8):
  for t in [0,1/3,2/3]:
   ang=(k+.5)*math.pi/4;p=Vector(sidepoint(r-.2,k,t,floor-.98));rad=Vector((math.cos(ang),math.sin(ang),0));tan=Vector((-math.sin(ang),math.cos(ang),0))
   # Connected squat seats with longitudinal arms and two tiers of bearing blocks.
   box(i,'平座坐斗','古木',p+Vector((0,0,.12)),(.48,.52,.24),ang)
   for tier in range(2):
    center=p+rad*(.16+tier*.20)+Vector((0,0,.30+tier*.25))
    box(i,'平座华栱','浅木',center,(1.05+tier*.25,.24,.24),ang)
    box(i,'平座横栱','浅木',center+Vector((0,0,.06)),(.30,1.25+tier*.28,.22),ang)
    for sign in [-1,1]:box(i,'平座升斗','古木',center+tan*sign*(.40+tier*.10)+Vector((0,0,.20)),(.30,.28,.18),ang)
   beam(i,'平座挑梁','古木',sidepoint(r*.56,k,t,floor-.16),sidepoint(r+.64,k,t,floor-.16),.30,.32)
 # Dark recessed spandrel bridges the external mezzanine band without covering the brackets.
 for k in range(8):
  a=point(r-.46,k*math.pi/4,floor-.66);b=point(r-.46,(k+1)*math.pi/4,floor-.66);beam(i,'平座暗层封板','暗木',a,b,.10,.83)
 report.append({'level':i,'removed_old_bracket_vertices':removed,'sill_top':floor-.98,'bracket_base':floor-.98,'deck_bottom':floor,'support_beam_top':floor})
# Replace only the intermediate roof belts. Their upper edge now stops below the balcony sill.
roofs=[(1,15.15,11.5,17.7,21.2,'首层',11.4,16.3,.85),(2,14,10.9,27.5,30.5,'主檐',11.5,26,.72),(3,13.4,10.2,36.7,39.6,'主檐',10.9,35.2,.72),(4,12.7,9.7,45.7,48.7,'主檐',10.2,44.2,.72)]
for i,outer,nextr,z,floor,tag,sr,sz,ss in roofs:
 prefix=['屋面_','望板_','屋架檩条_','屋架顺梁_','屋架承托_','屋架撑木_','筒瓦_','椽子_','檐口_','垂脊_','瓦当_']
 # Preserve lower first-storey ornaments, replace upper ornaments to follow the new slope.
 for o in list(s.objects):
  if o.type!='MESH' or o.parent!=parents[i]:continue
  if '脊饰' in o.name:
   bm=bmesh.new();bm.from_mesh(o.data);verts=[v for v in bm.verts if i!=1 or v.co.z>17];bmesh.ops.delete(bm,geom=verts,context='VERTS');bm.to_mesh(o.data);bm.free();o.data.update()
  if any((p+tag) in o.name for p in prefix):bpy.data.objects.remove(o,do_unlink=True)
 before=set(buckets)
 roof(i,outer,nextr+.25,z,max(.6,floor-1.33-z),tag,sr,sz,ss)
 # Existing untagged roof ornaments are retained, skip duplicated generated ones.
 for key in list(buckets):
  if key not in before and key[1] in ['风铎']:del buckets[key]
# Create named, independently editable model parts and apply visibility consistent with six scenes.
roofmatch=re.compile('筒瓦|屋面|垂脊|檐口|椽子|脊饰|风铎|攒尖|塔刹|相轮|宝瓶|刹尖|刹链|瓦当|望板|屋架')
for (i,cat,ma),(vs,fs) in buckets.items():
 me=bpy.data.meshes.new(f'{i}_{cat}_{ma}_修正');me.from_pydata(vs,[],fs);me.materials.append(bpy.data.materials[ma]);me.update();uv=me.uv_layers.new(name='TimberUV')
 for face in me.polygons:
  pts=[me.vertices[j].co for j in face.vertices];edges=[pts[(j+1)%len(pts)]-pts[j] for j in range(len(pts))];axis=max(edges,key=lambda e:e.length).normalized();cross=face.normal.cross(axis).normalized()
  for li in face.loop_indices:
   v=me.vertices[me.loops[li].vertex_index].co;uv.data[li].uv=(v.dot(cross)*.34,v.dot(axis)*.34)
 o=bpy.data.objects.new(f'L{i}_{cat}_{ma}_修正',me);parents[i].users_collection[0].objects.link(o);o.parent=parents[i];o['构件类别']=cat;o['楼层']=i
 if cat.startswith('平座'):
  bevel=o.modifiers.new('木缘细磨','BEVEL');bevel.width=.012;bevel.segments=2;o.modifiers.new('平整木面','WEIGHTED_NORMAL')
 if any(t in cat for t in ['筒瓦','屋面','垂脊','瓦当']):
  for f in me.polygons:f.use_smooth=True
 for j in range(6):
  o.hide_render=(j==1 and i not in [2,3,4]) or (j in [2,3] and (i!=3 or(j==2 and bool(roofmatch.search(cat)))));o.keyframe_insert('hide_render',frame=j*100+1)
s.frame_set(2);s.frame_set(1);s['assembly_corrected_v6']=True
bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=BASE+'/model/应县木塔_六幕光影.blend')
with open(BASE+'/结构修正/承托尺寸检查.json','w') as f:json.dump(report,f,ensure_ascii=False,indent=2)
print('ASSEMBLY_FIXED',report,flush=True)
# Export only this active scene (the file also contains Blender's unused default scene).
levels=[o for o in s.objects if o.name.startswith('Level_') and o.name!='Level_7'];objects=[o for o in s.objects if o.parent in levels]
bpy.ops.object.select_all(action='DESELECT')
for o in levels+objects:o.hide_set(False);o.select_set(True)
bpy.ops.export_scene.gltf(filepath=BASE+'/model/应县木塔_通用.glb',export_format='GLB',use_selection=True,use_active_scene=True,export_apply=True,export_extras=True,export_animations=False,export_cameras=False,export_lights=False,export_yup=True)
print('EXPORTED',len(objects),flush=True)
