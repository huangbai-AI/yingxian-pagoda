import assert from 'node:assert/strict';
import fs from 'node:fs';

const asset=JSON.parse(fs.readFileSync(new URL('../minitool/original-parts.json',import.meta.url)));
const ids=new Set(asset.objects.filter(o=>o.level===3&&/斗栱/.test(o.name)).flatMap(o=>o.parts.map(p=>p[0])));
function volume(template,index){
 let sum=0;
 for(let j=0;j<index.length;j+=3){
  const [a,b,c]=index.slice(j,j+3).map(id=>template.p.slice(id*3,id*3+3).map(v=>v/10000));
  sum+=a[0]*(b[1]*c[2]-b[2]*c[1])+a[1]*(b[2]*c[0]-b[0]*c[2])+a[2]*(b[0]*c[1]-b[1]*c[0]);
 }
 return sum/6;
}
for(const id of ids){
 const t=asset.templates[id];
 assert(t.closed?.length,`构件 ${id} 缺少过渡模型`);
 const edges=new Map();
 for(let j=0;j<t.closed.length;j+=3)for(let k=0;k<3;k++){
  const a=t.closed[j+k],b=t.closed[j+(k+1)%3];
  assert(a!==b&&a>=0&&b<t.p.length/3,`构件 ${id} 顶点索引错误`);
  const key=[Math.min(a,b),Math.max(a,b)].join(',');
  const directions=edges.get(key)||[];directions.push(a<b?1:-1);edges.set(key,directions);
 }
 for(const directions of edges.values())assert(directions.length===2&&directions[0]!==directions[1],`构件 ${id} 存在开口或反面`);
 const ratio=volume(t,t.closed)/volume(t,t.i);
 assert(ratio>.97&&ratio<1.01,`构件 ${id} 简化后形体变化过大：${ratio}`);
}
console.log(`PASS：${ids.size} 个斗栱模板闭合、面方向一致，体积保留超过 97%。`);
