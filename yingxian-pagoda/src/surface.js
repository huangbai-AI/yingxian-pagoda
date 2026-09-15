import * as THREE from 'three';
const loader=new THREE.TextureLoader();
const texture=(name,color=false)=>{const t=loader.load('/materials/'+name);t.wrapS=t.wrapT=THREE.RepeatWrapping;t.repeat.set(.82,.82);t.flipY=false;t.colorSpace=color?THREE.SRGBColorSpace:THREE.NoColorSpace;return t;};
const color=texture('timber-color.jpg',true),normal=texture('timber-normal.jpg'),roughness=texture('timber-roughness.jpg');
export function refineSurface(mesh,renderer){
 const m=mesh.material;
 m.alphaHash=false;m.alphaToCoverage=true;m.transparent=false;m.opacity=1;
 if(/古木|浅木|暗木|朱漆/.test(m.name)){
  for(const t of [color,normal,roughness])t.anisotropy=Math.min(8,renderer.capabilities.getMaxAnisotropy());
  m.map=color;m.bumpMap=null;m.bumpScale=0;m.normalMap=normal;m.normalScale.set(.42,.42);m.roughnessMap=roughness;m.roughness=.87;m.metalness=0;
  if(/浅木/.test(m.name))m.color.setRGB(.98,.73,.45);else if(/暗木/.test(m.name))m.color.setRGB(.41,.30,.21);else if(/朱漆/.test(m.name))m.color.setRGB(.60,.31,.18);else m.color.setRGB(.78,.51,.30);
 }
 // An opaque, continuous sweep replaces stochastic transparency during isolation.
 mesh.geometry.computeBoundingBox();const box=mesh.geometry.boundingBox;
 const up=new THREE.Vector3(0,1,0).transformDirection(mesh.matrixWorld.clone().invert());
 const values=[];for(const x of [box.min.x,box.max.x])for(const y of [box.min.y,box.max.y])for(const z of [box.min.z,box.max.z])values.push(new THREE.Vector3(x,y,z).dot(up));
 const limits=new THREE.Vector2(Math.min(...values),Math.max(...values));
 m.userData.reveal={value:1};m.onBeforeCompile=shader=>{
  shader.uniforms.uTimberReveal=m.userData.reveal;shader.uniforms.uTimberUp={value:up};shader.uniforms.uTimberRange={value:limits};
  shader.vertexShader='uniform vec3 uTimberUp; varying float vTimberHeight;\n'+shader.vertexShader;
  shader.vertexShader=shader.vertexShader.replace('#include <begin_vertex>','#include <begin_vertex>\nvTimberHeight=dot(position,uTimberUp);');
  shader.fragmentShader='uniform float uTimberReveal; uniform vec2 uTimberRange; varying float vTimberHeight;\n'+shader.fragmentShader;
  shader.fragmentShader=shader.fragmentShader.replace('#include <alphatest_fragment>',`#include <alphatest_fragment>
   if(uTimberReveal<0.999){float h=(vTimberHeight-uTimberRange.x)/max(uTimberRange.y-uTimberRange.x,0.01);if(h>uTimberReveal)discard;}
  `);
 };
 m.customProgramCacheKey=()=> 'solid-timber-reveal-v5';
 const depth=new THREE.MeshDepthMaterial({depthPacking:THREE.RGBADepthPacking});depth.onBeforeCompile=m.onBeforeCompile;depth.customProgramCacheKey=()=> 'solid-timber-shadow-v5';mesh.customDepthMaterial=depth;
}
