import fs from 'node:fs';
import {MeshoptSimplifier} from 'meshoptimizer';
await MeshoptSimplifier.ready;
const asset=JSON.parse(fs.readFileSync('scripts/mobile-parts-raw.json','utf8'));
const closedTemplates=new Set(asset.objects.filter(o=>o.level===3&&/斗栱/.test(o.name)).flatMap(o=>o.parts.map(p=>p[0])));
const roofTemplates=new Set(asset.objects.filter(o=>o.level===3&&/屋面|望板/.test(o.name)).flatMap(o=>o.parts.map(p=>p[0])));
// Offline-only simplifier. The application receives no WASM, decoder or loader.
for(const [id,t] of asset.templates.entries()){
 const positions=Float32Array.from(t.p,v=>v/10000),index=Uint32Array.from(t.i);
 const target=Math.min(index.length,Math.max(24,Math.floor(index.length*.18/3)*3));
 t.low=Array.from(t.p.length<=24?index:MeshoptSimplifier.simplify(index,positions,3,target,.22)[0]);
 t.medium=Array.from(MeshoptSimplifier.simplify(index,positions,3,Math.min(index.length,Math.max(24,Math.floor(index.length*.55/3)*3)),.018)[0]);
 // Keep the bracket silhouette and all sides intact as the camera pulls back.
 if(closedTemplates.has(id))t.closed=Array.from(t.p.length<=72?index:MeshoptSimplifier.simplify(index,positions,3,Math.min(index.length,Math.max(24,Math.floor(index.length*.35/3)*3)),.035)[0]);
 if(roofTemplates.has(id))t.returnRoof=Array.from(MeshoptSimplifier.simplify(index,positions,3,Math.min(index.length,Math.max(24,Math.floor(index.length*.4/3)*3)),.025)[0]);
}
fs.writeFileSync('minitool/original-parts.json',JSON.stringify(asset));
console.log('Shared original asset:',fs.statSync('minitool/original-parts.json').size,'bytes');
