"""Lossless component deduplication of the approved Blender mesh.
The asset describes shared parts and their actual transforms in plain JSON.
No binary wrapping, runtime decompression, network loading or WASM required.
"""
import bpy, json, math, os, re
from collections import defaultdict
from mathutils import Vector
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
templates=[];template_map={};objects=[]
sources=[o for o in bpy.context.scene.objects if o.type=='MESH' and o.parent and re.match(r'^Level_\d+$',o.parent.name)]
for o in sources:
    name=o.name
    # Individual floor planks are replaced by continuous octagonal decks in
    # minitool/pagoda.js, at their original heights and with the stairwell open.
    if re.search('筒瓦|木板拼缝|屋架檩条|屋架顺梁|实铺木地板|匾额_.*墨书',name):continue
    m=o.data;m.calc_loop_triangles();nv=len(m.vertices);parents=list(range(nv))
    def find(i):
        while parents[i]!=i:parents[i]=parents[parents[i]];i=parents[i]
        return i
    for e in m.edges:
        a,b=e.vertices;parents[find(b)]=find(a)
    parts=defaultdict(list);triangles=defaultdict(list)
    for i in range(nv):parts[find(i)].append(i)
    for tri in m.loop_triangles:triangles[find(tri.vertices[0])].append(list(tri.vertices))
    instances=[]
    for partnum,(root,vertices) in enumerate(parts.items()):
        # Curved rafter ends are visible; their continuation is concealed by the deck.
        if '椽子' in name and partnum%8<7:continue
        if len(triangles[root])==0:continue
        coords=[o.matrix_world@m.vertices[i].co for i in vertices]
        center=sum(coords,Vector())/len(coords)
        octant=round(math.atan2(center.y,center.x)/(math.pi/4))%8
        angle=octant*math.pi/4;c=math.cos(angle);s=math.sin(angle)
        local=[Vector((c*(v.x-center.x)+s*(v.y-center.y),-s*(v.x-center.x)+c*(v.y-center.y),v.z-center.z)) for v in coords]
        lo=Vector(tuple(min(v[k] for v in local) for k in range(3)));hi=Vector(tuple(max(v[k] for v in local) for k in range(3)))
        scale=hi-lo;origin=(hi+lo)*.5
        scale=Vector(tuple(max(v,.0001) for v in scale))
        normalized=[round((v[k]-origin[k])/scale[k]*10000) for v in local for k in range(3)]
        lookup={idx:k for k,idx in enumerate(vertices)}
        idx=[lookup[i] for tri in triangles[root] for i in tri]
        key=(tuple(normalized),tuple(idx))
        tid=template_map.get(key)
        if tid is None:
            tid=len(templates);template_map[key]=tid;templates.append({'p':normalized,'i':idx})
        center+=Vector((c*origin.x-s*origin.y,s*origin.x+c*origin.y,origin.z))
        instances.append([tid,round(center.x*1000),round(center.y*1000),round(center.z*1000),octant,*[round(v*1000) for v in scale]])
    objects.append({'name':name,'level':int(o.parent.name.split('_')[1]),'material':m.materials[0].name,'parts':instances})
out=os.path.join(ROOT,'scripts','mobile-parts-raw.json')
with open(out,'w') as f:json.dump({'templates':templates,'objects':objects},f,ensure_ascii=False,separators=(',',':'))
print('ORIGINAL_PARTS',len(templates),sum(len(o['parts']) for o in objects),os.path.getsize(out))
