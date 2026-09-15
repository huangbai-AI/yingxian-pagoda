import * as THREE from 'three';

export function buildEnvironment(scene){
 const group=new THREE.Group();group.name='前庭与树影';scene.add(group);
 let seed=1056;const rand=()=>{seed=(seed*1664525+1013904223)>>>0;return seed/4294967296;};
 const materials=[];
 function material(color,extra={}){const m=new THREE.MeshStandardMaterial({color,roughness:.94,transparent:true,depthWrite:false,...extra});materials.push(m);return m;}
 const stone=material(0x101915),edge=material(0x242c24),bark=material(0x252b20),leaf=material(0x263728);
 const ground=new THREE.Mesh(new THREE.PlaneGeometry(2000,2000),material(0x0e1815));ground.rotation.x=-Math.PI/2;ground.position.y=-.19;ground.receiveShadow=true;ground.renderOrder=-2;group.add(ground);
 const slabs=new THREE.InstancedMesh(new THREE.BoxGeometry(3.4,.1,2.2),stone,2200);const matrix=new THREE.Matrix4(),quat=new THREE.Quaternion(),sc=new THREE.Vector3();let n=0;
 for(let x=-26;x<27;x++)for(let z=-18;z<22;z++){
  const xx=x*3.46+(z%2)*1.73,zz=z*2.26;if(Math.abs(xx)<18&&Math.abs(zz)<18)continue;
  matrix.compose(new THREE.Vector3(xx,-.08,zz),quat,sc.set(1,.8+rand()*.3,1));slabs.setMatrixAt(n,matrix);slabs.setColorAt(n,new THREE.Color().setRGB(.61+rand()*.18,.61+rand()*.14,.53+rand()*.16));n++;
 }slabs.count=n;slabs.receiveShadow=true;slabs.renderOrder=-1;group.add(slabs);
 const treeMap=new THREE.TextureLoader().load('/environment/pine.png');treeMap.colorSpace=THREE.SRGBColorSpace;
 const treeMat=new THREE.MeshBasicMaterial({map:treeMap,color:0x5c6355,alphaTest:.25,side:THREE.DoubleSide,transparent:true,depthWrite:false});materials.push(treeMat);
 const treeCards=[];
 for(let i=0;i<44;i++){
  const a=rand()*Math.PI*2,radius=48+rand()*43,x=Math.cos(a)*radius,z=Math.sin(a)*radius;
  if(z<5||Math.abs(x)<57)continue;
  const height=8+rand()*6;
  const card=new THREE.Mesh(new THREE.PlaneGeometry(height*.76,height),treeMat);card.position.set(x,height*.5-1.0,z);group.add(card);treeCards.push(card);
 }
 // Terrain dissolves into the photographic sky plate; its far edge is never visible.
 for(const m of [stone,ground.material]){
  m.transparent=true;m.alphaHash=false;m.depthWrite=false;
  m.onBeforeCompile=shader=>{
   shader.vertexShader='varying vec3 vLandPosition;\n'+shader.vertexShader;
   shader.vertexShader=shader.vertexShader.replace('#include <begin_vertex>',`#include <begin_vertex>
    vec4 landPosition=vec4(transformed,1.0);
    #ifdef USE_INSTANCING
    landPosition=instanceMatrix*landPosition;
    #endif
    vLandPosition=(modelMatrix*landPosition).xyz;`);
   shader.fragmentShader='varying vec3 vLandPosition;\n'+shader.fragmentShader;
   shader.fragmentShader=shader.fragmentShader.replace('#include <alphatest_fragment>',`diffuseColor.a *= 1.0-smoothstep(20.0,62.0,length(vLandPosition.xz));\n#include <alphatest_fragment>`);
  };
 }
 const posts=new THREE.InstancedMesh(new THREE.BoxGeometry(.35,1.45,.35),edge,200);let pi=0;
 for(const sg of [-1,1]){
  for(let z=-29;z<23;z+=2.8){matrix.makeTranslation(sg*29,.725,z);posts.setMatrixAt(pi++,matrix);}
  const rail=new THREE.Mesh(new THREE.BoxGeometry(.22,.16,51),edge);rail.position.set(sg*29,1.15,-3);group.add(rail);
  const rail2=rail.clone();rail2.position.y=.56;group.add(rail2);
 }posts.count=pi;posts.castShadow=true;group.add(posts);
 return {update(value,camera){group.visible=value>.01;materials.forEach(m=>m.opacity=value);if(camera)treeCards.forEach(card=>{card.rotation.y=Math.atan2(camera.position.x-card.position.x,camera.position.z-card.position.z);});},group};
}
