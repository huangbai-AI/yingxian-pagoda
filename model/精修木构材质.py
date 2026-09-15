import bpy,os,math,random,json
from mathutils import Vector
BASE=os.path.dirname(os.path.dirname(os.path.abspath(__file__)));s=bpy.context.scene;s.frame_set(1)
if s.get('timber_refined_v5'):raise RuntimeError('本场景已经完成木材精修，请使用未精修的模型副本执行。')
root=bpy.data.collections.get('应县木塔 | 1056');timber=['古木','浅木','暗木','朱漆']
images={}
for name,file in [('color','timber-color.jpg'),('normal','timber-normal.jpg'),('rough','timber-roughness.jpg'),('height','timber-height.png')]:
 image=bpy.data.images.load(BASE+'/yingxian-pagoda/public/materials/'+file,check_existing=True);image.colorspace_settings.name='sRGB' if name=='color' else 'Non-Color';image.use_fake_user=True;image.pack();images[name]=image
for name in timber:
 m=bpy.data.materials.get(name)
 if not m:continue
 nt=m.node_tree;nt.nodes.clear();out=nt.nodes.new('ShaderNodeOutputMaterial');p=nt.nodes.new('ShaderNodeBsdfPrincipled');nt.links.new(p.outputs[0],out.inputs['Surface'])
 uv=nt.nodes.new('ShaderNodeTexCoord');mapping=nt.nodes.new('ShaderNodeVectorMath');mapping.operation='MULTIPLY';mapping.inputs[1].default_value=(.82,.82,1);nt.links.new(uv.outputs['UV'],mapping.inputs[0])
 textures={}
 for k in images:
  tex=nt.nodes.new('ShaderNodeTexImage');tex.name='实木_'+k;tex.image=images[k];tex.extension='REPEAT';nt.links.new(mapping.outputs[0],tex.inputs['Vector']);textures[k]=tex
 color=nt.nodes.new('ShaderNodeMixRGB');color.blend_type='MULTIPLY';color.inputs[0].default_value=1;color.inputs[2].default_value={'古木':(.78,.51,.30,1),'浅木':(.98,.73,.45,1),'暗木':(.41,.30,.21,1),'朱漆':(.60,.31,.18,1)}[name];nt.links.new(textures['color'].outputs['Color'],color.inputs[1]);nt.links.new(color.outputs[0],p.inputs['Base Color'])
 normal=nt.nodes.new('ShaderNodeNormalMap');normal.inputs['Strength'].default_value=.65;nt.links.new(textures['normal'].outputs['Color'],normal.inputs['Color']);nt.links.new(normal.outputs[0],p.inputs['Normal']);nt.links.new(textures['rough'].outputs['Color'],p.inputs['Roughness'])
 p.inputs['Specular IOR Level'].default_value=.28
# Rotate the UV coordinates so the scanned grain follows the long axis of each timber.
for o in root.all_objects:
 if o.type!='MESH' or not o.data.materials or o.data.materials[0].name not in timber:continue
 for loop in o.data.uv_layers.active.data if o.data.uv_layers.active else []:
  u,v=loop.uv;loop.uv=(v,u)
 for mod in o.modifiers:
  if mod.type=='BEVEL':mod.width=.025 if '斗栱' in o.name or '昂嘴' in o.name else .014;mod.segments=3
# Shallow grooves are applied later, to individual closed blocks only.
cuts_total=0
# Export the same connected building, with the additional close-up detail.
bpy.ops.object.select_all(action='DESELECT')
levels=[o for o in s.objects if o.name.startswith('Level_') and o.name!='Level_7']
for o in list(levels)+[o for o in s.objects if o.parent in levels]:o.hide_set(False);o.select_set(True)
bpy.ops.export_scene.gltf(filepath=BASE+'/model/应县木塔_通用.glb',export_format='GLB',use_selection=True,use_active_scene=True,export_apply=True,export_extras=True,export_animations=False,export_cameras=False,export_lights=False,export_yup=True)
# Re-evaluate visibility animation and save an editable upgraded lighting scene.
s['timber_refined_v5']=True;s.frame_set(2);s.frame_set(1);bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=BASE+'/model/应县木塔_六幕光影.blend')
print('UPGRADE_DONE',cuts_total,flush=True)
