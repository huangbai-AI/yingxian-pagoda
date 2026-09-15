import * as THREE from 'three';
import {EffectComposer} from 'three/addons/postprocessing/EffectComposer.js';
import {RenderPass} from 'three/addons/postprocessing/RenderPass.js';
import {GTAOPass} from 'three/addons/postprocessing/GTAOPass.js';
import {OutputPass} from 'three/addons/postprocessing/OutputPass.js';
import {ShaderPass} from 'three/addons/postprocessing/ShaderPass.js';
import {BokehPass} from 'three/addons/postprocessing/BokehPass.js';
import {FXAAShader} from 'three/addons/shaders/FXAAShader.js';
export function createCinema(renderer,scene,camera){
 const target=new THREE.WebGLRenderTarget(1,1,{type:THREE.HalfFloatType});
 const composer=new EffectComposer(renderer,target);composer.addPass(new RenderPass(scene,camera));
 const ao=new GTAOPass(scene,camera,1,1);ao.updateGtaoMaterial({radius:1.2,thickness:.8,distanceFallOff:.8,scale:1,samples:16});ao.updatePdMaterial({lumaPhi:10,depthPhi:2,normalPhi:3,radius:4,rings:2,samples:16});composer.addPass(ao);
 const glow=new ShaderPass({uniforms:{tDiffuse:{value:null},texel:{value:new THREE.Vector2(1,1)}},vertexShader:`varying vec2 vUv;void main(){vUv=uv;gl_Position=projectionMatrix*modelViewMatrix*vec4(position,1.);}`,fragmentShader:`uniform sampler2D tDiffuse;uniform vec2 texel;varying vec2 vUv;
 void main(){vec4 c=texture2D(tDiffuse,vUv);vec3 halo=vec3(0.);for(int i=0;i<8;i++){float a=float(i)*.785398;vec4 q=texture2D(tDiffuse,vUv+vec2(cos(a),sin(a))*texel*3.);halo+=max(q.rgb-vec3(1.1),vec3(0.))*q.a;}gl_FragColor=vec4(c.rgb+halo*.013*c.a,c.a);}`});composer.addPass(glow);
 const dof=new BokehPass(scene,camera,{focus:3.5,aperture:.001,maxblur:.0035});dof.materialBokeh.fragmentShader=dof.materialBokeh.fragmentShader.replace('gl_FragColor.a = 1.0;','');composer.addPass(dof);const focusPoint=new THREE.Vector3();
 composer.addPass(new OutputPass());const fxaa=new ShaderPass(FXAAShader);composer.addPass(fxaa);
 let width=1,height=1;
 function resize(w,h){width=w;height=h;composer.setSize(w,h);const d=renderer.getPixelRatio();ao.setSize(Math.max(1,Math.round(w*d*.65)),Math.max(1,Math.round(h*d*.65)));glow.uniforms.texel.value.set(1/(w*d),1/(h*d));fxaa.uniforms.resolution.value.set(1/(w*d),1/(h*d));}
 function render(phase,exploring){const near=Math.max(0,1-Math.abs(phase-3)),stable=exploring?1:1-THREE.MathUtils.smoothstep(Math.abs(phase-Math.round(phase)),.02,.20);ao.blendIntensity=(width<700?.28:.38)*stable;ao.enabled=stable>.001;ao.gtaoMaterial.uniforms.radius.value=THREE.MathUtils.lerp(1.5,.32,near);const focusWeight=exploring?0:1-THREE.MathUtils.smoothstep(Math.abs(phase-3),.04,.22);dof.enabled=focusWeight>.001;dof.uniforms.aperture.value=.0009*focusWeight;dof.uniforms.focus.value=-focusPoint.set(.2,43.7,11).applyMatrix4(camera.matrixWorldInverse).z;composer.render();}
 return {resize,render};
}
