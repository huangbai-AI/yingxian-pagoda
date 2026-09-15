import bpy, math, random, json, os
from mathutils import Vector
from collections import defaultdict
random.seed(1056)
OUT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# Build a separate scene. Existing scenes are not edited.
scene=bpy.data.scenes.new('应县木塔 · 第三版 · 连续六幕')
bpy.context.window.scene=scene
scene.unit_settings.system='METRIC'
root=bpy.data.collections.new('应县木塔 | 1056'); scene.collection.children.link(root)
mats={}
def mat(name,color,rough=.8,metal=0):
 m=bpy.data.materials.new(name); m.diffuse_color=(*color,1); m.use_nodes=True
 p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(*color,1);p.inputs['Roughness'].default_value=rough;p.inputs['Metallic'].default_value=metal
 mats[name]=m;return m
mat('古木',(.115,.060,.031));mat('朱漆',(.17,.047,.025));mat('浅木',(.24,.14,.075));mat('暗木',(.065,.035,.021));mat('青灰瓦',(.078,.085,.077));mat('瓦脊',(.11,.12,.105));mat('石台',(.48,.44,.36));mat('灰缝',(.29,.27,.22));mat('土朱墙',(.24,.11,.066));mat('鎏金',(.60,.40,.16),.5,.55);mat('铁刹',(.16,.155,.14),.55,.6);mat('彩画青',(.052,.093,.069));mat('彩画土黄',(.26,.18,.082));mat('地面',(.038,.050,.045))
# Real timber color texture with UV-aligned grain, packed for portable Blender and glTF.
woodpath=os.path.join(OUT,'model','材质','古木纹理.png')
woodimage=bpy.data.images.load(woodpath) if os.path.exists(woodpath) else None
for name in ['古木','浅木','暗木','朱漆']:
 m=mats[name];nt=m.node_tree;p=nt.nodes.get('Principled BSDF')
 if woodimage:
  tex=nt.nodes.new('ShaderNodeTexImage');tex.image=woodimage;tex.extension='REPEAT';nt.links.new(tex.outputs['Color'],p.inputs['Base Color'])
  bump=nt.nodes.new('ShaderNodeBump');bump.inputs['Strength'].default_value=.22;bump.inputs['Distance'].default_value=.032;nt.links.new(tex.outputs['Color'],bump.inputs['Height']);nt.links.new(bump.outputs['Normal'],p.inputs['Normal'])
 p.inputs['Roughness'].default_value=.78
buckets={};parts=defaultdict(int);parents={};cols={}
def level(i,label):
 c=bpy.data.collections.new(label);root.children.link(c);cols[i]=c
 o=bpy.data.objects.new('Level_'+str(i),None);c.objects.link(o);o['说明']=label;parents[i]=o
for i,s in enumerate(['00 石砌台基','01 首层与副阶周匝','02 第二明层与暗层','03 第三明层与暗层','04 第四明层与暗层','05 第五明层与暗层','06 攒尖顶与铁刹']):level(i,s)
def geo(i,cat,ma,vs,fs):
 key=(i,cat,ma)
 if key not in buckets:buckets[key]=[[],[]]
 v,f=buckets[key];n=len(v);v.extend(vs);f.extend(tuple(n+x for x in face) for face in fs);parts[cat]+=1

def box(i,cat,ma,c,size,ang=0):
 x,y,z=c;a,b,h=[k/2 for k in size];co=math.cos(ang);si=math.sin(ang)
 vs=[(x+u*co-v*si,y+u*si+v*co,z+w) for u,v,w in [(-a,-b,-h),(a,-b,-h),(a,b,-h),(-a,b,-h),(-a,-b,h),(a,-b,h),(a,b,h),(-a,b,h)]]
 geo(i,cat,ma,vs,[(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)])
def rod(i,cat,ma,a,b,r,n=8,r2=None):
 a,b=Vector(a),Vector(b);d=(b-a).normalized();u=d.cross(Vector((0,0,1)))
 if u.length<.1:u=d.cross(Vector((0,1,0)))
 u.normalize();v=d.cross(u);r2=r if r2 is None else r2
 vs=[tuple(p+rad*(math.cos(k*2*math.pi/n)*u+math.sin(k*2*math.pi/n)*v)) for p,rad in [(a,r),(b,r2)] for k in range(n)]
 fs=[tuple(reversed(range(n))),tuple(range(n,2*n))]+[(k,(k+1)%n,(k+1)%n+n,k+n) for k in range(n)]
 geo(i,cat,ma,vs,fs)
def beam(i,cat,ma,a,b,width=.3,height=None):
 # true rectangular beam along an arbitrary vector
 a,b=Vector(a),Vector(b);d=(b-a).normalized();u=d.cross(Vector((0,0,1)))
 if u.length<.1:u=d.cross(Vector((0,1,0)))
 u.normalize();v=d.cross(u);u*=width/2;v*=(height or width)/2
 vs=[tuple(p+s*u+t*v) for p in [a,b] for s,t in [(-1,-1),(1,-1),(1,1),(-1,1)]]
 geo(i,cat,ma,vs,[(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)])
def octa(i,cat,ma,r,z,h,inner=0):
 vs=[(math.cos(k*math.pi/4)*rad,math.sin(k*math.pi/4)*rad,zz) for zz in [z,z+h] for rad in [r,inner] for k in range(8)]
 fs=[]
 for k in range(8):
  j=(k+1)%8;fs.extend([(k,j,j+16,k+16),(k+8,k+24,j+24,j+8),(k+16,j+16,j+24,k+24),(k,k+8,j+8,j)])
 geo(i,cat,ma,vs,fs)
def point(r,ang,z):return (r*math.cos(ang),r*math.sin(ang),z)
def sidepoint(r,k,t,z,radial=0):
 a=Vector(point(r,k*math.pi/4,z));b=Vector(point(r,(k+1)*math.pi/4,z));p=a.lerp(b,t);p+=Vector((math.cos((k+.5)*math.pi/4)*radial,math.sin((k+.5)*math.pi/4)*radial,0));return tuple(p)
def ring_beams(i,r,z,w,h,cat='梁枋',ma='古木'):
 for k in range(8):beam(i,cat,ma,point(r,k*math.pi/4,z),point(r,(k+1)*math.pi/4,z),w,h)
def bracket(i,p,angle,s=1):
 # One repeating, connected teaching assembly; used identically in the tower and close view.
 origin=Vector(p);rad=Vector((math.cos(angle),math.sin(angle),0));tan=Vector((-math.sin(angle),math.cos(angle),0))
 def local(x,y,z):return origin+rad*x*s+tan*y*s+Vector((0,0,z*s))
 def block(cat,x,y,z,l,w,h,ma='古木'):
  box(i,cat,ma,local(x,y,z),(l*s,w*s,h*s),angle)
 def gong(center,axis,length,width,base):
  # Continuous shaped underside; broad bearing tops and curved bracket arms.
  axis=axis.normalized();normal=Vector((-axis.y,axis.x,0));profile=[]
  for n in range(13):
   t=-1+n/6;profile.append((t*length,base+.26+.11*abs(t)**3))
  for n in range(12,-1,-1):
   t=-1+n/6;profile.append((t*length,base-.11+.25*abs(t)**2))
  vs=[tuple(center+axis*(u*s)+normal*(sg*width*s/2)+Vector((0,0,z*s))) for sg in [-1,1] for u,z in profile]
  N=len(profile);fs=[tuple(reversed(range(N))),tuple(range(N,2*N))]+[(j,(j+1)%N,(j+1)%N+N,j+N) for j in range(N)]
  geo(i,'斗栱栱身','浅木',vs,fs)
 # The cap's bottom reaches the actual column head.
 block('斗栱坐斗',0,0,.08,.76,.76,.38)
 for tier in range(3):
  x=tier*.30;zz=.36+tier*.40;span=.75+tier*.31
  gong(local(x,0,0),tan,span,.27,zz)
  gong(local(x+.1,0,0),rad,.67+tier*.20,.30,zz+.035)
  # Core and bearing blocks touch both crossing arms and the next tier.
  block('斗栱升斗',x+.18,0,zz+.33,.46,.46,.24)
  for sign in [-1,1]:block('斗栱升斗',x,sign*span*.74,zz+.37,.30,.36,.24)
 beam(i,'昂嘴','古木',local(-.5,0,1.25),local(1.95,0,.72),.30*s,.36*s)
 block('斗栱顶枋',.63,0,1.70,.60,3.05,.34)
def roof(i,r,inner,z,rise,tag,support_r,support_z,support_s):
 # Eight pitched surfaces, with a concave section and uplifted corners.
 def p(k,t,u,offset=0):
  rad=inner+(r-inner)*u;a=Vector(point(rad,k*math.pi/4,0));b=Vector(point(rad,(k+1)*math.pi/4,0));v=a.lerp(b,t)
  v.z=z+rise*(1-u)**1.7+.6*u**4+.75*abs(2*t-1)**7*u**3+offset;return v
 for k in range(8):
  vs=[tuple(p(k,j/16,h/10)) for h in range(11) for j in range(17)]
  fs=[(h*17+j,h*17+j+1,(h+1)*17+j+1,(h+1)*17+j) for h in range(10) for j in range(16)]
  geo(i,'屋面_'+tag,'青灰瓦',vs,[tuple(reversed(f)) for f in fs])
  # Closed wooden roof deck with actual thickness, all rafters bear against it.
  underside=[tuple(Vector(v)-Vector((0,0,.18))) for v in vs]
  boundary=list(range(17))+[h*17+16 for h in range(1,11)]+[170+j for j in range(15,-1,-1)]+[h*17 for h in range(9,0,-1)]
  shell=[(a,b,b+187,a+187) for a,b in zip(boundary,boundary[1:]+boundary[:1])]
  geo(i,'望板_'+tag,'暗木',vs+underside,[(a+187,b+187,c+187,d+187) for a,b,c,d in fs]+shell)
  # Concentric purlins follow the eight roof slopes; a continuous ring at every bearing line.
  for u in [.04,.32,.60,.83,.97]:
   for j in range(16):beam(i,'屋架檩条_'+tag,'古木',p(k,j/16,u,-.43),p(k,(j+1)/16,u,-.43),.36,.40)
  # Main radial members run from the inner roof ring to the eave, beneath the rafters.
  for t in [0,1/3,2/3]:
   for j in range(10):beam(i,'屋架顺梁_'+tag,'古木',p(k,t,j/10,-.64),p(k,t,(j+1)/10,-.64),.34,.35)
   u=max(0,min(.97,(support_r-inner)/(r-inner)))
   bearing=p(k,t,u,-.63)
   base=Vector(sidepoint(support_r,k,t,support_z))
   # Vertical timber connects the column-head bracket through to the principal roof member.
   beam(i,'屋架承托_'+tag,'古木',base+Vector((0,0,1.55*support_s)),bearing,.34,.34)
   outward=p(k,t,min(.97,u+.18),-.63)
   beam(i,'屋架撑木_'+tag,'浅木',base+Vector((0,0,.6*support_s)),outward,.24,.26)

  # Individual semi-cylindrical tile segments, with visible overlaps.
  count=int(2*r*math.sin(math.pi/8)/.30)
  for col in range(count):
   t=(col+.5)/count
   for row in range(12):
    u0=row/12;u1=min(1,(row+1.07)/12)
    vv=[]
    for u in [u0,u1]:
     for v in range(5):
      angle=v*math.pi/4
      width=.39/count
      vv.append(tuple(p(k,t+math.cos(angle)*width,u,.085*math.sin(angle)+.045)))
    geo(i,'筒瓦_'+tag,'青灰瓦' if (col+row)%5 else '瓦脊',vv,[(a,a+1,a+6,a+5) for a in range(4)])
   # rafter visible beneath roof at same curve
   for j in range(8):rod(i,'椽子_'+tag,'浅木',p(k,t,j/8,-.255),p(k,t,(j+1)/8,-.255),.075,6)
   # Circular tile-end profiles at every eave tile row.
   tip=p(k,t,1,.05); outward=Vector((math.cos((k+.5)*math.pi/4),math.sin((k+.5)*math.pi/4),0))
   rod(i,'瓦当_'+tag,'瓦脊',tip,tip+outward*.09,.115,10)
  # eave edge / fascia
  for j in range(16):
   beam(i,'檐口_'+tag,'暗木',p(k,j/16,1,-.1),p(k,(j+1)/16,1,-.1),.22,.23)
  for j in range(14):
   rod(i,'垂脊_'+tag,'瓦脊',p(k,0,j/14,.14),p(k,0,(j+1)/14,.14),.19,8)
  # wind bell and ridge ornaments at each hip
  tip=p(k,0,1,.15)
  rod(i,'风铎','铁刹',tip-Vector((0,0,.2)),tip-Vector((0,0,.85)),.025,6)
  rod(i,'风铎','铁刹',tip-Vector((0,0,1.02)),tip-Vector((0,0,.82)),.18,8,.09)
  beam(i,'脊饰','瓦脊',tip,tip+Vector((0,0,.55)),.18,.2)
  for n in range(3):
   q=p(k,0,.74+n*.07,.18);rod(i,'脊饰','瓦脊',q,q+Vector((0,0,.24+n*.035)),.11,7,.075)
# Square stepped base with octagonal upper plinth.
box(0,'台基','石台',(0,0,.7),(34,34,1.4))
box(0,'台基压沿','石台',(0,0,1.48),(34.6,34.6,.18))
octa(0,'台基','石台',17.0,1.57,2.35);octa(0,'台基压沿','石台',17.3,3.92,.28)
# Stone courses and vertical joints.
for k in range(8):
 for row in range(4):
  for j in range(13):
   a=sidepoint(17.015,k,(j+.03)/13,1.58+row*.58);b=sidepoint(17.015,k,(j+.97)/13,1.58+row*.58)
   beam(0,'石砌缝','灰缝',a,b,.025,.024)
   if j<12:beam(0,'石砌缝','灰缝',b,Vector(b)+Vector((0,0,.55)),.024,.024)
for sg in [-1,1]:
 for j in range(18):box(0,'踏步','石台',(0,sg*(17.4+(17-j)*.28),j*.23/2+.11),(6.3,.31,j*.23+.22))
# First story, body behind lower peripheral aisle.
octa(1,'楼板','古木',15.135,4.2,.22)
for r,z0,z1,cat in [(14.5,4.42,10.5,'副阶柱'),(11.4,4.42,16.3,'外槽柱'),(6.4,4.42,16.3,'内槽柱')]:
 for k in range(8):
  for t in ([0,1/3,2/3] if r>10 else [0]):
   p=sidepoint(r,k,t,z0);rod(1,cat,'朱漆',p,(*p[:2],z1),.30 if r>10 else .4,20,.27)
   rod(1,'柱础','石台',(*p[:2],4.2),(*p[:2],4.65),.48,12)
   if r>10:bracket(1,(*p[:2],z1),(k+.5)*math.pi/4,.85)
 for z in [z0+.5,z1-.45]:ring_beams(1,r,z,.35,.48)
# Ground enclosure, doors at front and back, lattice openings.
for k in range(8):
 for j in range(3):
  a=sidepoint(11.32,k,j/3,4.5);b=sidepoint(11.32,k,(j+1)/3,4.5);center=(Vector(a)+Vector(b))/2;width=(Vector(b)-Vector(a)).length-.28;ang=(k+.5)*math.pi/4+math.pi/2
  door=k in [1,5] and j==1
  if not door:box(1,'首层墙','土朱墙',(center.x,center.y,7.3),(width,.25,5.6),ang)
  else:
   for sg in [-1,1]:
    p=center+Vector((math.cos(ang),math.sin(ang),0))*sg*width*.39
    box(1,'门扇','暗木',(p.x,p.y,7.0),(width*.19,.22,5.0),ang)
  box(1,'首层墙','土朱墙',(center.x,center.y,13.4),(width,.24,5.8),ang)
roof(1,16.3,11.35,11.45,2.3,'副阶',14.5,10.5,.85)
roof(1,15.15,8.9,17.7,3.7,'首层',11.4,16.3,.85)
# Upper stories with hidden structural layers.
for i,r,zfloor,ztop in [(2,11.5,21.2,26.0),(3,10.9,30.5,35.2),(4,10.2,39.6,44.2),(5,9.7,48.7,53.4)]:
 octa(i,'楼板','古木',r+.7,zfloor,.28,2.3)
 for k in range(8):
  for t in [j/30 for j in range(1,30)]:
   a=sidepoint(2.34,k,t,zfloor+.286);b=sidepoint(r+.66,k,t,zfloor+.286)
   beam(i,'木板拼缝','暗木',a,b,.012,.012)
 # full framework in the dark mezzanine below balcony
 octa(i,'暗层楼板','暗木',r+.1,zfloor-1.9,.24,2.3)
 for rad in [r,r*.56]:
  for k in range(8):
   for t in ([0,1/3,2/3] if rad==r else [0]):
    p=sidepoint(rad,k,t,zfloor-1.65);rod(i,'柱网','朱漆',p,(*p[:2],ztop),.26 if rad==r else .32,16,.24)
    if rad==r:bracket(i,(*p[:2],ztop),(k+.5)*math.pi/4,.72)
   beam(i,'暗层斜撑','浅木',point(rad,k*math.pi/4,zfloor-1.6),point(rad,(k+1)*math.pi/4,zfloor-.1),.28,.32)
  for z in [zfloor-1.65,zfloor-.1,ztop-.4]:ring_beams(i,rad,z,.36,.44)
 for k in range(8):
  # radial beams between inner / outer column rings
  for z in [zfloor-.3,ztop-.3]:beam(i,'径向梁','古木',point(r*.56,k*math.pi/4,z),point(r+.65,k*math.pi/4,z),.37,.48)
  # solid parapet panels and wooden lattice back screens leaving door openings
  rr=r-.95;ang=(k+.5)*math.pi/4+math.pi/2
  for j in range(3):
   a=Vector(sidepoint(rr,k,j/3,zfloor));b=Vector(sidepoint(rr,k,(j+1)/3,zfloor));c=(a+b)/2;w=(b-a).length-.16
   if not (k%2==1 and j==1):
    box(i,'隔扇裙板','土朱墙',(c.x,c.y,zfloor+1.05),(w,.16,1.5),ang)
    for x in range(8):
     p=a.lerp(b,(x+.5)/8);beam(i,'隔扇棂格','浅木',(*p[:2],zfloor+1.8),(*p[:2],ztop-.7),.085,.085)
    for zz in [zfloor+1.8,zfloor+2.35,zfloor+2.9,ztop-.7]:beam(i,'隔扇棂格','古木',(*a[:2],zz),(*b[:2],zz),.1,.1)
  # balcony posts and rails
  rr=r+.55
  for t in [j/12 for j in range(12)]:
   p=sidepoint(rr,k,t,zfloor+.27);rod(i,'栏杆','浅木',p,(*p[:2],zfloor+1.55),.075,6)
   if int(round(t*12))%4==0:rod(i,'望柱','古木',p,(*p[:2],zfloor+1.72),.13,8)
  for zz in [zfloor+.57,zfloor+1.15,zfloor+1.52]:beam(i,'栏杆','浅木',point(rr,k*math.pi/4,zz),point(rr,(k+1)*math.pi/4,zz),.13,.14)
  # diagonal balcony lattice
  for j in range(6):
   a=sidepoint(rr,k,j/6,zfloor+.62);b=sidepoint(rr,k,(j+1)/6,zfloor+1.12);beam(i,'栏杆花格','古木',a,b,.08)
  # flying balcony cantilevers below decking
  for t in [0,1/3,2/3]:bracket(i,sidepoint(r-.2,k,t,zfloor-1.65),(k+.5)*math.pi/4,.60)
  # colour band on lintel, fine repeating motifs
  a=point(r,k*math.pi/4,ztop-.45);b=point(r,(k+1)*math.pi/4,ztop-.45);beam(i,'檐下彩画','彩画青',a,b,.40,.3)
  for j in range(14):
   q=Vector(a).lerp(Vector(b),(j+.5)/14);box(i,'檐下彩画','彩画土黄',q,(.10,.43,.14),ang)
 roof(i,r+2.5,.65 if i==5 else r-2.0,ztop+1.5,4.55 if i==5 else 3.25,'主檐',r,ztop,.72)
# Closed load path between the top beams and the dark layer above.
# Columns taper inward between storeys; each transition has bearing rings and radial ties.
for i,r,z0,rnext,z1 in [(1,11.4,16.3,11.5,19.3),(2,11.5,26,10.9,28.6),(3,10.9,35.2,10.2,37.7),(4,10.2,44.2,9.7,46.8)]:
 for factor in [1,.56]:
  for k in range(8):
   for t in ([0,1/3,2/3] if factor==1 else [0]):
    a=sidepoint(r*factor,k,t,z0-.25);b=sidepoint(rnext*factor,k,t,z1+.12)
    beam(i,'层间承柱','古木',a,b,.40,.44)
  ring_beams(i,rnext*factor,z1-.13,.42,.40,'层间承梁')
 for k in range(8):beam(i,'层间拉结','古木',point(rnext*.56,k*math.pi/4,z1-.14),point(rnext,k*math.pi/4,z1-.14),.40,.40)
# Solid timber stair flights, two supporting stringers, rail posts and landing boards.
for i,z0,z1,x0,x1,y,n in [(1,4.42,21.48,-7.8,6.4,5.3,46),(2,21.48,30.78,-4.6,3.7,4.1,26),(3,30.78,39.88,-4.6,3.7,4.1,26),(4,39.88,48.98,-4.6,3.7,4.1,26)]:
 for j in range(n):
  t=(j+1)/n;x=x0+(x1-x0)*t;z=z0+(z1-z0)*t
  box(i,'木楼梯','古木',(x,y,z-.09),((x1-x0)/n+.05,1.65,.18))
  if j%4==0:
   for sg in [-1,1]:beam(i,'木楼梯栏柱','浅木',(x,y+sg*.8,z-.06),(x,y+sg*.8,z+1),.10,.10)
 for sg in [-1,1]:
  beam(i,'木楼梯梯梁','古木',(x0,y+sg*.64,z0-.1),(x1+.25,y+sg*.64,z1-.1),.24,.40)
  beam(i,'木楼梯扶手','浅木',(x0,y+sg*.8,z0+1),(x1,y+sg*.8,z1+1),.12,.12)
 box(i,'木楼梯平台','古木',(x1+.3,y,z1-.12),(.9,1.8,.24))
# top roof starts at 54.9, apex 58.15; metal finial reaches exactly 67.31.
# Close top inner opening with eight roof apex facets.
for k in range(8):
 a=point(.65,k*math.pi/4,59.45);b=point(.65,(k+1)*math.pi/4,59.45)
 geo(6,'攒尖顶','青灰瓦',[a,b,(0,0,60.0)],[(0,1,2)])
 rod(6,'攒尖脊','瓦脊',a,(0,0,60.0),.16,8)
rod(6,'塔刹','铁刹',(0,0,59.0),(0,0,65.5),.7,16,.24)
for j in range(11):
 zz=60+j*.39;rad=1.13-j*.064
 rod(6,'相轮','铁刹',(0,0,zz),(0,0,zz+.13),rad,24,rad*.98)
rod(6,'宝瓶','铁刹',(0,0,64.6),(0,0,65.5),.32,16,.52)
rod(6,'宝瓶','铁刹',(0,0,65.5),(0,0,65.9),.52,16,.19)
rod(6,'刹尖','铁刹',(0,0,65.9),(0,0,67.31),.12,12,0)
for k in range(8):
 a=point(10.8,k*math.pi/4,55.6);b=Vector((0,0,64.6))
 for j in range(16):
  p=Vector(a).lerp(b,j/16);q=Vector(a).lerp(b,(j+1)/16);p.z-=1.15*math.sin(math.pi*j/16);q.z-=1.15*math.sin(math.pi*(j+1)/16)
  rod(6,'刹链','铁刹',p,q,.028,5)
# Create a compact mesh per level / construction family / material.
for (i,cat,ma),(vs,fs) in buckets.items():
 mesh=bpy.data.meshes.new(f'{i}_{cat}_{ma}');mesh.from_pydata(vs,[],fs);mesh.materials.append(mats[ma]);mesh.update()
 uv=mesh.uv_layers.new(name='TimberUV')
 for face in mesh.polygons:
  ids=list(face.vertices)
  points=[mesh.vertices[j].co for j in ids]
  edges=[points[(j+1)%len(points)]-points[j] for j in range(len(points))]
  axis=max(edges,key=lambda a:a.length).normalized();cross=face.normal.cross(axis).normalized()
  for li in face.loop_indices:
   v=mesh.vertices[mesh.loops[li].vertex_index].co
   uv.data[li].uv=(v.dot(axis)*.34,v.dot(cross)*.34)
 o=bpy.data.objects.new(f'L{i}_{cat}_{ma}',mesh);cols[i].objects.link(o);o.parent=parents[i];o['构件类别']=cat;o['楼层']=i
 if any(t in cat for t in ['筒瓦','屋面','垂脊','瓦当']):
  for f in mesh.polygons:f.use_smooth=True
 if any(t in cat for t in ['斗栱','昂嘴','梁枋','径向梁','层间承','望柱']) and len(mesh.polygons)<12000:
  mod=o.modifiers.new('细磨木缘','BEVEL');mod.width=.018;mod.segments=1
  o.modifiers.new('面部法线','WEIGHTED_NORMAL')
# Plaques, legible text retained and converted only during GLB export.
fontpath=os.path.join(OUT,'model','字体','NotoSerifCJKsc-Regular.otf')
font=bpy.data.fonts.load(fontpath) if os.path.exists(fontpath) else None
for i,title,zz,width,rr in [(2,'万古观瞻',25.1,5.5,11.7),(3,'释迦塔',34.35,5.3,11.1),(4,'天下奇观',43.5,5.0,10.4),(5,'峻极神工',52.7,4.8,9.9)]:
 # South face is between vertices 5 and 6; local label faces toward -Y at side center.
 ang=11*math.pi/8;p=Vector(point(rr*math.cos(math.pi/8),ang,zz));tangent=ang+math.pi/2
 # backing made directly as one mesh
 boxkey=(i,'匾额','暗木');before=len(buckets.get(boxkey,[[],[]])[0]);box(i,'匾额','暗木',p,(width,.22,1.12),tangent)
 vs,fs=buckets[boxkey]
 # only a single backing per level
 mesh=bpy.data.meshes.new('匾');mesh.from_pydata(vs,[],fs);mesh.materials.append(mats['暗木']);o=bpy.data.objects.new('L%d_匾额'%i,mesh);cols[i].objects.link(o);o.parent=parents[i]
 curve=bpy.data.curves.new('题字','FONT');curve.body=title;curve.align_x='CENTER';curve.align_y='CENTER';curve.size=1.65;curve.extrude=.008
 if font:curve.font=font
 text=bpy.data.objects.new('L%d_匾额题字'%i,curve);cols[i].objects.link(text);text.parent=parents[i];text.location=p+Vector((math.cos(ang),math.sin(ang),0))*.13;text.rotation_euler=(math.pi/2,0,tangent);curve.materials.append(mats['鎏金'])
# A separate teaching specimen uses a single complete capital, bracket set and roof bearing.
level(7,'斗栱 · 独立承托标本')
rod(7,'柱头','朱漆',(0,0,-2.5),(0,0,0),.48,24,.44)
box(7,'柱头枋','古木',(0,0,-.4),(3.2,.5,.55))
bracket(7,(0,0,.08),0,1.5)
# Cap directly bears on upper stacked gong. Purlins bear on the cap, rafters bear on purlins.
box(7,'承托顶枋','古木',(1.05,0,2.33),(.62,6.15,.42))
box(7,'后部承托','古木',(-.42,0,1.90),(.55,4.2,.40))
for y in [-2.6,-1.95,-1.3,-.65,0,.65,1.3,1.95,2.6]:
 beam(7,'檐椽','浅木',(-1.5,y,2.65),(2.7,y,2.15),.21,.24)
beam(7,'挑檐檩','古木',(2.35,-3.1,2.02),(2.35,3.1,2.02),.36,.36)
beam(7,'上昂承接','古木',(.85,0,1.65),(2.35,0,2.02),.38,.40)
for (i,cat,ma),(vs,fs) in buckets.items():
 if i!=7:continue
 mesh=bpy.data.meshes.new(f'Detail_{cat}');mesh.from_pydata(vs,[],fs);mesh.materials.append(mats[ma]);mesh.update()
 uv=mesh.uv_layers.new(name='TimberUV')
 for face in mesh.polygons:
  pts=[mesh.vertices[j].co for j in face.vertices];axis=max([pts[(j+1)%len(pts)]-pts[j] for j in range(len(pts))],key=lambda a:a.length).normalized();cross=face.normal.cross(axis).normalized()
  for li in face.loop_indices:
   v=mesh.vertices[mesh.loops[li].vertex_index].co;uv.data[li].uv=(v.dot(axis)*.34,v.dot(cross)*.34)
 o=bpy.data.objects.new(f'Detail_{cat}_{ma}',mesh);cols[7].objects.link(o);o.parent=parents[7]
 bevel=o.modifiers.new('木件边缘','BEVEL');bevel.width=.028;bevel.segments=2
 o.modifiers.new('法线','WEIGHTED_NORMAL')
parents[7].hide_render=True
# Studio lights, camera and ground live outside model export.
studio=bpy.data.collections.new('展示灯光');scene.collection.children.link(studio)
def light(name,pos,power,size,color):
 d=bpy.data.lights.new(name,'AREA');d.energy=power;d.shape='DISK';d.size=size;d.color=color;o=bpy.data.objects.new(name,d);studio.objects.link(o);o.location=pos;o.rotation_euler=(Vector((0,0,28))-o.location).to_track_quat('-Z','Y').to_euler()
light('暖金主光',(55,-38,75),175000,18,(1,.74,.43));light('墨绿天光',(-45,-35,60),45000,55,(.46,.65,.64));light('檐口轮廓光',(15,40,80),165000,25,(1,.69,.36))
world=bpy.data.worlds.new('暖灰天空');world.use_nodes=True;world.node_tree.nodes['Background'].inputs[0].default_value=(.017,.031,.030,1);world.node_tree.nodes['Background'].inputs[1].default_value=.35;scene.world=world
mesh=bpy.data.meshes.new('地');mesh.from_pydata([(-2000,-2000,-.1),(2000,-2000,-.1),(2000,2000,-.1),(-2000,2000,-.1)],[],[(0,1,2,3)]);mesh.materials.append(mats['地面']);ground=bpy.data.objects.new('展示地面',mesh);studio.objects.link(ground)
camdata=bpy.data.cameras.new('建筑相机');cam=bpy.data.objects.new('建筑相机',camdata);studio.objects.link(cam);scene.camera=cam;cam.location=(65,-140,65);target=Vector((0,0,32));cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler();camdata.type='ORTHO';camdata.ortho_scale=83
scene.render.engine='CYCLES';scene.cycles.device='CPU';scene.cycles.denoising_use_gpu=False;scene.cycles.samples=40;scene.cycles.use_denoising=True
scene.render.resolution_x=1200;scene.render.resolution_y=1400;scene.render.resolution_percentage=100
scene.view_settings.view_transform='AgX';scene.render.image_settings.file_format='PNG';scene.render.filepath=OUT+'/model/木塔全景.png'
# Select model only for export, explicit selection, no default objects.
bpy.ops.object.select_all(action='DESELECT')
for i,c in cols.items():
 if i<7:
  for o in c.objects:o.select_set(True)
for screen in bpy.data.screens:
 for area in screen.areas:
  if area.type=='VIEW_3D':
   area.spaces.active.region_3d.view_location=(0,0,32)
   area.spaces.active.region_3d.view_distance=105
   area.spaces.active.region_3d.view_rotation=cam.rotation_euler.to_quaternion()
   area.spaces.active.shading.type='MATERIAL'
bpy.ops.file.pack_all()
bpy.ops.wm.save_as_mainfile(filepath=OUT+'/model/应县木塔.blend')
bpy.ops.export_scene.gltf(filepath=OUT+'/model/应县木塔_通用.glb',export_format='GLB',use_selection=True,use_active_scene=True,export_apply=True,export_extras=True,export_cameras=False,export_lights=False,export_yup=True)
bpy.ops.object.select_all(action='DESELECT')
for o in cols[7].objects:o.select_set(True)
bpy.ops.export_scene.gltf(filepath=OUT+'/model/斗栱标本.glb',export_format='GLB',use_selection=True,use_active_scene=True,export_apply=True,export_yup=True)
for o in cols[7].objects:o.hide_render=True;o.hide_set(True)
bpy.ops.object.select_all(action='DESELECT')
bpy.ops.wm.save_as_mainfile(filepath=OUT+'/model/应县木塔.blend')
report={'height_m':67.31,'base_body_diameter_m':30.27,'objects':sum(len(c.objects) for i,c in cols.items() if i<7),'vertices':sum(len(o.data.vertices) for i,c in cols.items() if i<7 for o in c.objects if o.type=='MESH'),'polygons':sum(len(o.data.polygons) for i,c in cols.items() if i<7 for o in c.objects if o.type=='MESH'),'modeled_parts':dict(parts),'scope':'依据公开尺寸和照片制作的建筑科普重建；非测绘复原。斗栱采用代表性组合，未逐一复刻54种形制；内部佛像、壁画未复原。'}
with open(OUT+'/model/模型信息.json','w') as f:json.dump(report,f,ensure_ascii=False,indent=2)
print('MODEL_READY',json.dumps(report,ensure_ascii=False),flush=True)
bpy.ops.render.render(write_still=True)
# second close view
cam.location=(42,-61,36);target=Vector((0,0,26));cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler();camdata.ortho_scale=27;scene.render.resolution_x=1400;scene.render.resolution_y=1000;scene.render.filepath=OUT+'/model/斗栱与平座.png';bpy.ops.render.render(write_still=True)
# True close view of the same third-storey corner bracket used by the website.
camdata.type='PERSP';camdata.lens=45
cam.location=(4.5,-18.8,37.4);target=Vector((.15,-11.05,36.0));cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler()
scene.render.resolution_x=1600;scene.render.resolution_y=1000;scene.render.filepath=OUT+'/model/塔上斗栱近景.png';bpy.ops.render.render(write_still=True)
print('RENDERS_READY',flush=True)
