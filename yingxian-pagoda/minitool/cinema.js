import * as THREE from 'three';
// Mini-tool version: no post-processing (GTAO/Bokeh/FXAA disabled for mobile performance).
// Direct renderer.render() with MSAA antialiasing instead of FXAA.
export function createCinema(renderer, scene, camera){
 let width=1,height=1;
 function resize(w,h){width=w;height=h;}
 function render(phase,exploring){
  renderer.render(scene,camera);
 }
 return {resize,render};
}
