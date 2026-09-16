import {NodeIO} from '@gltf-transform/core';
import {KHRMeshQuantization} from '@gltf-transform/extensions';
import {weld, prune, dedup, textureCompress, quantize} from '@gltf-transform/functions';
import sharp from 'sharp';
import {statSync} from 'node:fs';

const input = 'minitool-assets/models/yingxian.glb';
const output = 'minitool-assets/models/yingxian.glb';

const io = new NodeIO().registerExtensions([KHRMeshQuantization]);
console.log('Reading...');
const doc = await io.read(input);
const root = doc.getRoot();

// Weld
console.log('Welding...');
await doc.transform(weld({tolerance: 0.0001}));

// Quantize vertex data (no WASM needed, Three.js native support)
console.log('Quantizing geometry...');
await doc.transform(quantize({
  pattern: /^(POSITION|NORMAL|TEXCOORD_\d+)$/,
  quantizePosition: 14,
  quantizeNormal: 10,
  quantizeTexcoord: 12,
  quantizationVolume: 'scene',
}));

// Compress textures individually - color at 1024, others at 512
console.log('Resizing textures...');
const textures = root.listTextures();
for (let i = 0; i < textures.length; i++) {
  const tex = textures[i];
  const size = tex.getSize();
  // texture 0=normal, 1=color, 2=roughness based on earlier inspection
  // Keep color textures larger, compress data textures smaller
  const isColor = i === 1 || i === 4; // timber-color and wall color
  const targetSize = isColor ? 1024 : 512;
  if (size[0] > targetSize) {
    const image = await sharp(tex.getImage())
      .resize(targetSize, targetSize, {fit: 'inside'})
      .jpeg({quality: isColor ? 72 : 65})
      .toBuffer();
    tex.setImage(image);
    tex.setMimeType('image/jpeg');
    if (tex.getURI()) tex.setURI('');
    console.log(`  tex ${i}: ${size[0]} -> ${targetSize}`);
  }
}

// Cleanup
await doc.transform(dedup());
await doc.transform(prune({keepLeaves: true}));

let tris = 0;
for (const mesh of root.listMeshes()) {
  for (const prim of mesh.listPrimitives()) {
    const idx = prim.getIndices();
    if (idx) tris += idx.getCount() / 3;
  }
}

console.log('Writing...');
await io.write(output, doc);
const sizeMB = statSync(output).size / 1024 / 1024;
console.log(`Output: ${sizeMB.toFixed(2)} MB, ${Math.round(tris)} tris`);
