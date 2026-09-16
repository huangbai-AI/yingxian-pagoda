import * as THREE from 'three';
const asset=window.PagodaOriginalParts;
delete window.PagodaOriginalParts;

// Coordinates extracted from 应县木塔_牌匾贴图.blend. No replacement tower.
const colors={'古木':0x987956,'浅木':0xb29870,'暗木':0x534537,'朱漆':0x8d6246,'土朱墙':0x8b654f,'风化土朱墙':0x85634f,'石台':0x656961,'风化青石':0x75786d,'青灰瓦':0x626766,'瓦脊':0x656963,'彩画青':0x29463e,'彩画土黄':0xab8e53,'铁刹':0x5f6055};
const heightKnots=[[0,0],[4.42,4.42],[10.5,10.5],[13.75,13.2],[16.3,14.1],[21.48,19.202],[30.78,28.150],[39.88,37.25],[48.98,46.35],[59,55.571],[67.31,67.31],[100,100]];
function modelHeight(z){for(let i=1;i<heightKnots.length;i++){const a=heightKnots[i-1][0],b=heightKnots[i-1][1],c=heightKnots[i][0],d=heightKnots[i][1];if(z<=c)return b+(z-a)/(c-a)*(d-b);}return z;}
export async function buildPagoda(progress){
 const root=new THREE.Group(),levels=[];
 for(let i=0;i<=6;i++){const group=new THREE.Group();group.name='Level_'+i;root.add(group);levels.push(group);}
 const buckets=new Map();
 function bucket(level,cat,material,detail,sector=0){
  const key=[level,cat,material,detail,sector].join('_');
  if(!buckets.has(key))buckets.set(key,{name:'L'+key,level,material,detail,p:[],n:[],uv:[],color:[]});
  return buckets.get(key);
 }
 const category=name=>/木楼梯/.test(name)?'木楼梯':/层间承|层间拉结/.test(name)?'层间承':/匾额/.test(name)?'匾额':/隔扇/.test(name)?'隔扇':/筒瓦|屋面|垂脊|檐口|椽子|脊饰|风铎|攒尖|塔刹|相轮|宝瓶|刹尖|刹链|瓦当|望板|屋架/.test(name)?'屋面':'木构';
 const a=new THREE.Vector3(),b=new THREE.Vector3(),c=new THREE.Vector3(),ab=new THREE.Vector3(),ac=new THREE.Vector3(),n=new THREE.Vector3();
 function append(r,detail){
  const cat=category(r.name),near=detail===1,sealedBracket=detail===2&&/斗栱/.test(r.name),returnRoof=detail===2&&/屋面|望板/.test(r.name),returnCap=detail===2&&/瓦当/.test(r.name);
  for(let partIndex=0;partIndex<r.parts.length;partIndex++){
   if(!near&&/椽子/.test(r.name)&&partIndex%3)continue;
   if(!near&&/檐下彩画/.test(r.name)&&/土黄/.test(r.material)&&partIndex%2)continue;
   const instance=r.parts[partIndex];
   const [tid,x,y,z,oct,sx,sy,sz]=instance,t=asset.templates[tid],cs=Math.cos(oct*Math.PI/4),sn=Math.sin(oct*Math.PI/4);
   // Cull whole spatial sections outside the camera, never individual faces of
   // the close-up solids. This keeps the detail mesh affordable while moving.
   const out=bucket(r.level,cat,r.material,detail,near?Math.floor(oct/2):0);
   // A six-sided front disk preserves the round tile-end silhouette without
   // collapsing the short cylinder into a pointed wedge during the return.
   const cap=[10,12,13,10,13,15,10,15,17,10,17,18];
   const index=returnCap&&t.p.length===60?cap:near?t.medium:returnRoof?t.returnRoof:sealedBracket?t.closed:t.low;
   const coords=t.p.map((v,i)=>v/10000*[sx,sy,sz][i%3]/1000);
   // The source column feet sat 10 mm above their dark-floor bearing surface.
   // Extend only the bottom ring by 12 mm; the column heads stay in place.
   function point(id,target){const k=id*3,seat=/柱网/.test(r.name)?.012*(.5-t.p[k+2]/10000):0;target.set((x/1000+cs*coords[k]-sn*coords[k+1]),z/1000+coords[k+2]-seat,-(y/1000+sn*coords[k]+cs*coords[k+1]));}
   for(let j=0;j<index.length;j+=3){
    point(index[j],a);point(index[j+1],b);point(index[j+2],c);n.crossVectors(ab.subVectors(b,a),ac.subVectors(c,a)).normalize();
    const flatDecor=!near&&/隔扇棂格|檐下彩画|砌石面层|墙脚砌石|墙面立框|额枋压线|门扇板缝|瓦当/.test(r.name);
    if(flatDecor&&!returnCap&&(n.x*x-n.z*y)<.72*Math.hypot(x,y))continue;
    // Interior-facing sides are occluded by the opaque assembled body. Full
    // components are retained in the isolated structural/detail view.
    if(!near&&!sealedBracket&&/斗栱|平座|檐口|梁枋|墙面收边|栏杆|望柱|柱网|外槽柱|副阶柱|椽子/.test(r.name)&&(n.x*x-n.z*y)<-.15*Math.hypot(x,y))continue;
    if(/望板/.test(r.name)&&n.y>.3)continue;
    const roof=/青灰瓦/.test(r.material);
    const angle=Math.round(Math.atan2(-(a.z+b.z+c.z),a.x+b.x+c.x)/(Math.PI/4)-.5)*Math.PI/4+Math.PI/8;
    for(const v of [a,b,c]){
     out.p.push(v.x,v.y,v.z);out.n.push(n.x,n.y,n.z);
     if(roof)out.uv.push((v.x*-Math.sin(angle)-v.z*Math.cos(angle))/.3,Math.hypot(v.x,v.z)/.5);
     else if(/古木|浅木|暗木|朱漆/.test(r.material)){
      const dx=v.x-x/1000,dy=-v.z-y/1000,local=[cs*dx+sn*dy,-sn*dx+cs*dy,v.y-z/1000],norm=[cs*n.x-sn*n.z,-sn*n.x-cs*n.z,n.y];
      const major=sx>=sy&&sx>=sz?0:sy>=sz?1:2,other=[0,1,2].filter(k=>k!==major),cross=Math.abs(norm[other[0]])<Math.abs(norm[other[1]])?other[0]:other[1];
      out.uv.push(local[cross]*1.25+(partIndex*.618033)%1,local[major]*.28);
     }else{const nx=Math.abs(n.x),ny=Math.abs(n.y),nz=Math.abs(n.z);if(ny>nx&&ny>nz)out.uv.push(v.x*.3,v.z*.3);else if(nx>nz)out.uv.push(v.z*.3,v.y*.3);else out.uv.push(v.x*.3,v.y*.3);}
     const localN=[cs*n.x-sn*n.z,-sn*n.x-cs*n.z,n.y];let shade=0,weight=0;
     for(let k=0;k<3;k++){const w=Math.abs(localN[k]);shade+=w*(instance[8+k*2+(localN[k]<0?1:0)]===undefined?255:instance[8+k*2+(localN[k]<0?1:0)]);weight+=w;}
     shade=shade/(Math.max(weight,.001)*255);out.color.push(shade,shade,shade);
    }
   }
  }
 }
 for(let i=0;i<asset.objects.length;i++){
  const r=asset.objects[i];if(/木楼梯|石栏莲头|石栏浮框|柱础下盘/.test(r.name))continue;append(r,0);if(r.level===3){append(r,1);append(r,2);}
  if(i%8===7){if(progress)progress(i/asset.objects.length);await new Promise(resolve=>setTimeout(resolve,0));}
 }
 // Restore the continuous balcony deck omitted by the mobile export. These
 // dimensions match 精修台基与楼板.py; the central stair opening stays open.
 // A ring of 64 triangles replaces hundreds of individual planks per floor.
 for(const [level,radius,height] of [[2,12.2,modelHeight(21.2)],[3,11.6,modelHeight(30.5)],[4,10.9,modelHeight(39.6)],[5,10.4,modelHeight(48.7)]]){
  for(const detail of level===3?[0,1,2]:[0]){
   let out;
   const point=(rad,angle,y)=>new THREE.Vector3(Math.cos(angle)*rad,y,-Math.sin(angle)*rad);
   function quad(vs){for(const ids of [[0,1,2],[0,2,3]]){const va=vs[ids[0]],vb=vs[ids[1]],vc=vs[ids[2]],normal=new THREE.Vector3().crossVectors(vb.clone().sub(va),vc.clone().sub(va)).normalize();for(const v of [va,vb,vc]){out.p.push(v.x,v.y,v.z);out.n.push(normal.x,normal.y,normal.z);out.uv.push(v.x*.8,v.z*.28);const shade=normal.y<-.5?.52:.83;out.color.push(shade,shade,shade);}}}
   for(let k=0;k<8;k++){
    out=bucket(level,'木构','古木',detail,detail===1?Math.floor(k/2):0);
    const a=k*Math.PI/4,b=(k+1)*Math.PI/4;
    const obA=point(radius,a,height),obB=point(radius,b,height),otA=point(radius,a,height+.28),otB=point(radius,b,height+.28),ibA=point(2.3,a,height),ibB=point(2.3,b,height),itA=point(2.3,a,height+.28),itB=point(2.3,b,height+.28);
    quad([otA,otB,itB,itA]);quad([ibA,ibB,obB,obA]);quad([obA,obB,otB,otA]);quad([ibB,ibA,itA,itB]);
   }
  }
 }
 for(const r of buckets.values()){
  const g=new THREE.BufferGeometry();g.setAttribute('position',new THREE.Float32BufferAttribute(r.p,3));g.setAttribute('normal',new THREE.Float32BufferAttribute(r.n,3));g.setAttribute('uv',new THREE.Float32BufferAttribute(r.uv,2));g.setAttribute('color',new THREE.Float32BufferAttribute(r.color,3));g.computeBoundingSphere();
  const material=new THREE.MeshStandardMaterial({name:r.material,color:colors[r.material]||0x86745d,roughness:.9,vertexColors:true});
  const mesh=new THREE.Mesh(g,material);mesh.name=r.name;mesh.userData.detail=r.detail;mesh.userData.triangles=r.p.length/9;levels[r.level].add(mesh);
 }
 // Photo-referenced plaque atlas. The backing timbers come from Blender;
 // only the albedo face is added here so the mobile asset stays compact.
 const plaqueTexture=await new Promise((resolve,reject)=>new THREE.TextureLoader().load('./textures/yingxian-plaques.webp',resolve,undefined,reject));
 plaqueTexture.colorSpace=THREE.SRGBColorSpace;plaqueTexture.flipY=true;plaqueTexture.anisotropy=4;
 const plaqueMaterial=new THREE.MeshStandardMaterial({name:'牌匾墨书',map:plaqueTexture,color:0xffffff,roughness:.94,metalness:0});
 const plaques=[
  [2,'天宮高聳',[-4.136574,22.684984,9.986574],5.5,1.65,[0,.5,.762,1]],
  [3,'釋迦塔',[-3.924443,31.270000,9.474442],1.58,3.2,[.762,0,1,1]],
  [4,'天下奇觀',[-3.676955,40.870000,8.876955],5.0,1.5,[0,0,.762,.5]]
 ];
 for(const [level,title,center,width,height,rect] of plaques){
  const radial=new THREE.Vector3(center[0],0,center[2]).normalize(),tangent=new THREE.Vector3(radial.z,0,-radial.x),up=new THREE.Vector3(0,1,0),c=new THREE.Vector3(...center).addScaledVector(radial,.14);
  const corners=[[-1,-1],[1,-1],[1,1],[-1,1]].map(pair=>c.clone().addScaledVector(tangent,pair[0]*width/2).addScaledVector(up,pair[1]*height/2));
  const positions=[],normals=[];for(const id of [0,1,2,0,2,3]){positions.push(...corners[id]);normals.push(radial.x,radial.y,radial.z);}
  const u0=rect[0],v0=rect[1],u1=rect[2],v1=rect[3],uvCorners=[[u0,v0],[u1,v0],[u1,v1],[u0,v1]],uv=[];for(const id of [0,1,2,0,2,3])uv.push(...uvCorners[id]);
  const geometry=new THREE.BufferGeometry();geometry.setAttribute('position',new THREE.Float32BufferAttribute(positions,3));geometry.setAttribute('normal',new THREE.Float32BufferAttribute(normals,3));geometry.setAttribute('uv',new THREE.Float32BufferAttribute(uv,2));geometry.computeBoundingSphere();
  const plaque=new THREE.Mesh(geometry,plaqueMaterial);plaque.name='L'+level+'_匾额墨书_'+title;plaque.userData.detail=0;levels[level].add(plaque);
 }
 asset.objects.length=0;asset.templates.length=0;
 return root;
}
