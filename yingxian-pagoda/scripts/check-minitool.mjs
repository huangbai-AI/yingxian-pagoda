import fs from 'node:fs';
import path from 'node:path';
const root=path.resolve('minitool-dist');
const files=[];function walk(dir){for(const f of fs.readdirSync(dir)){const p=path.join(dir,f);if(fs.statSync(p).isDirectory())walk(p);else files.push(p);}}walk(root);
const allowed=/\.(html|css|js|png|jpe?g|gif|webp|svg|woff2?|json)$/;
const errors=[];
for(const f of files)if(!allowed.test(f)||/\.DS_Store|\.map$/.test(f))errors.push('不支持的文件：'+f);
const html=fs.readFileSync(path.join(root,'index.html'),'utf8');
if(files.filter(f=>f.endsWith('.html')).length!==1)errors.push('入口必须唯一');
if(/type=["']module|\bon\w+\s*=|<iframe|<object|<base|javascript:|target=["']_blank|\bdownload[=>\s]/i.test(html))errors.push('HTML 含禁止能力');
for(const m of html.matchAll(/<script\b([^>]*)>([\s\S]*?)<\/script>/g))if(!/\bsrc=/.test(m[1])||m[2].trim())errors.push('存在内联脚本');
for(const f of files.filter(f=>/\.(html|css)$/.test(f))){const text=fs.readFileSync(f,'utf8');for(const m of text.matchAll(/(?:src|href)=["']([^"']+)["']|url\(["']?([^\s"')]+)["']?\)/g)){const ref=m[1]||m[2];if(ref.startsWith('#')||ref.startsWith('%23')||ref.startsWith('data:'))continue;if(/^(https?:|\/)/.test(ref))errors.push('外部或绝对路径：'+ref);else if(!fs.existsSync(path.resolve(path.dirname(f),ref.split('?')[0])))errors.push('缺少资源：'+ref);}}
const forbidden=/\bfetch\s*\(|XMLHttpRequest|WebAssembly|\bnew\s+(?:Worker|SharedWorker|WebSocket|EventSource|RTCPeerConnection|Function)\s*\(|\beval\s*\(|navigator\.(?:clipboard|geolocation|bluetooth|usb|hid|serial|connection|credentials|locks)|window\.(?:open|prompt)\s*\(/;
for(const f of files.filter(f=>f.endsWith('.js')))if(forbidden.test(fs.readFileSync(f,'utf8')))errors.push('脚本含禁止能力：'+path.basename(f));
if(errors.length){console.error(errors.join('\n'));process.exitCode=1;}else console.log('PASS：唯一入口、文件类型、包内路径、经典外置脚本、禁止能力扫描。');
