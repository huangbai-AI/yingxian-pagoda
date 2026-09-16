// Post-build fixer for the mini-tool bundle.
// Vite emits index.html into minitool-dist/minitool/ with module scripts and ../ paths.
// The mini-tool container requires: index.html at zip root, classic (non-module) external
// scripts, relative ./ paths, and defer so the DOM is ready before execution.
import {readFileSync, writeFileSync, existsSync, rmSync, readdirSync, statSync} from 'fs';
import {dirname, join} from 'path';
import {fileURLToPath} from 'url';

const root = dirname(dirname(fileURLToPath(import.meta.url)));
const dist = join(root, 'minitool-dist');
const nested = join(dist, 'minitool', 'index.html');
const target = join(dist, 'index.html');

let htmlPath = existsSync(target) ? target : nested;
let html = readFileSync(htmlPath, 'utf8');

// 1) Classic deferred script instead of <script type="module" crossorigin src="../app.js">
html = html.replace(
  /<script[^>]*src="(?:\.\.\/)?app\.js"[^>]*>\s*<\/script>/,
  '<script defer src="./model-data.js"></script><script defer src="./app.js"></script>'
);
// 2) Stylesheet: relative path, no crossorigin
html = html.replace(
  /<link([^>]*?)href="(?:\.\.\/)?style\.css"([^>]*)>/g,
  (match, pre, post) => `<link rel="stylesheet" href="./style.css">`
);

html=html.replace('./environment/fallback.jpg','./posters/chapter-0.webp');
writeFileSync(target, html);
// A small shared-part scene description, independently readable and auditable.
// No loader, binary wrapper, Base64 or runtime decompressor is used.
writeFileSync(join(dist,'model-data.js'),'window.PagodaOriginalParts='+readFileSync(join(root,'minitool','original-parts.json'),'utf8')+';\n');

// Chrome 61 does not understand four/eight-digit hex colors. Convert the final
// stylesheet so the compatibility check applies to the actual upload artifact.
const cssPath = join(dist, 'style.css');
if (existsSync(cssPath)) {
  let css = readFileSync(cssPath, 'utf8');
  css = css.replace(/#([0-9a-f]{8})(?![0-9a-f])/gi, (_match, value) => {
    const r = parseInt(value.slice(0, 2), 16);
    const g = parseInt(value.slice(2, 4), 16);
    const b = parseInt(value.slice(4, 6), 16);
    const a = Math.round((parseInt(value.slice(6, 8), 16) / 255) * 1000) / 1000;
    return `rgba(${r},${g},${b},${a})`;
  });
  css = css.replace(/#([0-9a-f]{4})(?![0-9a-f])/gi, (_match, value) => {
    const r = parseInt(value[0] + value[0], 16);
    const g = parseInt(value[1] + value[1], 16);
    const b = parseInt(value[2] + value[2], 16);
    const a = Math.round((parseInt(value[3] + value[3], 16) / 255) * 1000) / 1000;
    return `rgba(${r},${g},${b},${a})`;
  });
  writeFileSync(cssPath, css);
}

// 3) Remove the now-empty nested minitool directory if Vite created it
if (existsSync(join(dist, 'minitool'))) {
  rmSync(join(dist, 'minitool'), {recursive: true, force: true});
}

// 4) Remove any empty material/draco dirs that the public asset folder may carry
for (const d of ['materials', 'draco', 'models']) {
  const p = join(dist, d);
  if (existsSync(p)) rmSync(p, {recursive: true, force: true});
}
rmSync(join(dist,'environment','fallback.jpg'),{force:true});

const allowed = new Set(['.html', '.css', '.js', '.png', '.jpg', '.jpeg', '.gif', '.webp', '.svg', '.woff', '.woff2', '.json']);
function verifyFiles(directory) {
  for (const name of readdirSync(directory)) {
    const path = join(directory, name);
    if (statSync(path).isDirectory()) verifyFiles(path);
    else {
      const dot = name.lastIndexOf('.');
      const extension = dot >= 0 ? name.slice(dot).toLowerCase() : '';
      if (!allowed.has(extension)) throw new Error(`Unsupported mini-tool artifact: ${path}`);
    }
  }
}
verifyFiles(dist);

console.log('[postbuild] index normalized, legacy colors converted, unsupported artifact types rejected.');
