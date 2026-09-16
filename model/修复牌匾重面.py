import bpy,bmesh,json
from pathlib import Path
from mathutils import Vector
BASE=Path(__file__).resolve().parents[1];s=bpy.context.scene;s.frame_set(1);report=[]
assert s.get('plaques_v19') and not s.get('plaques_v20')
for o in s.objects:
 if o.type!='MESH' or '匾额' not in o.name or not o.name.endswith('_木胎'):continue
 front=s.objects.get(o.name[:-3]+'_墨书');assert front,o.name
 normal=front.data.polygons[0].normal.normalized()
 bm=bmesh.new();bm.from_mesh(o.data)
 faces=[f for f in bm.faces if f.normal.dot(normal)>.999]
 assert len(faces)==1,(o.name,len(faces))
 bmesh.ops.delete(bm,geom=faces,context='FACES_ONLY');bm.to_mesh(o.data);bm.free();o.data.update()
 report.append({'backing':o.name,'removed_duplicate_front_faces':1})
assert len(report)==3
s['plaques_v20']=True
bpy.ops.wm.save_as_mainfile(filepath=str(BASE/'model/应县木塔_牌匾稳定版.blend'))
levels=[s.objects['Level_'+str(i)] for i in range(7)]
bpy.ops.object.select_all(action='DESELECT')
for o in s.objects:
 if o in levels or (o.parent in levels and o.type=='MESH'):o.hide_set(False);o.select_set(True)
bpy.ops.export_scene.gltf(filepath=str(BASE/'model/应县木塔_牌匾稳定版.glb'),export_format='GLB',use_selection=True,use_active_scene=True,export_apply=True,export_extras=True,export_animations=False,export_cameras=False,export_lights=False,export_yup=True)
(BASE/'结构修正/牌匾重面修复_v20.json').write_text(json.dumps(report,ensure_ascii=False,indent=2));print('FIXED',report)
