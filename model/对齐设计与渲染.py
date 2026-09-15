import bpy,os,math,json
from mathutils import Vector
BASE=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PREVIEW=os.environ.get('PAGODA_PREVIEW')=='1'
scene=bpy.context.scene
scene.frame_set(1)
scene['timber_refined_v5']=True
for o in scene.objects:
 if o.name.startswith('Detail_') or o.name=='Level_7':o.hide_render=True
for node in scene.world.node_tree.nodes:
 if node.type=='BACKGROUND':node.inputs['Strength'].default_value=.28
# Preserve the same building; update only exhibition light and cameras.
for name,pos,power,size,color in [('暖金主光',(34,-22,66),165000,12,(1,.79,.54)),('墨绿天光',(-30,-60,45),18000,45,(.62,.77,.76)),('檐口轮廓光',(36,38,65),150000,20,(1,.72,.40))]:
 o=scene.objects.get(name)
 if o:
  o.location=pos;o.data.energy=power;o.data.size=size;o.data.color=color;o.rotation_euler=(Vector((0,0,32))-o.location).to_track_quat('-Z','Y').to_euler()
for mat in bpy.data.materials:
 if mat.use_nodes and mat.name=='石台':mat.node_tree.nodes.get('Principled BSDF').inputs['Base Color'].default_value=(.14,.16,.145,1)
# Match the quiet, fading courtyard used by the website.
for mat in bpy.data.materials:
 if mat.name.startswith('石材') and mat.use_nodes:
  p=mat.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(.025,.033,.028,1)
for name in ['石铺前庭','连续庭院地面']:
 obj=scene.objects.get(name)
 if not obj:continue
 for mat in obj.data.materials:
  if not mat or not mat.use_nodes:continue
  n=mat.node_tree
  if any(node.bl_idname=='ShaderNodeMapRange' and abs(node.inputs['From Min'].default_value-20)<.001 and abs(node.inputs['From Max'].default_value-62)<.001 for node in n.nodes):continue
  out=n.nodes.get('Material Output');surface=out.inputs['Surface'].links[0].from_socket
  geo=n.nodes.new('ShaderNodeNewGeometry');length=n.nodes.new('ShaderNodeVectorMath');length.operation='LENGTH';n.links.new(geo.outputs['Position'],length.inputs[0])
  fade=n.nodes.new('ShaderNodeMapRange');fade.clamp=True;fade.inputs['From Min'].default_value=20;fade.inputs['From Max'].default_value=62;n.links.new(length.outputs['Value'],fade.inputs['Value'])
  trans=n.nodes.new('ShaderNodeBsdfTransparent');mix=n.nodes.new('ShaderNodeMixShader');n.links.new(fade.outputs['Result'],mix.inputs[0]);n.links.new(surface,mix.inputs[1]);n.links.new(trans.outputs[0],mix.inputs[2]);n.links.new(mix.outputs[0],out.inputs['Surface'])
# Far trees are part of the backdrop, preserving a clear view of the tower.
for o in scene.objects:
 if o.name.startswith('松影'):
  o.animation_data_clear();o.hide_render=True
# Match the six web camera anchors and retain smooth scene continuity.
poses=[([47,36,130],[0,33,0],0,0),([29,59,49],[0,44,0],-.13,-.43),([18.5,63,26],[0,41.5,0],-.15,-.08),([2.8,42.5,16.1],[.18,43.9,11.2],.10,0),([18,33,37],[.5,34.1,8],.09,.13),([50,34,138],[0,33,0],-.16,0)]
cam=scene.camera
for j,(pos,aim,shift,roll) in enumerate(poses):
 frame=100*j+1;cam.location=(pos[0],-pos[2],pos[1]);direction=Vector((aim[0],-aim[2],aim[1]))-cam.location;cam.rotation_euler=direction.to_track_quat('-Z','Y').to_euler();cam.rotation_euler.rotate_axis('Z',-roll);cam.data.shift_x=-shift*(1672/940);cam.keyframe_insert('location',frame=frame);cam.keyframe_insert('rotation_euler',frame=frame);cam.data.keyframe_insert('shift_x',frame=frame)
# Camera-projected environment plate, visible through transparent world rays.
scene.render.film_transparent=True
# Blender 5 compositor node group API.
scene.use_nodes=True
try:nt=scene.node_tree
except AttributeError:
 nt=bpy.data.node_groups.new('设计对齐背景','CompositorNodeTree');scene.compositing_node_group=nt
nt.nodes.clear()
render=nt.nodes.new('CompositorNodeRLayers');plate=nt.nodes.new('CompositorNodeImage');plate.image=bpy.data.images.load(BASE+'/yingxian-pagoda/public/environment/atmosphere.png',check_existing=True)
scale=nt.nodes.new('CompositorNodeScale');scale.inputs['X'].default_value=(668 if PREVIEW else 1336)/plate.image.size[0];scale.inputs['Y'].default_value=(376 if PREVIEW else 752)/plate.image.size[1];nt.links.new(plate.outputs['Image'],scale.inputs['Image'])
over=nt.nodes.new('CompositorNodeAlphaOver');nt.links.new(scale.outputs['Image'],over.inputs['Background']);nt.links.new(render.outputs['Image'],over.inputs['Foreground'])
try:out=nt.nodes.new('CompositorNodeComposite');nt.links.new(over.outputs['Image'],out.inputs['Image'])
except RuntimeError:
 nt.interface.new_socket(name='Image',in_out='OUTPUT',socket_type='NodeSocketColor');out=nt.nodes.new('NodeGroupOutput');nt.links.new(over.outputs['Image'],out.inputs[0])
# Near scenes keep a quiet ink-green background.
quiet=nt.nodes.new('CompositorNodeRGB');quiet.outputs[0].default_value=(.009,.027,.028,1)
scene.view_settings.exposure=-.55
scene.render.use_persistent_data=True
scene.render.resolution_x=1336;scene.render.resolution_y=752;scene.render.resolution_percentage=100;scene.cycles.device='CPU';scene.cycles.denoising_use_gpu=False;scene.cycles.samples=int(os.environ.get('PAGODA_SAMPLES','64'));scene.cycles.use_adaptive_sampling=True;scene.cycles.adaptive_threshold=.045;scene.cycles.adaptive_min_samples=16;scene.cycles.use_denoising=True;scene.render.threads_mode='FIXED';scene.render.threads=6
if PREVIEW:scene.render.resolution_percentage=50;scene.cycles.samples=32;scene.cycles.adaptive_min_samples=16
for j,label in enumerate(['初见','斜向拆层','柱网','斗栱','飞檐归位','全景守护']):
 if PREVIEW and j!=3:continue
 if os.environ.get('PAGODA_FRAME') and j+1!=int(os.environ['PAGODA_FRAME']):continue
 if os.environ.get('PAGODA_FRAMES') and j+1 not in [int(v) for v in os.environ['PAGODA_FRAMES'].split(',')]:continue
 scene.frame_set(j*100+1)
 if j in [0,5]:plate.image=bpy.data.images.load(BASE+'/yingxian-pagoda/public/environment/'+('atmosphere-guard.png' if j==5 and os.path.exists(BASE+'/yingxian-pagoda/public/environment/atmosphere-guard.png') else 'atmosphere.png'),check_existing=True)
 if j in [0,5]:nt.links.new(scale.outputs['Image'],over.inputs['Background'])
 else:
  plate.image=bpy.data.images.load(BASE+'/yingxian-pagoda/public/environment/chamber-haze.png',check_existing=True);nt.links.new(scale.outputs['Image'],over.inputs['Background'])
 scene.render.filepath=BASE+'/渲染验证/Blender_0'+str(j+1)+'_'+label+'.png';scene.render.filepath=BASE+'/../work/v5/render-preview.png' if PREVIEW else scene.render.filepath;print('START',j+1,flush=True);bpy.ops.render.render(write_still=True);print('READY',j+1,flush=True)
if PREVIEW:raise SystemExit
for image in bpy.data.images:
 if image.name.startswith('atmosphere') or image.name.startswith('chamber'):image.use_fake_user=True
scene.frame_set(1);plate.image=bpy.data.images.load(BASE+'/yingxian-pagoda/public/environment/atmosphere.png',check_existing=True);bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=BASE+'/model/应县木塔_六幕光影.blend')
