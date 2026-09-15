"""原生1080p适度景深版本；--preview首帧，默认渲染全部帧。"""
import bpy,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parent;OUT=ROOT/'sharp';OUT.mkdir(exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(ROOT/'refined/斗栱质感精修.blend'))
s=bpy.context.scene;s.camera.data.dof.use_dof=True;s.camera.data.dof.aperture_fstop=8
s.render.resolution_x=1920;s.render.resolution_y=1080;s.render.resolution_percentage=100
s.cycles.samples=96;s.cycles.adaptive_threshold=.018;s.cycles.adaptive_min_samples=16;s.cycles.use_denoising=True;s.cycles.denoising_prefilter='ACCURATE';s.cycles.use_animated_seed=False
s.cycles.max_bounces=6;s.cycles.diffuse_bounces=3;s.cycles.device='CPU';s.render.threads_mode='FIXED';s.render.threads=6;s.render.use_persistent_data=True;s.render.image_settings.color_mode='RGBA'
# 构件已有几何倒角；移除额外的着色倒角，使用显卡加速高清逐帧渲染。
for m in bpy.data.materials:
 if not m.use_nodes:continue
 nt=m.node_tree
 for n in list(nt.nodes):
  if n.type!='BEVEL':continue
  source=n.inputs['Normal'].links[0].from_socket if n.inputs['Normal'].is_linked else None
  for dest in [l.to_socket for l in n.outputs[0].links]:
   if source:nt.links.new(source,dest)
  nt.nodes.remove(n)
prefs=bpy.context.preferences.addons['cycles'].preferences
prefs.compute_device_type='METAL';prefs.get_devices()
for device in prefs.devices:device.use=device.type=='METAL'
s.cycles.device='GPU';s.cycles.denoising_use_gpu=False
s.frame_set(1);bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'斗栱原生高清.blend'))
frames=OUT/'frames-dof';frames.mkdir(exist_ok=True)
for f in ([1] if '--preview' in sys.argv else range(1,37)):
 p=frames/f'{f:04}.png'
 if p.exists():continue
 s.frame_set(f);s.render.filepath=str(p);bpy.ops.render.render(write_still=True);print('SHARP_FRAME',f,flush=True)
