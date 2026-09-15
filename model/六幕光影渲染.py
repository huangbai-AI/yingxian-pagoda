import bpy,math,os,json,random,re
from mathutils import Vector
BASE=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
scene=bpy.context.scene
scene.name='应县木塔 · 六幕光影'
model=[o for o in scene.objects if o.name.startswith('Level_') and o.name!='Level_7']
objects=[o for o in scene.objects if o.parent in model]
for o in scene.objects:
 if o.name.startswith('Detail_') or o.name=='Level_7':o.hide_render=True
# Export smooth tile normals back to the portable model without changing its dimensions.
for o in objects:
 if o.type=='MESH' and any(s in o.name for s in ['筒瓦','屋面','垂脊','瓦当']):
  for f in o.data.polygons:f.use_smooth=True
bpy.ops.object.select_all(action='DESELECT')
for o in model+objects:o.hide_set(False);o.select_set(True)
bpy.ops.export_scene.gltf(filepath=BASE+'/model/应县木塔_通用.glb',export_format='GLB',use_selection=True,use_active_scene=True,export_apply=True,export_extras=True,export_yup=True)
bpy.ops.object.select_all(action='DESELECT')
# Keep a clean editable building before adding the optional exhibition environment.
bpy.ops.wm.save_as_mainfile(filepath=BASE+'/model/应县木塔.blend')
# Muted timber patina for the high quality render; the image pixels are shared with the website.
for mat in bpy.data.materials:
 if not mat.use_nodes:continue
 nt=mat.node_tree;p=nt.nodes.get('Principled BSDF')
 if not p:continue
 tex=next((n for n in nt.nodes if n.type=='TEX_IMAGE'),None)
 if tex and mat.name in ['古木','暗木','浅木','朱漆']:
  mix=nt.nodes.new('ShaderNodeMixRGB');mix.blend_type='MULTIPLY';mix.inputs[0].default_value=1
  factor={'古木':(.65,.59,.49,1),'浅木':(.78,.69,.54,1),'暗木':(.43,.42,.36,1),'朱漆':(.65,.48,.36,1)}[mat.name]
  mix.inputs[2].default_value=factor;nt.links.new(tex.outputs['Color'],mix.inputs[1]);nt.links.new(mix.outputs[0],p.inputs['Base Color'])
 if mat.name in ['青灰瓦','瓦脊']:p.inputs['Base Color'].default_value=(.032,.043,.057,1)
 if mat.name=='石台':p.inputs['Base Color'].default_value=(.25,.25,.22,1)
 if mat.name=='彩画青':p.inputs['Base Color'].default_value=(.028,.05,.036,1)
# Environment uses packed texture plates only for distant sky and foliage. Architecture is full geometry.
asset=BASE+'/yingxian-pagoda/public/environment/'
world=scene.world;world.use_nodes=True;nt=world.node_tree;nt.nodes.clear()
output=nt.nodes.new('ShaderNodeOutputWorld');envtex=nt.nodes.new('ShaderNodeTexEnvironment');envtex.image=bpy.data.images.load(asset+'night-sky.png');background=nt.nodes.new('ShaderNodeBackground');background.inputs['Strength'].default_value=.65;nt.links.new(envtex.outputs['Color'],background.inputs['Color']);nt.links.new(background.outputs[0],output.inputs['Surface'])
oldground=scene.objects.get('展示地面')
if oldground:oldground.hide_render=True
ambient_objects=[]
# A joined stone-paved courtyard has real gaps and real cast shadows.
random.seed(1056);vs=[];fs=[];mis=[]
def cube(x,y,z,sx,sy,sz):
 n=len(vs);vs.extend([(x+a*sx/2,y+b*sy/2,z+c*sz/2) for a,b,c in [(-1,-1,-1),(1,-1,-1),(1,1,-1),(-1,1,-1),(-1,-1,1),(1,-1,1),(1,1,1),(-1,1,1)]])
 fs.extend([tuple(n+j for j in f) for f in [(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)]])
 shade=random.randrange(4);mis.extend([shade]*6)
for x in range(-23,24):
 for y in range(-26,20):
  xx=x*2.6+(y%2)*1.3;yy=y*1.8
  if abs(xx)<17.4 and abs(yy)<17.4:continue
  cube(xx,yy,-.13,2.56,1.76,.16)
mesh=bpy.data.meshes.new('石铺前庭');mesh.from_pydata(vs,[],fs);mesh.update();court=bpy.data.objects.new('石铺前庭',mesh);scene.collection.objects.link(court);ambient_objects.append(court)
for v in [.13,.16,.19,.22]:
 m=bpy.data.materials.new('石材');m.use_nodes=True;p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(v,v*.99,v*.86,1);p.inputs['Roughness'].default_value=.94;mesh.materials.append(m)
for f,i in zip(mesh.polygons,mis):f.material_index=i
pine=bpy.data.materials.new('远景松影');pine.use_nodes=True;nt=pine.node_tree;nt.nodes.clear();out=nt.nodes.new('ShaderNodeOutputMaterial');tr=nt.nodes.new('ShaderNodeBsdfTransparent');em=nt.nodes.new('ShaderNodeEmission');em.inputs[1].default_value=.75;im=nt.nodes.new('ShaderNodeTexImage');im.image=bpy.data.images.load(asset+'pine.png');mix=nt.nodes.new('ShaderNodeMixShader');nt.links.new(im.outputs['Color'],em.inputs[0]);nt.links.new(im.outputs['Alpha'],mix.inputs[0]);nt.links.new(tr.outputs[0],mix.inputs[1]);nt.links.new(em.outputs[0],mix.inputs[2]);nt.links.new(mix.outputs[0],out.inputs[0])
trees=[]
for j in range(30):
 a=random.uniform(0,math.tau);r=random.uniform(47,82);x=math.cos(a)*r;y=math.sin(a)*r
 if y<15 and abs(x)<38:continue
 h=random.uniform(13,23);w=h*.76
 me=bpy.data.meshes.new('松影平面');me.from_pydata([(-w/2,0,-.8),(w/2,0,-.8),(w/2,0,h-.8),(-w/2,0,h-.8)],[],[(0,1,2,3)]);me.materials.append(pine);uv=me.uv_layers.new()
 for loop,q in zip(uv.data,[(0,0),(1,0),(1,1),(0,1)]):loop.uv=q
 tree=bpy.data.objects.new('松影',me);scene.collection.objects.link(tree);tree.location=(x,y,0);trees.append(tree);ambient_objects.append(tree)
# Key light stays in the same direction throughout the sequence.
for o in scene.objects:
 if o.type=='LIGHT':
  if o.name=='暖金主光':o.data.energy=125000;o.data.size=24
  if o.name=='墨绿天光':o.data.energy=70000
  if o.name=='檐口轮廓光':o.data.energy=115000
camera=scene.camera;camera.data.type='PERSP';camera.data.sensor_fit='VERTICAL';camera.data.sensor_height=24;camera.data.lens=24/(2*math.tan(math.radians(17)))
scene.render.engine='CYCLES';scene.cycles.device='CPU';scene.cycles.denoising_use_gpu=False;scene.cycles.samples=40;scene.cycles.use_denoising=True;scene.render.resolution_x=1600;scene.render.resolution_y=1000;scene.render.resolution_percentage=100;scene.render.image_settings.file_format='PNG';scene.view_settings.view_transform='AgX'
poses=[([62,46,132],[0,32,0],0,0,0),([38,64,63],[0,44,0],-.13,-.43,1),([23,70,33],[0,41.5,0],-.17,-.08,1),([3.2,43.1,17.4],[.18,44.1,11.2],.27,0,1),([18,33,37],[.5,34.1,8],.16,.13,0),([64,43,145],[0,32,0],-.16,0,0)]
labels=['初见','斜向拆层','柱网','斗栱','飞檐归位','全景守护']
roof=re.compile('筒瓦|屋面|垂脊|檐口|椽子|脊饰|风铎|攒尖|塔刹|相轮|宝瓶|刹尖|刹链|瓦当|望板|屋架')
def xyz(v):return Vector((v[0],-v[2],v[1]))
for j,(pos,aim,shift,roll,explode) in enumerate(poses):
 frame=j*100+1
 for level in model:
  i=int(level.name.split('_')[1]);level.location.z=0 if i==0 else (min(i,5)-2)*8*explode;level.keyframe_insert('location',frame=frame)
 for o in objects:
  i=int(o.parent.name.split('_')[1]);hide=False
  if j==1:hide=i not in [2,3,4] or bool(re.search('木楼梯|层间承|层间拉结',o.name))
  if j in [2,3]:hide=i!=3 or bool(re.search('木楼梯|层间承|层间拉结|隔扇|匾额',o.name)) or (j==2 and bool(roof.search(o.name)))
  o.hide_render=hide;o.keyframe_insert('hide_render',frame=frame)
 for o in ambient_objects:o.hide_render=j not in [0,5];o.keyframe_insert('hide_render',frame=frame)
 camera.location=xyz(pos);direction=xyz(aim)-camera.location;camera.rotation_euler=direction.to_track_quat('-Z','Y').to_euler();camera.rotation_euler.rotate_axis('Z',-roll);camera.data.shift_x=-shift*1.6;camera.data.shift_y=0
 camera.keyframe_insert('location',frame=frame);camera.keyframe_insert('rotation_euler',frame=frame);camera.data.keyframe_insert('shift_x',frame=frame)
 for tree in trees:
  d=camera.location-tree.location;tree.rotation_euler.z=math.atan2(d.x,-d.y);tree.keyframe_insert('rotation_euler',frame=frame)
 marker=scene.timeline_markers.new(labels[j],frame=frame);marker.camera=camera
# Continuous ground supports the courtyard and distant trees.
ground=scene.objects.get('连续庭院地面')
if ground is None:
 me=bpy.data.meshes.new('连续地面');me.from_pydata([(-1000,-1000,-.11),(1000,-1000,-.11),(1000,1000,-.11),(-1000,1000,-.11)],[],[(0,1,2,3)])
 ground=bpy.data.objects.new('连续庭院地面',me);scene.collection.objects.link(ground)
 mat=bpy.data.materials.new('远景地面');mat.use_nodes=True;p=mat.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(.06,.071,.052,1);p.inputs['Roughness'].default_value=.97;me.materials.append(mat)
# Blend distant ground into the atmospheric background, avoiding a hard horizon.
mat=ground.data.materials[0];nt=mat.node_tree
if not nt.nodes.get('远景柔化'):
 geo=nt.nodes.new('ShaderNodeNewGeometry');distance=nt.nodes.new('ShaderNodeVectorMath');distance.operation='LENGTH';nt.links.new(geo.outputs['Position'],distance.inputs[0])
 fade=nt.nodes.new('ShaderNodeMapRange');fade.name='远景柔化';fade.clamp=True;fade.inputs['From Min'].default_value=95;fade.inputs['From Max'].default_value=200;nt.links.new(distance.outputs['Value'],fade.inputs['Value'])
 transparent=nt.nodes.new('ShaderNodeBsdfTransparent');mix=nt.nodes.new('ShaderNodeMixShader');nt.links.new(fade.outputs['Result'],mix.inputs[0]);nt.links.new(nt.nodes.get('Principled BSDF').outputs[0],mix.inputs[1]);nt.links.new(transparent.outputs[0],mix.inputs[2]);nt.links.new(mix.outputs[0],nt.nodes.get('Material Output').inputs['Surface'])
for j in range(6):
 ground.hide_render=j not in [0,5];ground.keyframe_insert('hide_render',frame=j*100+1)
scene.frame_set(1)

scene.frame_end=501;scene.frame_set(1);bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=BASE+'/model/应县木塔_六幕光影.blend')
for j,label in enumerate(labels):
 scene.frame_set(j*100+1);scene.render.filepath=BASE+'/渲染验证/Blender_0'+str(j+1)+'_'+label+'.png';bpy.ops.render.render(write_still=True);print('FRAME_READY',j+1,flush=True)
print('SIX_RENDERS_READY',flush=True)
