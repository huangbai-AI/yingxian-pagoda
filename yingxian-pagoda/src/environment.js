import * as THREE from 'three';

export function buildEnvironment(scene){
 const group=new THREE.Group();group.name='前庭与树影';scene.add(group);
 let seed=1056;const rand=()=>{seed=(seed*1664525+1013904223)>>>0;return seed/4294967296;};
 const materials=[],landNear={value:28},landFar={value:85};
 function material(color,extra={}){const m=new THREE.MeshStandardMaterial({color,roughness:.94,transparent:true,depthWrite:true,...extra});materials.push(m);return m;}
 const stone=material(0x51534d),edge=material(0x454b45),bark=material(0x111913),leaf=material(0x263728);
 const ground=new THREE.Mesh(new THREE.PlaneGeometry(2000,2000),material(0x343c37));ground.rotation.x=-Math.PI/2;ground.position.y=-.19;ground.receiveShadow=true;ground.renderOrder=-2;group.add(ground);
 const canvas=document.createElement('canvas');canvas.width=canvas.height=512;const ctx=canvas.getContext('2d');ctx.fillStyle='#85867e';ctx.fillRect(0,0,512,512);
 for(let i=0;i<28000;i++){const c=Math.round(95+rand()*75);ctx.fillStyle=`rgba(${c},${c},${c-4},.25)`;ctx.fillRect(rand()*512,rand()*512,1+rand()*4,1+rand()*3);}
 const tex=new THREE.CanvasTexture(canvas);tex.wrapS=tex.wrapT=THREE.RepeatWrapping;tex.colorSpace=THREE.SRGBColorSpace;stone.map=tex;stone.bumpMap=tex;stone.bumpScale=.045;stone.roughness=.98;ground.material.map=tex.clone();ground.material.map.repeat.set(800,800);ground.material.color.setHex(0x3c3d37);
 const slabs=new THREE.InstancedMesh(new THREE.BoxGeometry(1.78,.12,1.18),stone,6000);const matrix=new THREE.Matrix4(),quat=new THREE.Quaternion(),sc=new THREE.Vector3();let n=0;
 for(let x=-38;x<39;x++)for(let z=-36;z<42;z++){
  const xx=x*1.81+(z%2)*.905,zz=z*1.21;if(Math.abs(xx)<17.4&&Math.abs(zz)<17.4)continue;
  matrix.compose(new THREE.Vector3(xx,-.08,zz),quat,sc.set(1,.8+rand()*.3,1));slabs.setMatrixAt(n,matrix);slabs.setColorAt(n,new THREE.Color().setRGB(.61+rand()*.18,.61+rand()*.14,.53+rand()*.16));n++;
 }slabs.count=n;slabs.receiveShadow=true;slabs.renderOrder=-1;group.add(slabs);
 const treeMap=new THREE.TextureLoader().load('/environment/pine.png');treeMap.colorSpace=THREE.SRGBColorSpace;
 const treeMat=new THREE.MeshStandardMaterial({map:treeMap,color:0x899079,roughness:1,alphaTest:.4,side:THREE.DoubleSide,transparent:true,depthWrite:true});materials.push(treeMat);
 const treeCards=[];
 for(let i=0;i<22;i++){
  const a=rand()*Math.PI*2,radius=29+rand()*34,x=Math.cos(a)*radius,z=Math.sin(a)*radius;
  if(Math.abs(x)<26||z>42)continue;
  const height=8+rand()*8;
  const card=new THREE.Mesh(new THREE.PlaneGeometry(height*.76,height),treeMat);card.position.set(x,height*.5-1.0,z);card.castShadow=false;card.receiveShadow=true;group.add(card);treeCards.push(card);
  const trunk=new THREE.Mesh(new THREE.CylinderGeometry(.15,.30,height*.65,7),bark);trunk.position.set(x,height*.325-.2,z);trunk.castShadow=true;group.add(trunk);
 }
 // Terrain dissolves into the photographic sky plate; its far edge is never visible.
 for(const m of [stone,ground.material]){
  m.transparent=true;m.alphaHash=false;m.depthWrite=false;m.userData.land=true;
  m.onBeforeCompile=shader=>{shader.uniforms.uLandNear=landNear;shader.uniforms.uLandFar=landFar;
   shader.vertexShader='varying vec3 vLandPosition;\n'+shader.vertexShader;
   shader.vertexShader=shader.vertexShader.replace('#include <begin_vertex>',`#include <begin_vertex>
    vec4 landPosition=vec4(transformed,1.0);
    #ifdef USE_INSTANCING
    landPosition=instanceMatrix*landPosition;
    #endif
    vLandPosition=(modelMatrix*landPosition).xyz;`);
   shader.fragmentShader='uniform float uLandNear; uniform float uLandFar; varying vec3 vLandPosition;\n'+shader.fragmentShader;
   shader.fragmentShader=shader.fragmentShader.replace('#include <alphatest_fragment>',`diffuseColor.a *= 1.0-smoothstep(uLandNear,uLandFar,length(vLandPosition.xz));\n#include <alphatest_fragment>`);
  };
 }
 const posts=new THREE.InstancedMesh(new THREE.BoxGeometry(.35,1.45,.35),edge,200);let pi=0;
 for(const sg of [-1,1]){
  for(let z=-29;z<23;z+=2.8){matrix.makeTranslation(sg*29,.725,z);posts.setMatrixAt(pi++,matrix);}
  const rail=new THREE.Mesh(new THREE.BoxGeometry(.22,.16,51),edge);rail.position.set(sg*29,1.15,-3);group.add(rail);
  const rail2=rail.clone();rail2.position.y=.56;group.add(rail2);
 }posts.count=pi;posts.castShadow=true;group.add(posts);
 return {update(value,camera){group.visible=value>.01;landFar.value=camera?Math.max(85,camera.position.length()*1.35):85;landNear.value=landFar.value*(28/85);materials.forEach(m=>{m.opacity=value;m.depthWrite=!m.userData.land&&value>.98});if(camera)treeCards.forEach(card=>{card.rotation.y=Math.atan2(camera.position.x-card.position.x,camera.position.z-card.position.z);});},group};
}
