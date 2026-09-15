import './style.css';
import * as THREE from 'three';
import {GLTFLoader} from 'three/addons/loaders/GLTFLoader.js';
import {DRACOLoader} from 'three/addons/loaders/DRACOLoader.js';
import {OrbitControls} from 'three/addons/controls/OrbitControls.js';
import gsap from 'gsap';
import {ScrollTrigger} from 'gsap/ScrollTrigger';
import Lenis from 'lenis';
import {buildEnvironment} from './environment.js';
import {refineSurface} from './surface.js';
import {createCinema} from './cinema.js';
import {RoomEnvironment} from 'three/addons/environments/RoomEnvironment.js';
gsap.registerPlugin(ScrollTrigger);
history.scrollRestoration='manual';
if(!location.hash||location.hash==='#intro')window.scrollTo(0,0);
const $=s=>document.querySelector(s),$$=s=>[...document.querySelectorAll(s)],clamp=THREE.MathUtils.clamp,lerp=THREE.MathUtils.lerp;
const ease=t=>{t=clamp(t,0,1);return t*t*t*(t*(t*6-15)+10);},range=(a,b,t)=>ease((t-a)/(b-a)),mobile=()=>innerWidth<=700;
const state={phase:0,explode:0},sections=$$('.story'),panels=$$('.panel');
let reduced=matchMedia('(prefers-reduced-motion: reduce)').matches;
try{reduced=localStorage.getItem('pagoda-reduced-motion')==='true'||reduced;}catch{}
let lenis,renderer,cinema,controls,model,loaded=false,exploring=false,lastFocus,cutaway=false,hiddenRoof=false,autorotate=false,manualExplode=0,selectedFloor='all',planTop=false;
let savedScroll=0;
const arrival={light:1},loadingStarted=performance.now();
let arrivalTimeline;
let frameCount=0,frames=[],lastTime=performance.now(),viewportW=innerWidth,viewportH=innerHeight;
const levels=[],meshes=[],roofMeshes=[],stage=$('#stage'),canvas=$('#world');
const scene=new THREE.Scene(),camera=new THREE.PerspectiveCamera(34,innerWidth/innerHeight,.08,1200);
const cameraAim=new THREE.Vector3(),cameraPosition=new THREE.Vector3(),projectionPoint=new THREE.Vector3(),clipPlane=new THREE.Plane(new THREE.Vector3(0,0,-1),0);
const environment=buildEnvironment(scene);scene.fog=new THREE.FogExp2(0x122a25,.0034);
const ambient=new THREE.HemisphereLight(0xb0c9c1,0x1b2523,.38);scene.add(ambient);
const key=new THREE.DirectionalLight(0xffd39a,5.8);key.position.set(55,80,50);key.castShadow=true;key.shadow.mapSize.set(mobile()?2048:4096,mobile()?2048:4096);key.shadow.normalBias=.045;key.shadow.bias=-.00035;key.shadow.radius=4;key.shadow.blurSamples=8;key.shadow.camera.near=1;key.shadow.camera.far=220;scene.add(key,key.target);
const rim=new THREE.DirectionalLight(0xffc680,2.8);rim.position.set(36,48,-38);scene.add(rim,rim.target);
const fill=new THREE.DirectionalLight(0xb8ceca,.42);fill.position.set(-30,38,60);scene.add(fill,fill.target);
const bounce=new THREE.DirectionalLight(0xffdfb5,0);scene.add(bounce,bounce.target);
const axis=new THREE.Line(new THREE.BufferGeometry().setFromPoints([new THREE.Vector3(0,-10,0),new THREE.Vector3(0,110,0)]),new THREE.LineDashedMaterial({color:0xe0b369,dashSize:1.2,gapSize:.8,transparent:true,opacity:0,depthTest:false}));axis.computeLineDistances();axis.renderOrder=20;scene.add(axis);
const rings=new THREE.Group();scene.add(rings);
for(let i=2;i<=4;i++){const pts=[];for(let k=0;k<=8;k++){const a=k*Math.PI/4;pts.push(new THREE.Vector3(Math.cos(a)*(13.1-(i-2)*.7),0,Math.sin(a)*(13.1-(i-2)*.7)));}const r=new THREE.Line(new THREE.BufferGeometry().setFromPoints(pts),new THREE.LineBasicMaterial({color:0xcaa46c,transparent:true,opacity:0}));r.userData.floor=i;rings.add(r);}
function setupMotion(){lenis?.destroy();lenis=null;document.body.classList.toggle('reduced-motion',reduced);$('#motion-toggle').setAttribute('aria-pressed',String(reduced));$('#motion-toggle').textContent=reduced?'恢复动态效果':'减少动态效果';if(!reduced){lenis=new Lenis({duration:1.05,smoothWheel:true,anchors:true});lenis.on('scroll',ScrollTrigger.update);}}
setupMotion();gsap.ticker.add(t=>lenis?.raf(t*1000));gsap.ticker.lagSmoothing(0);
$('#motion-toggle').onclick=()=>{reduced=!reduced;try{localStorage.setItem('pagoda-reduced-motion',String(reduced));}catch{}setupMotion();buildStory();};
function failure(error){console.error('模型加载失败',error);document.body.classList.remove('loading');lenis?.start();$('#model-loading').hidden=true;$('#model-error').hidden=false;}
$('#retry').onclick=()=>location.reload();document.body.classList.add('loading');lenis?.stop();
try{
 renderer=new THREE.WebGLRenderer({canvas,alpha:true,antialias:true,powerPreference:'high-performance'});renderer.setPixelRatio(Math.min(devicePixelRatio,mobile()?1.35:1.65));renderer.outputColorSpace=THREE.SRGBColorSpace;renderer.toneMapping=THREE.ACESFilmicToneMapping;renderer.toneMappingExposure=1.25;renderer.setClearColor(0x10201e,0);renderer.shadowMap.enabled=true;renderer.shadowMap.type=THREE.VSMShadowMap;renderer.localClippingEnabled=true;renderer.info.autoReset=false;
 const room=new RoomEnvironment();const pmrem=new THREE.PMREMGenerator(renderer);scene.environment=pmrem.fromScene(room,.04).texture;scene.environmentIntensity=.22;room.dispose();pmrem.dispose();
 cinema=createCinema(renderer,scene,camera);
 controls=new OrbitControls(camera,canvas);controls.enabled=false;controls.enableDamping=true;controls.dampingFactor=.075;controls.minDistance=3;controls.maxDistance=400;controls.maxPolarAngle=Math.PI*.8;canvas.tabIndex=0;
 controls.addEventListener('start',()=>{if(exploring){autorotate=false;$('#auto-toggle').setAttribute('aria-pressed','false');}});
 new ResizeObserver(()=>{viewportW=stage.clientWidth;viewportH=stage.clientHeight;renderer.setSize(viewportW,viewportH,false);cinema.resize(viewportW,viewportH);camera.aspect=viewportW/viewportH;camera.updateProjectionMatrix();}).observe(stage);
 new GLTFLoader().setDRACOLoader(new DRACOLoader().setDecoderPath('/draco/').setWorkerLimit(2)).load('/models/yingxian.glb?v=17',g=>{
  model=g.scene;model.name='应县木塔';scene.add(model);model.updateMatrixWorld(true);
  model.traverse(o=>{
   if(/^Level_\d+$/.test(o.name)){o.userData.index=Number(o.name.split('_')[1]);o.userData.baseY=o.position.y;levels.push(o);}
   if(!o.isMesh)return;meshes.push(o);o.castShadow=true;o.receiveShadow=true;o.material=o.material.clone();const m=o.material;m.alphaHash=true;m.roughness=.81;m.clippingPlanes=[];
   if(m.map){m.map.anisotropy=Math.min(8,renderer.capabilities.getMaxAnisotropy());m.bumpMap=m.map;m.bumpScale=.002;if(/朱漆/.test(m.name))m.color.setRGB(.72,.55,.40);else if(/暗木/.test(m.name))m.color.setRGB(.54,.52,.45);else if(/浅木/.test(m.name))m.color.setRGB(.96,.85,.67);else m.color.setRGB(.80,.73,.61);}
   if(/青灰瓦|瓦脊/.test(m.name))m.color.setRGB(.085,.092,.095);if(/石台/.test(m.name))m.color.setRGB(.12,.14,.13);
   refineSurface(o,renderer);
   o.userData.roof=/筒瓦|屋面|垂脊|檐口|椽子|脊饰|风铎|攒尖|塔刹|相轮|宝瓶|刹尖|刹链|瓦当|望板|屋架/.test(o.name);o.userData.stair=/木楼梯/.test(o.name);o.userData.enclosure=/隔扇|匾额/.test(o.name);o.userData.transition=/层间承|层间拉结/.test(o.name);if(o.userData.roof)roofMeshes.push(o);
  });
  loaded=true;$('#load-percent').textContent='100%';$('#load-bar').style.width='100%';startArrival();
  $('#stage').setAttribute('aria-label','应县木塔三维模型已载入。可跟随滚动看斜向拆层、柱网、斗栱与飞檐，或进入自由观塔。');
  window.__pagoda={loaded:true,levels:levels.length,meshes:meshes.length,stats:()=>({lighting:{key:key.intensity,fill:fill.intensity,ambient:ambient.intensity},stochasticMaterials:meshes.filter(m=>m.material.alphaHash).length,timberNormalMaps:meshes.filter(m=>m.material.normalMap).length,triangles:renderer.info.render.triangles,calls:renderer.info.render.calls,frameMs:frames.reduce((a,b)=>a+b,0)/(frames.length||1),phase:state.phase,exploring,explode:state.explode,hiddenRoof,cutaway,floor:selectedFloor,fov:camera.fov,camera:camera.position.toArray(),target:controls.target.toArray(),levelOffsets:levels.map(l=>({level:l.userData.index,y:l.position.y})),connected:state.explode<.001&&roofMeshes.every(m=>Math.abs(m.position.y)<.001)})};
 },p=>{const pct=p.total?Math.round(p.loaded/p.total*99):Math.min(95,Math.round(p.loaded/100000));$('#load-percent').textContent=pct+'%';$('#load-bar').style.width=pct+'%';},failure);
}catch(e){failure(e);}
async function startArrival(){
 // 等字体和第一帧就绪，避免退场后突然出现空塔或换字。
 await Promise.race([document.fonts.ready,new Promise(r=>setTimeout(r,1800))]);
 await new Promise(r=>setTimeout(r,Math.max(0,(reduced?0:1500)-(performance.now()-loadingStarted))));
 await new Promise(r=>requestAnimationFrame(()=>requestAnimationFrame(r)));
 const hero=(!location.hash||location.hash==='#intro')&&scrollY<innerHeight*.35;
 const text=$$('.hero h1 span'),details=$$('.hero-meta,.hero-note,.scroll-cue');
 const finish=()=>{arrival.light=1;$('#arrival-shade').style.opacity=0;$('#model-loading').hidden=true;document.body.classList.remove('loading');lenis?.start();gsap.set([...text,...details],{clearProps:'opacity,visibility,transform,filter'});};
 if(reduced){finish();return;}
 if(hero){arrival.light=.24;gsap.set('#arrival-shade',{opacity:1});gsap.set(text,{autoAlpha:0,y:26,filter:'blur(7px)'});gsap.set(details,{autoAlpha:0,y:12});}
 // Freeze every tier on the same frame; keep SVG transforms in the browser's coordinate system.
 const tiers=$$('.loading-tower g');
 tiers.forEach(el=>el.getAnimations().forEach(animation=>animation.pause()));
 const tierFrames=tiers.map(el=>{const style=getComputedStyle(el);return {transform:style.transform,opacity:style.opacity};});
 tiers.forEach((el,i)=>{el.getAnimations().forEach(animation=>animation.cancel());el.style.animation='none';el.animate([tierFrames[i],{transform:'translateY(0px)',opacity:1}],{duration:280,easing:'ease-out',fill:'forwards'});});
 arrivalTimeline=gsap.timeline({onComplete:finish});
 arrivalTimeline.to('#model-loading',{opacity:0,duration:.7,ease:'power2.inOut',onStart:()=>document.body.classList.remove('loading'),onComplete:()=>$('#model-loading').hidden=true},.28);
 if(hero){arrivalTimeline.to(arrival,{light:1,duration:2.4,ease:'power2.inOut'},.35)
 .to('#arrival-shade',{opacity:0,duration:2.4,ease:'power2.inOut'},.35)
 .to(text,{autoAlpha:1,y:0,filter:'blur(0px)',duration:1.35,stagger:.24,ease:'power3.out'},.85)
 .to(details,{autoAlpha:1,y:0,duration:1,stagger:.10,ease:'power2.out'},1.7);}
}
let timeline;
function buildStory(){timeline?.scrollTrigger?.kill();timeline?.kill();timeline=gsap.fromTo(state,{phase:0},{phase:5,ease:'none',scrollTrigger:{trigger:'#intro',start:'top top',endTrigger:'#guard',end:'top top',scrub:reduced?true:.65,invalidateOnRefresh:true}});}
buildStory();window.addEventListener('resize',()=>{buildStory();ScrollTrigger.refresh();});document.fonts.ready.then(()=>ScrollTrigger.refresh());
// All six poses track the same third-floor corner. No replacement model is used for close views.
const poses=[
 {pos:[18,18,60],aim:[0,29,0],fov:64,shift:0,roll:0,explode:0,isolate:0,roof:0,env:1},
 {pos:[29,59,49],aim:[0,44,0],shift:-.13,roll:-.43,explode:1,isolate:0,roof:0,env:0},
 {pos:[17,54,29],aim:[0,41.5,0],fov:36,shift:-.15,roll:-.06,explode:1,isolate:1,roof:1,env:0},
 {pos:[3.6,43.25,13.9],aim:[.2,43.7,11],fov:42,shift:.14,roll:0,explode:1,isolate:1,roof:0,env:0},
 {pos:[9,33,24],aim:[.5,36,8],fov:40,shift:.04,roll:.08,explode:0,isolate:0,roof:0,env:0},
 {pos:[43,28,126],aim:[0,31.5,0],shift:-.14,roll:0,explode:0,isolate:0,roof:0,env:1}
];
for(const pose of poses)pose.fov??=34;
const sample={pos:new THREE.Vector3(),aim:new THREE.Vector3()};
function sampleStory(raw){const a=Math.min(4,Math.floor(raw)),b=a+1,t=ease(clamp((raw-a-.08)/.84,0,1)),pa=poses[a],pb=poses[b];sample.pos.fromArray(pa.pos).lerp(cameraPosition.fromArray(pb.pos),t);sample.aim.fromArray(pa.aim).lerp(cameraAim.fromArray(pb.aim),t);for(const k of ['fov','shift','roll','explode','isolate','roof','env'])sample[k]=lerp(pa[k],pb[k],t);return sample;}
const offsetFor=(i,amount)=>i===0?0:(Math.min(i,5)-2)*8*amount;
function floorIndex(mesh){let o=mesh;while(o&&!/^Level_\d+$/.test(o.name))o=o.parent;return o?.userData.index??0;}
function updateAssembly(s,phase){
 const chosen=exploring&&selectedFloor!=='all'?Number(selectedFloor):null;
 levels.forEach(l=>{const i=l.userData.index;l.position.y=l.userData.baseY+offsetFor(i,state.explode);l.visible=chosen===null||chosen===i||(chosen===5&&i===6);});
 meshes.forEach(m=>{
  const i=m.userData.floorIndex??(m.userData.floorIndex=floorIndex(m));let opacity=1,lift=0;
  if(!exploring){if(i!==3)opacity*=1-s.isolate;if(i===0||i===1||i>=5)opacity*=1-range(.20,.83,phase)*(1-range(3.45,4.05,phase));if(i===3&&m.userData.roof){lift=9*s.roof;opacity*=1-s.roof;}if(i===3&&m.userData.enclosure)opacity*=1-s.roof;if(i===3&&/匾额/.test(m.name))opacity*=1-range(2.25,2.8,phase)*(1-range(3.15,3.65,phase));if(m.userData.transition)opacity*=1-Math.max(s.isolate,state.explode);}
  if(m.userData.stair)opacity*=1-Math.max(state.explode,exploring?0:s.isolate);if(exploring&&hiddenRoof&&m.userData.roof)opacity=0;m.position.y=lift;m.material.opacity=1;m.material.userData.reveal.value=opacity;m.visible=opacity>.015;
 });
 const axes=exploring?state.explode*.45:range(.45,.92,phase)*(1-range(1.2,1.85,phase));axis.material.opacity=axes*.85;axis.visible=axes>.01;
 rings.children.forEach(r=>{const i=r.userData.floor;r.position.y=[0,0,21.2,30.5,39.6][i]+offsetFor(i,state.explode);r.material.opacity=axes*.36;r.visible=axes>.01;});
}
function setCamera(s){
 camera.fov=s.fov;let shift=s.shift,shiftY=0;cameraPosition.copy(s.pos);cameraAim.copy(s.aim);
 if(mobile()){
  const factors=[1.25,1.55,2.55,1.45,1.30,1.65],xs=[0,-.12,.02,.11,.16,-.25],ys=[.07,-.11,-.10,.05,-.07,-.04];const a=Math.min(4,Math.floor(state.phase)),t=ease(clamp((state.phase-a-.08)/.84,0,1)),b=a+1;cameraPosition.sub(cameraAim).multiplyScalar(lerp(factors[a],factors[b],t)).add(cameraAim);shift=lerp(xs[a],xs[b],t);shiftY=lerp(ys[a],ys[b],t);
 }
 if(planTop&&state.phase>1.85&&state.phase<2.3){cameraPosition.lerp(new THREE.Vector3(0,93,.15),.9);cameraAim.set(0,38.5,0);}
 camera.position.copy(cameraPosition);camera.up.set(Math.sin(s.roll),Math.cos(s.roll),0);camera.lookAt(cameraAim);controls.target.copy(cameraAim);camera.setViewOffset(viewportW,viewportH,-shift*viewportW,-shiftY*viewportH,viewportW,viewportH);
}
function setLabels(phase){
 const hotspot=$('#column-hotspot'),show=!exploring&&phase>1.86&&phase<2.25;hotspot.hidden=!show;const levelOffset=offsetFor(3,state.explode);
 function project(x,y,z){projectionPoint.set(x,y+levelOffset,z).project(camera);return {x:(projectionPoint.x+1)*.5*viewportW,y:(1-projectionPoint.y)*.5*viewportH};}
 if(show){const p=project(.15,36.05,11.05);hotspot.style.left=p.x+'px';hotspot.style.top=p.y+'px';}
 const amount=exploring?0:range(2.68,2.96,phase)*(1-range(3.05,3.36,phase));
 const svg=$('#label-lines');svg.style.opacity=amount;svg.setAttribute('viewBox',`0 0 ${viewportW} ${viewportH}`);
 const paths=[];
 [['#label-dou',.20,36.36,11.5],['#label-gong',.64,35.99,11.65],['#label-ang',.72,35.59,12.19]].forEach(([id,x,y,z],i)=>{
  const el=$(id),p=project(x,y,z),lx=viewportW*(mobile()?.08:.12),ly=viewportH*(mobile()?[.48,.59,.70][i]:[.53,.64,.75][i]);el.style.opacity=amount;el.style.left=lx+'px';el.style.top=ly+'px';
  paths.push(`<path d="M${p.x} ${p.y} L${lx+80} ${ly} H${lx+38}"/><circle cx="${p.x}" cy="${p.y}" r="2"/>`);
 });svg.innerHTML=paths.join('');

}
function updateText(){
 const raw=state.phase,index=clamp(Math.round(raw),0,5),footer=clamp(($('#about').getBoundingClientRect().top/innerHeight-.25)/.65,0,1);
 panels.forEach((p,i)=>{const opacity=(1-range(.12,.49,Math.abs(raw-i)))*footer,show=opacity>.01;p.style.opacity=opacity;p.style.visibility=show?'visible':'hidden';p.style.transform=`translateY(${(raw-i)*-16}px)`;p.inert=!show;p.setAttribute('aria-hidden',String(!show));});
 $$('.site-header nav a').forEach((a,i)=>{a.classList.toggle('active',i===index);if(i===index)a.setAttribute('aria-current','step');else a.removeAttribute('aria-current');});$$('.chapter-rail a').forEach((a,i)=>a.classList.toggle('active',i===index));$('#chapter-number').textContent=String(index+1).padStart(2,'0');$('#chapter-name').textContent=sections[index].dataset.chapter;$('.chapter-status').style.opacity=footer;$('#reading-progress').style.width=`${clamp(scrollY/(document.documentElement.scrollHeight-innerHeight),0,1)*100}%`;
}
function updateAtmosphere(phase){
 const a=Math.min(4,Math.floor(phase)),t=ease(clamp((phase-a-.08)/.84,0,1));
 const anchors=[[52,60,0,0],[44,38,.40,-7],[43,46,.35,5],[65,36,.22,9],[68,45,.32,-3],[38,67,.12,0]];
 const values=anchors[a].map((v,i)=>lerp(v,anchors[a+1][i],t));const style=document.documentElement.style;
 const backgroundLight=[1,.75,.90,.88,1.08,1];// 淡纹理只出现在中间四幕，首尾自然退净。
 style.setProperty('--interior-texture',range(.15,.85,phase)*(1-range(4.15,4.85,phase)));
 style.setProperty('--backdrop-light',lerp(backgroundLight[a],backgroundLight[a+1],t));style.setProperty('--haze-x',values[0]+'%');style.setProperty('--haze-y',values[1]+'%');style.setProperty('--chamber',values[2]);style.setProperty('--haze-angle',values[3]+'deg');style.setProperty('--haze-pan',((phase-2.5)*-2.8)+'%');
}
function updateLight(phase){
 const intro=1-range(.08,.85,phase), close=range(2.2,2.92,phase)*(1-range(3.05,3.8,phase));
 const interior=range(.15,.85,phase)*(1-range(4.15,4.85,phase));
 const size=lerp(lerp(62,18,1-range(.08,.6,Math.abs(phase-2))),8,close), y=lerp(35,35.8+offsetFor(3,state.explode),close), z=lerp(0,11.5,close);
 // 与离线近景保持同侧主光，弱冷补光托住檐下的木构细节。
 key.target.position.set(0,y,z);
 key.position.set(lerp(lerp(52,8,close),58,intro),y+lerp(lerp(29,4,close),23,intro),z+lerp(lerp(12,7,close),2,intro));
 key.intensity=lerp(lerp(6.4,4.9,interior),7.2,intro);key.color.setHex(0xffd1a0).lerp(new THREE.Color(0xffdfbd),interior*.7);
 scene.environmentIntensity=lerp(.13,.16,interior);
 key.shadow.camera.left=-size;key.shadow.camera.right=size;key.shadow.camera.top=size;key.shadow.camera.bottom=-size;key.shadow.camera.updateProjectionMatrix();
 key.shadow.normalBias=lerp(.05,.012,close);key.shadow.bias=lerp(-.00012,-.00004,close);key.shadow.radius=lerp(4,7,close);
 ambient.intensity=lerp(.18,.26,interior);fill.intensity=lerp(.24,.42,interior)+close*.10;
 fill.position.set(lerp(-30,-7,close),lerp(38,y+1,close),lerp(60,z+8,close));fill.target.position.set(0,y,z);
 rim.intensity=lerp(.38,.28,interior);rim.target.position.set(0,y,z);
 key.intensity*=arrival.light;fill.intensity*=lerp(.5,1,arrival.light);rim.intensity*=lerp(.4,1,arrival.light);
 bounce.intensity=close*.25;bounce.position.set(-8,y-1,z+6);bounce.target.position.set(0,y,z);
}

function render(now){requestAnimationFrame(render);if(!renderer||document.hidden)return;const dt=Math.min((now-lastTime)/1000,.1);lastTime=now;
 if(loaded){const s=sampleStory(reduced?Math.round(state.phase):state.phase);if(exploring){state.explode=THREE.MathUtils.damp(state.explode,manualExplode,7,dt);if(Math.abs(state.explode-manualExplode)<.001)state.explode=manualExplode;if(autorotate&&!reduced){const rel=camera.position.clone().sub(controls.target);rel.applyAxisAngle(new THREE.Vector3(0,1,0),dt*.10);camera.position.copy(controls.target).add(rel);}controls.update();environment.update(.15,camera);scene.fog.density=.0018;}else{state.explode=s.explode;setCamera(s);environment.update(s.env,camera);scene.fog.density=lerp(.0014,.0021,s.env);document.documentElement.style.setProperty('--environment',s.env);document.documentElement.style.setProperty('--intro-env',state.phase<2?s.env:0);document.documentElement.style.setProperty('--guard-env',state.phase>3?s.env:0);document.documentElement.style.setProperty('--forest-y',`${Math.min(state.phase,1)*120}px`);document.documentElement.style.setProperty('--mist-y',`${Math.sin(state.phase)*35}px`);updateAtmosphere(state.phase);updateText();}updateAssembly(s,state.phase);model.updateMatrixWorld(true);camera.updateMatrixWorld();setLabels(state.phase);updateLight(exploring?0:state.phase);}
 renderer.info.reset();cinema.render(state.phase,exploring);if(frameCount++%8===0&&dt>0&&dt<.09){frames.push(dt*1000);if(frames.length>100)frames.shift();}
}
requestAnimationFrame(render);document.addEventListener('visibilitychange',()=>lastTime=performance.now());
function goTo(id){const el=$(id);if(lenis)lenis.scrollTo(el,{duration:reduced?0:1.5});else el.scrollIntoView({behavior:reduced?'instant':'smooth'});}
$('#column-hotspot').onclick=$('#plan-close').onclick=()=>goTo('#craft');$('#plan-angle').onclick=()=>{planTop=!planTop;$('#plan-angle').textContent=planTop?'斜俯看':'俯看';$('#plan-angle').setAttribute('aria-pressed',String(planTop));};
function applyClipping(){meshes.forEach(m=>{m.material.clippingPlanes=cutaway?[clipPlane]:[];m.material.side=cutaway?THREE.DoubleSide:THREE.FrontSide;m.material.needsUpdate=true;});}
function setPressed(id,on){$(id).setAttribute('aria-pressed',String(on));}
function resetTools(){hiddenRoof=false;cutaway=false;autorotate=false;selectedFloor='all';manualExplode=0;$('#explode').value=0;$('#explode-value').textContent='0%';$('#floor-select').value='all';['#roof-toggle','#cut-toggle','#auto-toggle'].forEach(id=>setPressed(id,false));applyClipping();}
function poseView(view='overall',animate=true){
 if(!loaded)return;$$('[data-view]').forEach(b=>b.classList.toggle('active',b.dataset.view===view));const floor=selectedFloor==='all'?null:Number(selectedFloor),fy=[2,12,25,34,43,52,62][floor??0]+offsetFor(floor??2,manualExplode);let aim=new THREE.Vector3(0,floor===null?32:fy,0),pos=new THREE.Vector3(65,60,145);
 if(view==='front')pos.set(0,aim.y+8,150);if(view==='top')pos.set(0,160,.2);if(view==='detail'){aim.set(.2,36,11);pos.set(9,38,27);}if(floor!==null&&view!=='top'&&view!=='detail')pos.set(24,fy+15,45);if(floor===null&&manualExplode>0&&view!=='detail'){aim.y+=manualExplode*10;pos.y+=manualExplode*10;pos.sub(aim).multiplyScalar(1+manualExplode*.24).add(aim);}
 let shift=.11,shiftY=0;if(mobile()){pos.sub(aim).multiplyScalar(view==='detail'?1.4:1.75).add(aim);shift=0;shiftY=-.18;}camera.up.set(0,1,0);camera.setViewOffset(viewportW,viewportH,-shift*viewportW,-shiftY*viewportH,viewportW,viewportH);
 camera.fov=34;camera.updateProjectionMatrix();const duration=animate&&!reduced?.85:0;gsap.to(camera.position,{x:pos.x,y:pos.y,z:pos.z,duration,ease:'power2.inOut',overwrite:true});gsap.to(controls.target,{x:aim.x,y:aim.y,z:aim.z,duration,ease:'power2.inOut',overwrite:true});$('#view-caption').textContent=({overall:'完整形制 · 五层六檐',front:'立面观察 · 檐与柱',top:'八角平面 · 内外相依',detail:'塔上斗栱 · 层层承托'})[view];
}
function openExplorer(mode='overall'){if(!loaded)return;if($('#info-dialog').open)$('#info-dialog').close();lastFocus=document.activeElement;savedScroll=scrollY;exploring=true;lenis?.stop();document.body.style.overflow='hidden';document.body.classList.add('is-exploring');$('#explorer-ui').hidden=false;$('main').inert=true;$('.site-header').inert=true;$('.chapter-rail').inert=true;controls.enabled=true;resetTools();if(mode==='structure'){manualExplode=.8;$('#explode').value=80;$('#explode-value').textContent='80%';poseView('overall',false);}else poseView(mode,false);$('#close-explorer').focus();}
function closeExplorer(){if(!exploring)return;exploring=false;controls.enabled=false;resetTools();gsap.killTweensOf(camera.position);gsap.killTweensOf(controls.target);document.body.classList.remove('is-exploring');document.body.style.overflow='';window.scrollTo(0,savedScroll);$('#explorer-ui').hidden=true;$('main').inert=false;$('.site-header').inert=false;$('.chapter-rail').inert=false;lenis?.start();lastFocus?.focus({preventScroll:true});}
['#open-explorer','#explore-end','#explore-footer'].forEach(id=>$(id).onclick=()=>openExplorer());$('#inspect-structure').onclick=()=>openExplorer('structure');$('#close-explorer').onclick=closeExplorer;$$('[data-view]').forEach(b=>b.onclick=()=>poseView(b.dataset.view));
$('#explode').oninput=e=>{manualExplode=Number(e.target.value)/100;$('#explode-value').textContent=e.target.value+'%';if(selectedFloor==='all')poseView();};$('#roof-toggle').onclick=()=>{hiddenRoof=!hiddenRoof;setPressed('#roof-toggle',hiddenRoof);};$('#cut-toggle').onclick=()=>{cutaway=!cutaway;setPressed('#cut-toggle',cutaway);applyClipping();};$('#auto-toggle').onclick=()=>{autorotate=!autorotate;setPressed('#auto-toggle',autorotate);};$('#floor-select').onchange=e=>{selectedFloor=e.target.value;poseView();};$('#reset-view').onclick=()=>{resetTools();poseView();};
const info=$('#info-dialog');$('#detail-dougong').onclick=()=>{info.showModal();lenis?.stop();};$('#close-info').onclick=()=>info.close();info.addEventListener('close',()=>{if(!exploring)lenis?.start();});info.addEventListener('click',e=>{if(e.target===info){const r=info.getBoundingClientRect();if(e.clientX<r.left||e.clientX>r.right||e.clientY<r.top||e.clientY>r.bottom)info.close();}});$('#info-explore').onclick=()=>openExplorer('detail');
document.addEventListener('keydown',e=>{if(!exploring)return;if(e.key==='Escape'){closeExplorer();return;}if(e.key==='Tab'){const targets=[canvas,...$$('#explorer-ui button,#explorer-ui input,#explorer-ui select')],first=targets[0],last=targets.at(-1);if(e.shiftKey&&document.activeElement===first){e.preventDefault();last.focus();}else if(!e.shiftKey&&document.activeElement===last){e.preventDefault();first.focus();}return;}if(document.activeElement!==canvas)return;const rel=camera.position.clone().sub(controls.target);if(e.key==='ArrowLeft'||e.key==='ArrowRight'){e.preventDefault();rel.applyAxisAngle(new THREE.Vector3(0,1,0),e.key==='ArrowLeft'?.1:-.1);camera.position.copy(controls.target).add(rel);}if(['+','=','-'].includes(e.key)){e.preventDefault();rel.multiplyScalar(e.key==='-'?1.1:.9);camera.position.copy(controls.target).add(rel);}});
