import bpy,sys,math
from pathlib import Path
from mathutils import Vector
root=Path(__file__).resolve().parents[2]
out=root/'work/v18';out.mkdir(parents=True,exist_ok=True)
tag=sys.argv[sys.argv.index('--')+1] if '--' in sys.argv else 'before'
s=bpy.context.scene;s.frame_set(1)
for o in s.objects:
 if o.type=='MESH':o.hide_render=not(o.parent and o.parent.name.startswith('Level_') and o.parent.name!='Level_7')
 elif o.type not in ['CAMERA']:o.hide_render=True
s.render.use_compositing=False;s.render.use_sequencer=False;s.use_nodes=False;s.render.engine='BLENDER_WORKBENCH';s.render.use_border=False;s.render.use_crop_to_border=False
s.display.shading.light='STUDIO';s.display.shading.studio_light='paint.sl'
s.display.shading.color_type='SINGLE';s.display.shading.single_color=(.53,.40,.28)
s.display.shading.show_shadows=True;s.display.shading.show_cavity=True
s.display.shading.cavity_type='BOTH';s.display.shading.curvature_ridge_factor=1.3;s.display.shading.curvature_valley_factor=1.3
s.display.shading.background_type='WORLD';s.world.color=(.08,.10,.11)
s.render.resolution_x=1000;s.render.resolution_y=1200;s.render.resolution_percentage=100
s.render.image_settings.file_format='PNG';s.render.film_transparent=False
c=bpy.data.cameras.new('复核相机');cam=bpy.data.objects.new('复核相机',c);s.collection.objects.link(cam);s.camera=cam
for name,pos,aim,scale in [('front',(0,-150,33),(0,0,33),76),('corner',(65,-130,48),(0,0,33),77),('detail',(8,-25,39 if tag=='before' else 36.37),(0,-10.5,35 if tag=='before' else 32.37),13)]:
 cam.location=pos;cam.rotation_euler=(Vector(aim)-cam.location).to_track_quat('-Z','Y').to_euler();c.type='ORTHO';c.ortho_scale=scale
 s.render.filepath=str(out/(tag+'-'+name+'.png'));bpy.ops.render.render(write_still=True)
