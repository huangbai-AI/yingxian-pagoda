"""Bake six directional contact-occlusion samples per original component.
This is done once in Blender, so the phone needs no costly contact-shadow pass.
Only the saved source is read; it is never overwritten.
"""
import bpy,json,os,math
from mathutils import Vector
from mathutils.bvhtree import BVHTree
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
path=os.path.join(ROOT,'scripts','mobile-parts-raw.json')
with open(path) as f:data=json.load(f)
axes=[Vector((1,0,0)),Vector((-1,0,0)),Vector((0,1,0)),Vector((0,-1,0)),Vector((0,0,1)),Vector((0,0,-1))]
for level in range(7):
    verts=[];faces=[]
    for o in bpy.context.scene.objects:
        if o.type!='MESH' or not o.parent or o.parent.name!=f'Level_{level}':continue
        offset=len(verts);verts.extend(o.matrix_world@v.co for v in o.data.vertices)
        faces.extend(tuple(i+offset for i in p.vertices) for p in o.data.polygons)
    if not verts:continue
    bvh=BVHTree.FromPolygons(verts,faces,all_triangles=False)
    for o in data['objects']:
        if o['level']!=level:continue
        for p in o['parts']:
            _,x,y,z,oct,sx,sy,sz=p[:8];center=Vector((x/1000,y/1000,z/1000));sizes=[sx/1000,sy/1000,sz/1000]
            c=math.cos(oct*math.pi/4);s=math.sin(oct*math.pi/4)
            def rotate(v):return Vector((c*v.x-s*v.y,s*v.x+c*v.y,v.z))
            ao=[]
            for k,n in enumerate(axes):
                start=center+rotate(n)*(sizes[k//2]*.5+.025)
                u=axes[2] if k//2==0 else axes[0];v=n.cross(u)
                blocked=0
                for direction in [n,n+u*.85,n-u*.85,n+v*.85,n-v*.85]:
                    direction=rotate(direction.normalized());hit,normal,index,distance=bvh.ray_cast(start,direction,2.2)
                    if hit is not None:blocked+=1-min(distance/2.2,1)*.45
                ao.append(round(255*(1-.64*blocked/5)))
            p[8:]=ao
    print('Contact shadows baked:',level,flush=True)
with open(path,'w') as f:json.dump(data,f,ensure_ascii=False,separators=(',',':'))
