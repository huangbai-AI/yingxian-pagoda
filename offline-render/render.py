"""Blender 后台执行；默认制作 1.5 秒斗栱样片，--preview 仅出首帧。"""
import bpy, math, sys, re
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'offline-render'
args=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else []
preview='--preview' in args
count=36
final='--final' in args
bpy.ops.wm.open_mainfile(filepath=str(ROOT/'model/应县木塔_环境精修.blend'))
s=bpy.context.scene
for o in s.objects:
 o.animation_data_clear()
 if o.name.startswith('Level_'):o.location.z=8 if o.name=='Level_3' else 0
 if o.type=='MESH':o.hide_render=not(o.parent and o.parent.name=='Level_3') or bool(re.search('匾额|木楼梯|层间承|层间拉结',o.name))
# 真实木纹高度、微倒角与粗糙度仍保留为可编辑节点。
for name in ['古木','浅木','暗木','朱漆']:
 m=bpy.data.materials[name];nt=m.node_tree;p=next(n for n in nt.nodes if n.type=='BSDF_PRINCIPLED')
 color=nt.nodes.get('实木_color');height=nt.nodes.get('实木_height')
 tint=nt.nodes.new('ShaderNodeMixRGB');tint.blend_type='MULTIPLY';tint.inputs[0].default_value=1
 tint.inputs[2].default_value={'古木':(.49,.38,.26,1),'浅木':(.66,.52,.35,1),'暗木':(.23,.18,.13,1),'朱漆':(.4,.23,.14,1)}[name]
 nt.links.new(color.outputs['Color'],tint.inputs[1]);nt.links.new(tint.outputs[0],p.inputs['Base Color'])
 bump=nt.nodes.new('ShaderNodeBump');bump.inputs['Strength'].default_value=.3;bump.inputs['Distance'].default_value=.018
 if p.inputs['Normal'].is_linked:nt.links.new(p.inputs['Normal'].links[0].from_socket,bump.inputs['Normal'])
 nt.links.new(height.outputs['Color'],bump.inputs['Height'])
 bevel=nt.nodes.new('ShaderNodeBevel');bevel.samples=4;bevel.inputs['Radius'].default_value=.018
 nt.links.new(bump.outputs['Normal'],bevel.inputs['Normal']);nt.links.new(bevel.outputs[0],p.inputs['Normal'])
# 小面积主光、宽阔弱补光，让榫接处保留真实遮挡和反弹光。
aim=Vector((.2,-11.4,43.4))
for name,loc,power,size,color in [
 ('暖侧光',(-3,-18,48),1300,4,(1,.79,.56)),
 ('冷天光',(6,-18,44),420,7,(.59,.75,.85)),
 ('檐口反光',(1,-7,46),700,3,(1,.77,.5))]:
 d=bpy.data.lights.new(name,'AREA');d.energy=power;d.shape='DISK';d.size=size;d.color=color
 o=bpy.data.objects.new(name,d);s.collection.objects.link(o);o.location=loc;o.rotation_euler=(aim-o.location).to_track_quat('-Z','Y').to_euler()
s.world.use_nodes=True;nt=s.world.node_tree;nt.nodes.clear();out=nt.nodes.new('ShaderNodeOutputWorld');bg=nt.nodes.new('ShaderNodeBackground');bg.inputs[0].default_value=(.19,.27,.3,1);bg.inputs[1].default_value=.16;nt.links.new(bg.outputs[0],out.inputs[0])
d=bpy.data.cameras.new('样片镜头');cam=bpy.data.objects.new('样片镜头',d);s.collection.objects.link(cam);s.camera=cam
d.sensor_fit='VERTICAL';d.sensor_height=24;d.lens=24/(2*math.tan(math.radians(44)/2));d.shift_x=-.12*16/9
focus=bpy.data.objects.new('对焦点',None);s.collection.objects.link(focus);focus.location=aim
d.dof.use_dof=True;d.dof.focus_object=focus;d.dof.aperture_fstop=4;d.dof.aperture_blades=8
s.render.engine='CYCLES';s.cycles.samples=96;s.cycles.use_denoising=True;s.cycles.adaptive_threshold=.018;s.cycles.max_bounces=8;s.cycles.diffuse_bounces=4;s.cycles.sample_clamp_indirect=4
prefs=bpy.context.preferences.addons['cycles'].preferences
try:
 prefs.compute_device_type='METAL';prefs.get_devices()
 for device in prefs.devices:device.use=device.type=='METAL'
 s.cycles.device='GPU'
except Exception:s.cycles.device='CPU'
s.cycles.device='CPU';s.cycles.denoising_use_gpu=False;s.render.threads_mode='FIXED';s.render.threads=6
s.render.use_compositing=False
s.render.resolution_x=1920 if final else (1280 if preview else 960);s.render.resolution_y=1080 if final else (720 if preview else 540);s.cycles.samples=192 if final else (96 if preview else 48);s.render.resolution_percentage=100;s.render.fps=24;s.render.image_settings.file_format='PNG';s.render.image_settings.color_mode='RGBA';s.render.film_transparent=True;s.render.use_persistent_data=True
s.view_settings.view_transform='AgX';s.view_settings.exposure=.25
s.frame_start=1;s.frame_end=count
# 每帧计算同一条连续弧线，不使用静帧推拉伪装三维运动。
def pose(frame):
 t=(frame-1)/(count-1);t=t*t*(3-2*t)
 cam.location=(-2.8+t*.65,-14.8+t*.45,42.65+t*.35)
 cam.rotation_euler=(aim-cam.location).to_track_quat('-Z','Y').to_euler()
 cam.keyframe_insert('location',frame=frame);cam.keyframe_insert('rotation_euler',frame=frame)
for frame in range(1,count+1):pose(frame)
s.frame_set(1)
frames=OUT/('frames-final' if final else ('still' if preview else 'frames'));frames.mkdir(exist_ok=True)
bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'斗栱离线样片.blend'))
for frame in ([1] if preview else range(1,count+1)):
 path=frames/f'{frame:04}.png'
 if path.exists() and not preview:continue
 s.frame_set(frame);s.render.filepath=str(path);bpy.ops.render.render(write_still=True);print('FRAME_READY',frame,flush=True)
