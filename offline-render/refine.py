"""精修离线斗栱副本；默认高清首帧，--animation 输出连续36帧。"""
import bpy, math, sys, json
import numpy as np
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parent
OUT=ROOT/'refined';OUT.mkdir(exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(ROOT/'斗栱离线样片.blend'))
s=bpy.context.scene
# 端面使用独立年轮与微孔材质，避免扫描贴图在木块末端被拉伸。
m=bpy.data.materials.new('旧木端面_年轮');m.use_nodes=True;nt=m.node_tree;p=nt.nodes.get('Principled BSDF');p.inputs['Roughness'].default_value=.87;p.inputs['Specular IOR Level'].default_value=.2
uv=nt.nodes.new('ShaderNodeTexCoord');shift=nt.nodes.new('ShaderNodeVectorMath');shift.operation='ADD';shift.inputs[1].default_value=(-.5,-.5,0);nt.links.new(uv.outputs['UV'],shift.inputs[0])
wave=nt.nodes.new('ShaderNodeTexWave');wave.wave_type='RINGS';wave.rings_direction='Z';wave.inputs['Scale'].default_value=36;wave.inputs['Distortion'].default_value=8;wave.inputs['Detail Scale'].default_value=1.6;nt.links.new(shift.outputs[0],wave.inputs[0])
ramp=nt.nodes.new('ShaderNodeValToRGB');ramp.color_ramp.elements[0].position=.22;ramp.color_ramp.elements[0].color=(.10,.059,.029,1);ramp.color_ramp.elements[1].position=.82;ramp.color_ramp.elements[1].color=(.135,.085,.044,1);nt.links.new(wave.outputs['Fac'],ramp.inputs[0]);nt.links.new(ramp.outputs['Color'],p.inputs['Base Color'])
noise=nt.nodes.new('ShaderNodeTexNoise');noise.inputs['Scale'].default_value=95;nt.links.new(uv.outputs['UV'],noise.inputs[0]);bump=nt.nodes.new('ShaderNodeBump');bump.inputs['Strength'].default_value=.16;bump.inputs['Distance'].default_value=.003;nt.links.new(noise.outputs['Fac'],bump.inputs['Height']);nt.links.new(bump.outputs[0],p.inputs['Normal'])
report={'uv_components':0,'endgrain_faces':0,'unchanged_geometry':True}
for o in s.objects:
 if o.type!='MESH' or o.hide_render or not o.data.materials:continue
 if o.data.materials[0].name not in ['古木','浅木','暗木','朱漆']:continue
 if not any(k in o.name for k in ['斗栱','昂嘴','柱','枋','梁','栏']):continue
 me=o.data;me.materials.append(m);slot=len(me.materials)-1
 parent=list(range(len(me.vertices)))
 def find(x):
  while parent[x]!=x:parent[x]=parent[parent[x]];x=parent[x]
  return x
 for e in me.edges:
  a,b=map(find,e.vertices);parent[a]=b
 groups={}
 for v in me.vertices:groups.setdefault(find(v.index),[]).append(v.index)
 frames={};coords=np.array([v.co[:] for v in me.vertices])
 for root,ids in groups.items():
  if len(ids)<4:continue
  pts=coords[ids];center=pts.mean(axis=0);cov=(pts-center).T@(pts-center);values,vectors=np.linalg.eigh(cov);axis=vectors[:,-1]
  if axis[np.argmax(np.abs(axis))]<0:axis=-axis
  elongation=values[-1]/max(values[-2],1e-8)
  if elongation<2.3:continue
  side=vectors[:,0];other=np.cross(axis,side);frames[root]=(center,axis,side,other)
  report['uv_components']+=1
 uv=me.uv_layers.active or me.uv_layers.new(name='TimberUV')
 for f in me.polygons:
  info=frames.get(find(f.vertices[0]))
  if info is None:continue
  c,axis,side,other=info;normal=np.array(f.normal[:]);end=abs(normal@axis)>.86
  if end:f.material_index=slot;report['endgrain_faces']+=1
  tangent=np.cross(normal,axis);tangent/=max(np.linalg.norm(tangent),1e-8)
  for li in f.loop_indices:
   v=coords[me.loops[li].vertex_index]-c
   uv.data[li].uv=(float(v@side*.6+.5),float(v@other*.6+.5)) if end else (float(v@tangent*.38),float(v@axis*.25))
# 降低过强凹凸，保留旧木表面，而非石头般的凹槽。
for name in ['古木','浅木','暗木','朱漆']:
 mat=bpy.data.materials[name]
 for n in mat.node_tree.nodes:
  if n.type=='NORMAL_MAP':n.inputs['Strength'].default_value=.28
  if n.type=='BUMP':n.inputs['Strength'].default_value=.18;n.inputs['Distance'].default_value=.008
  if n.type=='BEVEL':n.inputs['Radius'].default_value=.012
# 彩画表层加入低对比磨损与细微起伏。
for name in ['彩画青','彩画土黄']:
 mat=bpy.data.materials.get(name)
 if not mat:continue
 nt=mat.node_tree;p=next(n for n in nt.nodes if n.type=='BSDF_PRINCIPLED');base=tuple(p.inputs['Base Color'].default_value)
 noise=nt.nodes.new('ShaderNodeTexNoise');noise.inputs['Scale'].default_value=24;noise.inputs['Detail'].default_value=3
 ramp=nt.nodes.new('ShaderNodeValToRGB');ramp.color_ramp.elements[0].color=tuple(v*.58 for v in base[:3])+(1,);ramp.color_ramp.elements[1].color=tuple(v*.92 for v in base[:3])+(1,);nt.links.new(noise.outputs['Fac'],ramp.inputs[0]);nt.links.new(ramp.outputs['Color'],p.inputs['Base Color'])
 bump=nt.nodes.new('ShaderNodeBump');bump.inputs['Strength'].default_value=.14;bump.inputs['Distance'].default_value=.002;nt.links.new(noise.outputs['Fac'],bump.inputs['Height']);nt.links.new(bump.outputs[0],p.inputs['Normal']);p.inputs['Roughness'].default_value=.88
cam=s.camera;cam.animation_data_clear();cam.data.animation_data_clear();aim=Vector((.2,-11,43.7));s.objects['对焦点'].location=aim;cam.data.lens=24/(2*math.tan(math.radians(42)/2));cam.data.shift_x=-.14*16/9;cam.data.dof.aperture_fstop=5.6
for name,pos,energy,size,color in [('暖侧光',(7,-18,47.5),2600,5,(1,.83,.65)),('冷天光',(-7,-19,45),850,8,(.68,.80,.9)),('檐口反光',(2,-5,46),500,4,(1,.79,.58))]:
 o=s.objects[name];o.location=pos;o.data.energy=energy;o.data.size=size;o.data.color=color;o.rotation_euler=(aim-o.location).to_track_quat('-Z','Y').to_euler()
for f in range(1,37):
 t=(f-1)/35;t=t*t*(3-2*t);cam.location=(3.9-.6*t,-14.15+.45*t,43.05+.3*t);cam.rotation_euler=(aim-cam.location).to_track_quat('-Z','Y').to_euler();cam.keyframe_insert('location',frame=f);cam.keyframe_insert('rotation_euler',frame=f)
s.view_settings.exposure=.7;s.cycles.adaptive_threshold=.012;s.cycles.samples=128;s.render.resolution_x=1920;s.render.resolution_y=1080;s.render.threads=6;s.frame_set(1)
bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'斗栱质感精修.blend'))
(OUT/'调整记录.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
anim='--animation' in sys.argv
if '--draft' in sys.argv:s.render.resolution_x=960;s.render.resolution_y=540;s.cycles.samples=48
if anim:s.render.resolution_x=960;s.render.resolution_y=540;s.cycles.samples=48;s.cycles.adaptive_threshold=.025
frames=OUT/('frames' if anim else 'still');frames.mkdir(exist_ok=True)
for f in (range(1,37) if anim else [1]):
 path=frames/f'{f:04}.png'
 if anim and path.exists():continue
 s.frame_set(f);s.render.filepath=str(path);bpy.ops.render.render(write_still=True);print('REFINED_FRAME',f,flush=True)
