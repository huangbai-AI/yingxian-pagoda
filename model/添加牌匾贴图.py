"""v19: three photo-referenced plaque textures, embedded in the shared model.
Calligraphy recreated from the supplied photo; not a photographic facsimile.
"""
import bpy,math,json
from pathlib import Path
from mathutils import Vector
BASE=Path(__file__).resolve().parents[1];s=bpy.context.scene;s.frame_set(1)
assert s.get('structure_v18') and not s.get('plaques_v19')
source=(BASE/'model/修订结构比例.py').read_text();exec(source[source.index('HEIGHTS='):source.index('# A straight octagonal')])
image=bpy.data.images.load(str(BASE/'yingxian-pagoda/public/materials/plaques/yingxian-plaques-v19.png'));image.pack()
mat=bpy.data.materials.new('牌匾墨书_实拍参照');mat.use_nodes=True
p=mat.node_tree.nodes.get('Principled BSDF');p.inputs['Roughness'].default_value=.94;p.inputs['Metallic'].default_value=0
tex=mat.node_tree.nodes.new('ShaderNodeTexImage');tex.image=image;tex.extension='EXTEND';mat.node_tree.links.new(tex.outputs['Color'],p.inputs['Base Color'])
report=[]
for i,title,oldz,w,h,rr,rect,dz in [(2,'天宮高聳',25.1,5.5,1.65,11.7,(0,.762,.50,1),0),(3,'釋迦塔',34.35,1.58,3.2,11.1,(.762,1,0,1),-.45),(4,'天下奇觀',43.5,5.0,1.5,10.4,(0,.762,0,.50),0)]:
 parent=s.objects['Level_'+str(i)]
 for obj in list(s.objects):
  if obj.parent==parent and '匾额' in obj.name:bpy.data.objects.remove(obj,do_unlink=True)
 ang=11*math.pi/8;rad=Vector((math.cos(ang),math.sin(ang),0));tan=Vector((-rad.y,rad.x,0));up=Vector((0,0,1));c=rad*(rr*math.cos(math.pi/8))+up*(height(oldz)+dz)
 def mesh(name,vs,fs,material):
  me=bpy.data.meshes.new(name);me.from_pydata(vs,[],fs);me.materials.append(material);me.update();o=bpy.data.objects.new(f'L{i}_匾额_{name}',me);parent.users_collection[0].objects.link(o);o.parent=parent;o['题字']=title;o['楼层']=i;return o
 # Backing is solid timber; front is a separate single-material surface for web compatibility.
 vs=[tuple(c+tan*x+up*y+rad*d) for d in [-.12,.12] for x,y in [(-w/2,-h/2),(w/2,-h/2),(w/2,h/2),(-w/2,h/2)]]
 back=mesh(title+'_木胎',vs,[(3,2,1,0),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)],bpy.data.materials['暗木'])
 mod=back.modifiers.new('旧木磨边','BEVEL');mod.width=.025;mod.segments=2
 front=mesh(title+'_墨书',[tuple(c+tan*x+up*y+rad*.124) for x,y in [(-w/2,-h/2),(w/2,-h/2),(w/2,h/2),(-w/2,h/2)]],[(0,1,2,3)],mat)
 uv=front.data.uv_layers.new(name='PlaqueUV');u0,u1,v0,v1=rect
 for li,val in enumerate([(u0,v0),(u1,v0),(u1,v1),(u0,v1)]):uv.data[li].uv=val
 report.append({'level':i,'title':title,'width':w,'height':h,'center':list(c),'atlas_uv':rect})
s['plaques_v19']=True
bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(BASE/'model/应县木塔_牌匾贴图.blend'))
levels=[s.objects['Level_'+str(i)] for i in range(7)]
bpy.ops.object.select_all(action='DESELECT')
for o in s.objects:
 if o in levels or (o.parent in levels and o.type=='MESH'):o.hide_set(False);o.select_set(True)
bpy.ops.export_scene.gltf(filepath=str(BASE/'model/应县木塔_牌匾贴图.glb'),export_format='GLB',use_selection=True,use_active_scene=True,export_apply=True,export_extras=True,export_animations=False,export_cameras=False,export_lights=False,export_yup=True)
(BASE/'结构修正/牌匾贴图_v19.json').write_text(json.dumps(report,ensure_ascii=False,indent=2));print('PLAQUES_COMPLETE',report,flush=True)
