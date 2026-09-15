# 用 Blender 打开 model/应县木塔_六幕光影.blend 后运行。
# 输出首页和斗栱两张定帧样片；不是完整滚动序列。
import bpy,os,math,json
from mathutils import Vector
BASE=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
p=BASE+'/model/对齐设计与渲染.py';setup=open(p).read().split("for j,label in enumerate(['初见'")[0]
exec(compile(setup,p,'exec'),{'__file__':p,'__name__':'__main__'})
s=bpy.context.scene;cam=s.camera;s.render.resolution_x=1008;s.render.resolution_y=568;s.render.resolution_percentage=100;s.cycles.samples=64;s.cycles.adaptive_threshold=.025;s.cycles.use_denoising=True;s.render.use_persistent_data=True;s.view_settings.exposure=.15
cam.data.sensor_fit='VERTICAL';cam.data.sensor_height=24
for node in s.world.node_tree.nodes:
 if node.type=='BACKGROUND':node.inputs['Strength'].default_value=.15
for name,color in {'古木':(.36,.22,.115,1),'浅木':(.57,.37,.20,1),'暗木':(.14,.09,.055,1),'朱漆':(.32,.13,.07,1)}.items():
 m=bpy.data.materials.get(name)
 if m:
  for n in m.node_tree.nodes:
   if n.type=='MIX_RGB' and n.blend_type=='MULTIPLY':n.inputs[2].default_value=color
for name in ['古木','浅木','暗木','朱漆']:
 m=bpy.data.materials[name];nt=m.node_tree;pbr=next(n for n in nt.nodes if n.type=='BSDF_PRINCIPLED');normal=pbr.inputs['Normal'].links[0].from_socket
 height=nt.nodes.get('实木_height');bump=nt.nodes.new('ShaderNodeBump');bump.inputs['Strength'].default_value=.35;bump.inputs['Distance'].default_value=.014;nt.links.new(height.outputs['Color'],bump.inputs['Height']);nt.links.new(normal,bump.inputs['Normal'])
 bevel=nt.nodes.new('ShaderNodeBevel');bevel.samples=4;bevel.inputs['Radius'].default_value=.028;nt.links.new(bump.outputs['Normal'],bevel.inputs['Normal']);nt.links.new(bevel.outputs['Normal'],pbr.inputs['Normal'])
focus=bpy.data.objects.new('样片对焦点',None);s.collection.objects.link(focus);cam.data.dof.focus_object=focus
nt=s.compositing_node_group;plate=next(n for n in nt.nodes if n.type=='IMAGE');scale=next(n for n in nt.nodes if n.type=='SCALE')
for j,pos,aim,fov,shift in [(0,(34,-92,18),(0,0,32),42,0),(3,(3.6,-13.9,43.25),(.2,-11,43.7),42,.14)]:
 s.frame_set(j*100+1);cam.animation_data_clear();cam.data.animation_data_clear();cam.location=pos;cam.rotation_euler=(Vector(aim)-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.lens=24/(2*math.tan(math.radians(fov)/2));cam.data.shift_x=-shift*(1008/568);cam.data.shift_y=0
 focus.location=aim if j==0 else (.7,-11.9,43.55);cam.data.dof.use_dof=j==3;cam.data.dof.aperture_fstop=1.4;cam.data.dof.aperture_blades=8
 params=[('暖金主光',(34,-35,57),95000,11,(1,.78,.52)),('墨绿天光',(-25,-45,30),16000,35,(.58,.73,.78)),('檐口轮廓光',(18,28,52),135000,14,(1,.68,.35))] if j==0 else [('暖金主光',(8,-19,47),5000,4,(1,.81,.59)),('墨绿天光',(-6,-19,43),1000,8,(.65,.78,.85)),('檐口轮廓光',(3,-5,48),4500,3,(1,.74,.46))]
 for name,loc,energy,size,color in params:
  o=s.objects.get(name);o.animation_data_clear();o.data.animation_data_clear();o.location=loc;o.data.energy=energy;o.data.size=size;o.data.color=color;o.rotation_euler=(Vector(aim)-o.location).to_track_quat('-Z','Y').to_euler()
 plate.image=bpy.data.images.load(BASE+'/yingxian-pagoda/public/environment/'+('atmosphere.png' if j==0 else 'chamber-haze.png'),check_existing=True);scale.inputs['X'].default_value=1008/plate.image.size[0];scale.inputs['Y'].default_value=568/plate.image.size[1]
 s.render.filepath=BASE+'/质感与镜头对照/'+('首页_预渲染样片.png' if j==0 else '斗栱_预渲染样片.png');print('START_SAMPLE',j,flush=True);bpy.ops.render.render(write_still=True);print('READY_SAMPLE',j,flush=True)
bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=BASE+'/质感与镜头对照/质感样片.blend')
